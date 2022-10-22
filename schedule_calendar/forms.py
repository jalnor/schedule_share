from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, DateInput
from schedule_calendar.models import Event, Profile, Participant, Address


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ('street_address', 'city', 'state', 'zipcode')


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar_url',)


class EventForm(ModelForm):
    class Meta:
        model = Event
        # datetime-local is a HTML5 input type, format to make date time show on fields
        widgets = {
            'start_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_time': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        fields = ('event_name', 'description', 'start_time', 'end_time', 'owner')

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        # input_formats to parse HTML5 datetime-local input to datetime field
        self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)
        self.fields['end_time'].input_formats = ('%Y-%m-%dT%H:%M',)


class InviteParticipantForm(ModelForm):
    class Meta:
        model = Participant
        fields = ('participant', 'event')

