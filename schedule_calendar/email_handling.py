import os
import socket

from django import shortcuts
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import request, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from schedule_calendar.models import Participant, Event


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            f'{user.pk}{timestamp}{user.is_active}'
        )


account_activation_token = TokenGenerator()


class EmailHandler:

    def __init__(self, current_user: User, template: str, from_email: str,
                 recipient: User, to_email: str, subject: str,
                 current_site: shortcuts = None, current_event: Event = None,
                 participant: Participant = None):
        self.current_user = current_user
        self.template = template
        self.from_email = from_email
        self.recipient = recipient
        self.to_email = to_email
        self.subject = subject
        self.current_site = current_site
        self.current_event = current_event
        self.participant = participant


    def send(self):
        try:
            return send_mail(self.subject, self.build_message(), [self.from_email], [self.to_email])
        except socket.error:
            return 1001

    def build_message(self):
        if self.current_site:
            domain = self.current_site.domain
        else:
            domain = None
        if self.current_event:
            return render_to_string(self.template, {
                'user': self.recipient.first_name,
                'sender': self.current_user.get_full_name(),
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(self.recipient.pk)),
                'token': account_activation_token.make_token(self.recipient),
                'participant_id': self.participant.id,
                'status': self.participant.status,
                'event_id': self.current_event.id,
                'event_name': self.current_event.event_name,
                'description': self.current_event.description,
                'start_time': self.current_event.start_time,
                'end_time': self.current_event.end_time
            })
        else:
            return render_to_string(self.template, {
                'user': self.recipient.first_name,
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(self.recipient.pk)),
                'token': account_activation_token.make_token(self.recipient),

            })


def notify_event_owner(participant: int):
    print('Participant ', participant)
    current_participant = Participant.objects.get(pk=participant)
    current_event = Event.objects.get(pk=current_participant.event_id)
    respondent = User.objects.get(pk=current_participant.participant_id)
    print('Respondent: ', respondent.get_full_name(), ' current_participant: ', current_participant.participant_id)
    event_owner = User.objects.get(pk=current_event.owner.id)
    current_respondent = respondent.get_full_name()
    invite_email = EmailHandler(
        current_user=respondent,
        template='calendar/event_owner_notification.html',
        from_email=os.environ['email_address'],
        recipient=event_owner,
        to_email=event_owner.email,
        subject='Invitation response',
        current_site=None,
        current_event=current_event,
        participant=current_participant
    )
    sent = invite_email.send()
    print(sent)


def invite_result(request, uidb64, token, participant, result=''):
    print('Participant id: ', participant, ' result: ', result)
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)
    except (ValueError, User.DoesNotExist):
        user = None
    print('UID: ', uid)
    if user is not None and account_activation_token.check_token(user, token):
        new_participant = Participant.objects.get(id=participant)
        if result == 'accepted':
            new_participant.status = Participant.Status.ACCEPTED
        else:
            new_participant.status = Participant.Status.DECLINED
        new_participant.save()
        print('Accepted by: ', user, ' participant: ', participant)

        notify_event_owner(participant)
        return redirect('schedule_calendar:invite_response')
    return HttpResponse('Token expired!')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)
    except (ValueError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('schedule_calendar:login')
    else:
        return HttpResponse('Invalid activation link. Please try again>')

