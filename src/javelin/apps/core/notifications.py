__author__ = 'adamshare'

from models import (Agency, EntourageMember, EntourageSession)
from core.utils import readable_name_for_user

from django_twilio.client import twilio_client
from twilio import TwilioRestException
from django.conf import settings
from django.core.mail import send_mail

from tasks import notify_user_arrived_at_destination


def added_by_user_message(user):

    return u"%s added you to their entourage." % readable_name_for_user(user)


def called_emergency_number_message(user):

    return u"%s dialed 911.\nThey may be in need of assistance." % readable_name_for_user(user)


def arrived_message(session):

    return u"%s arrived at their destination.\n." % readable_name_for_user(session.user)


def send_arrival_notifications(session):

    message = arrived_message(session)
    user = session.user
    entourage_members = user.entourage_members.all()
    errors = []
    for member in entourage_members:

        if member.matched_user:
            notify_user_arrived_at_destination.delay(message,
                                                     user.id,
                                                     member.matched_user.device_type,
                                                     member.matched_user.device_endpoint_arn)
        elif member.phone_number:
            try:
                resp = twilio_client.messages.create( \
                    to=member.phone_number,
                    from_=settings.TWILIO_SMS_VERIFICATION_FROM_NUMBER,
                    body=message)
                if resp.status == 'failed':
                    errors.append( \
                        {"Entourage Member %d" % \
                         member.id: 'Error sending SMS Verification',
                         "id": member.id})
            except TwilioRestException, e:
                if e.code and e.code == 21211:
                    errors.append( \
                        {"Entourage Member %d" % \
                         member.id: 'Invalid phone number',
                         "id": member.id})
        elif member.email_address:
            if not subject:
                subject = "A message from TapShield"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                      [member.email_address], fail_silently=True)

    if errors:
        return {'message': 'Partial Success',
                'errors': errors}
    else:
        return {'message': 'Success'}