import calendar
from datetime import datetime, date, timedelta

from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.views import generic
from django.utils.safestring import mark_safe

from .forms import EventForm, UserForm, ScheduleUserForm, AddParticipantForm
from .models import *
from .utils import Calendar


class CalendarView(generic.ListView):
    model = Event
    template_name = 'calendar/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.request.user)
        # use today's date for the calendar
        # d = get_date(self.request.GET.get('day', None))
        d = get_date(self.request.GET.get('month', None))
        # print('Current user: ', self.context('user'))
        # Instantiate our calendar class with today's year and date
        cal = Calendar(self.request.user, d.year, d.month)

        # d = get_date(self.request.GET.get('month', None))
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)

        return context


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


def event(request, event_id=None):
    participants = Participant.objects.get_queryset()
    print('Participants: ', participants)
    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
    else:
        instance = Event()

    form = EventForm(request.POST or None, instance=instance)
    # form.participants.objects.filter()
    if request.POST and form.is_valid():
        if event_id:
            if request.user.id == instance.owner.id:
                event_form = form.save(commit=False)
                event_form.owner = request.user
                event_form.save()
                for participant in participants:
                    participant.event_id = event_id
                    participant.save()
                return HttpResponseRedirect(reverse('schedule_calendar:calendar'))
            else:
                messages.error(request, 'You cannot edit this event!', 'danger')
        else:
            event_form = form.save(commit=False)
            event_form.owner = request.user
            event_form.save()
            return HttpResponseRedirect(reverse('schedule_calendar:calendar'))

    return render(request, 'calendar/event.html', {'form': form})


def add_participant(request, user_email=None):
    print('Supposed to go to add participant here...', request.user.email, ' With user_email: ', user_email)
    if user_email:
        instance = get_object_or_404(Participant, pk=request.user.email)
    else:
        instance = Participant()
        print('Instance: ', instance)
    form = AddParticipantForm(request.POST or None, instance=instance)
    if request.POST and form.is_valid():
        user = ScheduleUser.objects.get(user_id=request.user.id)

        print('ScheduleUser: ', user)
        add_form = form.save(commit=False)
        add_form.inviter_id = user
        add_form.save()


        return HttpResponseRedirect(reverse('schedule_calendar:calendar'))
    print('Should return view here...')
    return render(request, 'calendar/add_participant.html', {'form': form})


@transaction.atomic
def signup(request):
    if request.method == 'POST':
        print('Getting form data...')
        user_form = UserForm(request.POST)  # , instance=request.user
        schedule_user_form = ScheduleUserForm(request.POST)  # , instance=request.user.scheduleuser
        print('ScheduleUserForm data...', schedule_user_form.data)
        if user_form.is_valid() and schedule_user_form.is_valid():

            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            print(user.id)

            schedule_user = schedule_user_form.save(commit=False)
            schedule_user.user_id = user.id
            schedule_user.save()

            messages.success(request, 'Your update is successful!')
            return redirect('schedule_calendar:login')
        else:
            messages.error(request, _('Please correct the error below: '))
    else:
        print('Getting forms...')
        user_form = UserForm()
        schedule_user_form = ScheduleUserForm()
        return render(request, "registration/signup.html", {
            'user_form': user_form,
            'schedule_user_form': schedule_user_form
        })


def index(request):
    return HttpResponseRedirect('accounts/login')
