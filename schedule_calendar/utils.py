from calendar import HTMLCalendar

from .models import Event, Participant


class Calendar(HTMLCalendar):
    def __init__(self, user, year=None, month=None):
        self.year = year
        self.month = month
        self.user = user
        # self.profile = Profile.objects.get(user_id=self.user.id)
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day and owner
    def formatday(self, day, events):
        other_events = []
        try:
            participants = Participant.objects.filter(participants_id=self.user.id).values()
            # print('Other events: ', participants, ' Len(Participants]: ', len(participants))
            for participant in participants:
                other_events.append(Event.objects.filter(pk=participant['event_id']).values())

            # print(other_events[0])
        except Participant.DoesNotExist:
            print('Not Participating!!!!')

        events_per_day = events.filter(start_time__day=day, owner=self.user)
        if other_events:
            other_events_per_day = other_events[0].filter(start_time__day=day)
        else:
            other_events_per_day = []
        print('events per day : ', events_per_day, ' Type: ', type(events))
        print('other events per day: ', other_events_per_day)
        date = ''
        for event in events_per_day:
            date += f'<li><a href="event/edit/{event.id}"> {event.event_name} </a></li>'
        for event in other_events_per_day:
            date += f'<li><a href="event/edit/{event["id"]}"> {event["event_name"]} </a></li>'
        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {date} </ul></td>"
        return '<td></td>'

    # formats a week as a tr
    def formatweek(self, the_week, events):
        week = ''
        for day, weekday in the_week:
            week += self.formatday(day, events)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, with_year=True):
        events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month)

        calendar = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        calendar += f'{self.formatmonthname(self.year, self.month, withyear=with_year)}\n'
        calendar += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            calendar += f'{self.formatweek(week, events)}\n'
        return calendar
