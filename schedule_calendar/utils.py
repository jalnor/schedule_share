from datetime import datetime, timedelta
from calendar import HTMLCalendar

from django.contrib.auth.models import User
from .models import Event


class Calendar(HTMLCalendar):
	def __init__(self, user, year=None, month=None):
		self.year = year
		self.month = month
		self.user = user
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day and owner
	def formatday(self, day, events):
		events_per_day = events.filter(start_time__day=day, owner=self.user)
		other_events = events.filter(start_time__day=day, participants__user_email=self.user.email)
		print('Other events: ', other_events, ' ', self.user.email)
		date = ''
		for event in events_per_day:
			date += f'<li><a href="event/edit/{event.id}"> {event.title} </a></li>'
		for event in other_events:
			date += f'<li><a href="event/edit/{event.id}"> {event.title} </a></li>'
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
