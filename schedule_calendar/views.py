import calendar
import os
from datetime import datetime, date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django.views import generic
from dotenv import load_dotenv

from .email_handling import EmailHandler
from .forms import EventForm, UserForm, ProfileForm, InviteParticipantForm, AddressForm, CheckIfUserExists
from .models import Event, Address, Participant, Profile
from .utils import Calendar

load_dotenv()


class CalendarView(generic.ListView):
    model = Event
    template_name = 'calendar/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # use today's date for the calendar
        today_date = get_date(self.request.GET.get('month', None))
        # Instantiate our calendar class with today's year and date
        current_calendar = Calendar(self.request.user, today_date.year, today_date.month)

        context['prev_month'] = prev_month(today_date)
        context['next_month'] = next_month(today_date)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = current_calendar.formatmonth(with_year=True)
        context['calendar'] = mark_safe(html_cal)

        return context


def prev_month(d):
    first = d.replace(day=1)
    previous_month = first - timedelta(days=1)
    month = 'month=' + str(previous_month.year) + '-' + str(previous_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    the_next_month = last + timedelta(days=1)
    month = 'month=' + str(the_next_month.year) + '-' + str(the_next_month.month)
    return month


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


@login_required(login_url='')
def event(request, event_id=None):
    attendees = []
    events = Event.objects.filter(owner_id=request.user.id).values()
    participants = Participant.objects.filter(event_id=event_id).filter(status='Accepted').values()
    attendees_ids = [participant['participants_id'] for participant in participants]
    for attendee_id in attendees_ids:
        attendees.append(User.objects.filter(pk=attendee_id).values()[0])
    print('Events: ', events, '\nParticipants: ', participants, '\nAttendees: ', attendees)

    participant_data = zip(participants, attendees)

    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
        if instance.owner.id == request.user.id:
            instance.owner = request.user
        if instance.event_address:
            address_instance = Address.objects.get(id=instance.event_address.id)
        else:
            address_instance = Address()
    else:
        instance = Event()
        instance.owner = request.user
        address_instance = Address()

    form = EventForm(request.POST or None, instance=instance)
    address_form = AddressForm(request.POST or None, instance=address_instance)

    if request.POST and form.is_valid():
        event = form.save(commit=False)
        address = address_form.save(commit=False)

        if event_id:
            if request.user.id == instance.owner.id:
                address.save()
                print('Address id in else: ', address.id)
                if address.id:
                    event.event_address_id = address.id

                event.owner = request.user
                event.save()
                return redirect('schedule_calendar:calendar')
            else:
                messages.error(request, 'You cannot edit this event!', 'danger')
        else:
            address.save()
            print('Address id in else: ', address.id)
            event.event_address_id = address.id
            event.owner = request.user
            event.save()

            return redirect('schedule_calendar:calendar')

    return render(request, 'calendar/event.html', {
        'form': form,
        'events': events,
        'address_form': address_form,
        'participant_data': participant_data,
    })


@login_required(login_url='')
def invite(request, participant_id=None):
    if participant_id:
        participant_instance = get_object_or_404(Participant, pk=participant_id)
    else:
        participant_instance = Participant()

    form = InviteParticipantForm(request.POST or None, instance=participant_instance)
    if request.POST and form.is_valid():
        """ For future use """
        # account_sid = os.environ['ACCOUNT']
        # token = os.environ['TOKEN']
        current_event = Event.objects.get(id=request.POST['event'])
        print('Username: ', request.POST['participants'])
        user = User.objects.get(id=request.POST['participants'])
        if current_event.owner_id == request.user.id:
            participant = form.save(commit=False)
            participant.event = current_event
            participant.participants = user
            participant.status = participant.Status.INVITED
            participant.save()
            print('Event: ', current_event, ' Participants: ', participant.participants)

        else:
            message = ['You do not own this event!']
            return render(request, 'calendar/invite_participant.html', {
                'form': form,
                'messages': message
            })

        invite_email = EmailHandler(
            current_user=request.user,
            template='calendar/invitation.html',
            from_email=request.user.email,
            recipient=user,
            to_email=user.email,
            subject='Event Invitation',
            current_site=get_current_site(request),
            current_event=current_event,
            participant=participant
        )
        sent = invite_email.send()

        print('Sent: ', sent)
        if sent == 1001:
            messages.error('An error has occurred, please try again!')

        return redirect('schedule_calendar:calendar')

    return render(request, 'calendar/invite_participant.html', {'form': form})


def invite_response(request):
    return render(request, 'calendar/invite_response.html')


@transaction.atomic
def signup(request):
    address_form = AddressForm(request.POST or None)
    user_form = UserForm(request.POST or None)
    profile_form = ProfileForm(request.POST or None)

    if request.method == 'POST':

        email = user_form['email'].value()
        if user_form.is_valid() and not get_user(email):

            address = address_form.save(commit=False)
            user = user_form.save(commit=False)
            user.is_active = False
            user.save()

            address.save()

            new_profile = profile_form.save(commit=False)
            new_profile.user_id = user.id
            new_profile.address_id = address.id
            new_profile.save()

            confirmation_email = EmailHandler(
                current_user=user,
                template='calendar/email.html',
                from_email=os.environ['email_address'],
                recipient=user,
                to_email=user.email,
                subject='Email Verification',
                current_site=get_current_site(request)
            )
            sent = confirmation_email.send()

            if sent == 1001:
                messages.error('An error has occurred, please try again!')
                redirect('schedule_calendar:signup')

            return redirect('schedule_calendar:verifying')
        else:

            if not user_form.is_valid():
                message = 'Username already exists'
            elif email:
                message = 'User email already exists'

            user_form = UserForm()
            # =gJZxtbrTQ)C4]FM
            return render(request, "registration/signup.html", {
                'address_form': address_form,
                'user_form': user_form,
                'profile_form': profile_form,
                'messages': [message],
            })
    else:
        return render(request, "registration/signup.html", {
            'address_form': address_form,
            'user_form': user_form,
            'profile_form': profile_form,
        })


@login_required(login_url='')
def profile(request):
    profile_instance = Profile.objects.get(user_id=request.user.id)

    if profile_instance:
        address_instance = get_object_or_404(Address, pk=profile_instance.address_id)
    else:
        address_instance = Address()

    address_form = AddressForm(request.POST or None, instance=address_instance)
    profile_form = ProfileForm(request.POST or None, instance=profile_instance)

    if request.method == 'POST' and \
            address_form.is_valid() and \
            profile_form.is_valid():

        address = address_form.save()
        print('Address id: ', address.id)
        new_profile = profile_form.save(commit=False)
        new_profile.address_id = address.id
        new_profile.save()
        return redirect('schedule_calendar:calendar')
    else:
        return render(request, 'calendar/user_profile.html', {
            'address_form': address_form,
            'profile_form': profile_form,
        })


@login_required(login_url='')
def event_delete(request, event_id=None):
    print('Removing event...')


@login_required(login_url='')
def remove_participant(request):
    print('Removing participant...')


def verifying(request):
    return render(request, 'registration/verifying.html')


# @login_required(login_url='')
def get_user(email):
    try:
        return User.objects.get(email=email.lower())
    except User.DoesNotExist:
        return None


@login_required(login_url='')
def address_book(request, check_user=None):

    address_book_owner = User.objects.get(id=request.user.id)
    profiles = []
    addresses = []
    contacts = address_book_owner.profile.contacts.values()

    for contact in contacts:
        current_id = contact['id']
        current_profile = Profile.objects.filter(user_id=current_id).values()[0]
        profiles.append(current_profile)
        addresses.append(Address.objects.filter(pk=current_profile['id']).values()[0])

    addressbook = zip(contacts, profiles, addresses)

    form = CheckIfUserExists(request.POST)
    if request.method == 'POST' and form.is_valid():

        if check_user:
            email = form['email'].value()
            user = get_user(email)
            user_exists = [contact for contact in contacts if contact['email'] == email]
            print('Contacts: ', contacts)
            print('Checking if in contacts: ',  [contact for contact in contacts if contact['email'] == email])
            if email != request.user.email and user and not user_exists:
                # address_book_owner.profile.contacts.add(user)

                return render(request, 'calendar/address_book.html', {
                    'form': form,
                    'contacts': addressbook,
                    'check_user': False,
                })
            else:
                if email == request.user.email:
                    message = "Cannot add yourself!"
                elif user_exists:
                    message = 'User already added!'
                else:
                    message = 'The email you entered is not in our system.'
                form = CheckIfUserExists()
                return render(request, 'calendar/address_book.html', {
                    'form': form,
                    'contacts': addressbook,
                    'check_user': False,
                    'messages': [message],
                })

        return redirect('schedule_calendar:address_book')
    return render(request, 'calendar/address_book.html', {
        'form': form,
        'contacts': addressbook,
    })


def index(request):
    return redirect('accounts/login')
