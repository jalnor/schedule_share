from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
# from phonenumber_field.modelfields import PhoneNumberField


class Address(models.Model):
    street_address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=75, blank=True)
    state = models.CharField(max_length=25, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)
    avatar_url = models.URLField(blank=True)


# TODO Need to fix, may need profile id to link to profile instead of addressbook to profile
class AddressBook(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    contacts = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)


class Event(models.Model):
    event_name = models.CharField(max_length=200)
    description = models.TextField()
    event_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)

    readonly_fields = 'Owner'

    def __str__(self):
        return self.event_name

    @property
    def get_html_url(self):
        url = reverse('calendar:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.event_name} </a>'


class Participant(models.Model):

    class Status(models.TextChoices):
        INVITED = 'Invited'
        ACCEPTED = 'Accepted'
        DECLINED = 'Declined'

    participant = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True)
    status = models.CharField(max_length=8, choices=Status.choices, default=None)

    def __str__(self):
        return self.participant.email
