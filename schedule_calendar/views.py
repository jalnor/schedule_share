import calendar
import os
import socket
from datetime import datetime, date, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import generic
from django.utils.safestring import mark_safe
from dotenv import load_dotenv

from .forms import EventForm, UserForm, ProfileForm, InviteParticipantForm, AddressForm
from .models import *
from .utils import Calendar

load_dotenv()


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            f'{user.pk}{timestamp}{user.is_active}'
        )


account_activation_token = TokenGenerator()


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


def event(request, event_id=None):
    participants = Participant.objects.get_queryset()

    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
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
                return HttpResponseRedirect(reverse('schedule_calendar:calendar'))
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
        'address_form': address_form,
    })


def invite(request, user_email=None):
    if user_email:
        instance = get_object_or_404(Participant, pk=request.user.id)
    else:
        instance = Participant()
    form = InviteParticipantForm(request.POST or None, instance=instance)
    if request.POST and form.is_valid():
        # For future use
        # account_sid = os.environ['ACCOUNT']
        # token = os.environ['TOKEN']
        print('Profile: ', user_email)
        print('Profile: ', instance)
        user = User.objects.get(email=instance)

        print('Profile: ', user)
        current_site = get_current_site(request)
        subject = 'Event Invitation'
        message = render_to_string('calendar/email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        from_mail = os.environ['email_address']
        to_email = form.cleaned_data.get('email')
        # try:
        #     send_mail(subject, message, [from_mail], [to_email], fail_silently=False)
        # except socket.error:
        #     redirect('schedule_calendar:signup')
        # add_form = form.save(commit=False)
        # add_form.owner_id = user
        # add_form.save()

        return redirect('schedule_calendar:calendar')

    return render(request, 'calendar/invite_participant.html', {'form': form})


@transaction.atomic
def signup(request):
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid():
            address = address_form.save()

            user = user_form.save(commit=False)
            user.is_active = False
            user.save()
            print('Url safe id: ', urlsafe_base64_encode(force_bytes(user.pk)))

            new_profile = profile_form.save(commit=False)
            new_profile.user_id = user.id
            new_profile.address_id = address.id
            new_profile.save()

            current_site = get_current_site(request)
            subject = 'Email Verification'
            message = render_to_string('calendar/email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            from_mail = os.environ['email_address']
            to_email = user_form.cleaned_data.get('email')
            try:
                send_mail(subject, message, [from_mail], [to_email], fail_silently=False)
            except socket.error:
                redirect('schedule_calendar:signup')
                # messages.success(request, 'Your update is successful!')
            return HttpResponse('Please verify your email...')
        else:
            messages.error(request, 'Please correct the error below: ')
    else:
        address_form = AddressForm()
        user_form = UserForm()
        profile_form = ProfileForm()
        return render(request, "registration/signup.html", {
            'address_form': address_form,
            'user_form': user_form,
            'profile_form': profile_form,
        })


def profile(request):

    profile_instance = Profile.objects.get(user_id=request.user.id)
    print('Profile instance: ', profile_instance)
    # address_id = profile_instance.address_id

    if profile_instance:
        address_instance = get_object_or_404(Address, pk=profile_instance.address_id)
    else:
        address_instance = Address()
    print('Address instance: ', address_instance)
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


def event_delete(request, event_id=None):
    print('Removing event...')


def remove_participant(request):
    print('Removing participant...')


def verifying(request):
    return render(request, 'registration/verifying.html')


def get_user(email):
    try:
        return User.objects.get(email=email.lower())
    except User.DoesNotExist:
        return None
    pass


def activate(request, uidb64, token):
    # user = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('schedule_calendar:login')
    else:
        return HttpResponse('Invalid activation link. Please try again>')


def index(request):
    return redirect('accounts/login')
