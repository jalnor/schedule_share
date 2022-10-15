from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class ScheduleUser(models.Model):
    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=75, blank=True)
    state = models.CharField(max_length=25, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    avatar_url = models.URLField(blank=True)


class Participant(models.Model):
    user_email = models.EmailField(blank=True)
    event_id = models.IntegerField(null=True, blank=True)
    inviter_id = models.ForeignKey(ScheduleUser, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.user_email


# TODO Rename class to match application and add variables for ex. address...
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    owner = models.ForeignKey(User, editable=False, on_delete=models.CASCADE,
                              null=True, blank=True, related_name='schedule_calendar_event')
    participants = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def get_html_url(self):
        url = reverse('calendar:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'




