__author__ = 'adamshare'

from django_twilio.client import twilio_client
from twilio import TwilioRestException
from django.conf import settings
from django.core.mail import send_mail

from tasks import (notify_user_arrived_at_destination, notify_user_yank_alert,
                   notify_user_failed_arrival, notify_user_called_emergency_number)

from models import (Agency, EntourageMember, EntourageSession)
from utils import readable_name_for_user


def added_by_user_message(user):

    return u"%s added you to their entourage." % readable_name_for_user(user)


def called_emergency_number_message(user):

    return u"%s dialed 911. They may be in need of assistance." % readable_name_for_user(user)


def called_emergency_number_subject(user):

    return u"%s dialed 911." % readable_name_for_user(user)


def yank_message(user):

    return u"%s triggered a Yank alert using their headphones. They may be in need of assistance." % readable_name_for_user(user)


def yank_subject(user):

    return u"%s triggered a Yank alert" % readable_name_for_user(user)


def arrived_message(session):
    return u"%s has arrived at %s, %s" % (readable_name_for_user(session.user),
                                          session.end_location.name,
                                          session.end_location.formatted_address)


def arrived_subject(session):

    return u"%s has arrived at their destination." % readable_name_for_user(session.user)


def non_arrival_message(session):
    return u"%s has not made it to %s, %s, within their estimated time of arrival." % (readable_name_for_user(session.user),
                                                                                       session.end_location.name,
                                                                                       session.end_location.formatted_address)


def non_arrival_subject(session):

    return u"%s has not made it to their destination." % readable_name_for_user(session.user)


def send_message_to_sms_or_email(member, subject, message):

    errors = []
    if member.phone_number:
        try:
            resp = twilio_client.messages.create(
                to=member.phone_number,
                from_=settings.TWILIO_SMS_VERIFICATION_FROM_NUMBER,
                body=message)
            if resp.status == 'failed':
                errors.append(
                    {"Entourage Member %d" % member.id: 'Error sending SMS Verification',
                     "id": member.id})
        except TwilioRestException, e:
            if e.code and e.code == 21211:
                errors.append(
                    {"Entourage Member %d" % member.id: 'Invalid phone number',
                     "id": member.id})
    elif member.email_address:
        if not subject:
            subject = "A message from TapShield"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  [member.email_address], fail_silently=True)

    return errors


def send_arrival_notifications(session):

    message = arrived_message(session)
    subject = arrived_subject(session)
    user = session.user
    entourage_members = user.entourage_members.all()
    errors = []
    for member in entourage_members:

        if not member.notify_arrival:
            continue

        if member.matched_user:
            notify_user_arrived_at_destination.delay(message,
                                                     user.id,
                                                     member.matched_user.device_type,
                                                     member.matched_user.device_endpoint_arn)
        else:
            send_message_to_sms_or_email(member, subject, message)

    if errors:
        return {'message': 'Partial Success',
                'errors': errors}
    else:
        return {'message': 'Success'}


def send_non_arrival_notifications(session):

    message = non_arrival_message(session)
    subject = non_arrival_subject(session)
    user = session.user
    entourage_members = user.entourage_members.all()
    errors = []
    for member in entourage_members:

        # send_message_to_sms_or_email(member, subject, message)

        if not member.notify_non_arrival:
            continue

        send_message_to_sms_or_email(member, subject, message)

        # if member.matched_user:
        #     notify_user_failed_arrival.delay(message,
        #                                      user.id,
        #                                      member.matched_user.device_type,
        #                                      member.matched_user.device_endpoint_arn)
        # else:
        #     send_message_to_sms_or_email(member, subject, message)

    if errors:
        return {'message': 'Partial Success',
                'errors': errors}
    else:
        return {'message': 'Success'}


def send_called_emergency_notifications(user):

    message = called_emergency_number_message(user)
    subject = called_emergency_number_subject(user)
    entourage_members = user.entourage_members.all()
    errors = []
    for member in entourage_members:

        if not member.notify_called_911:
            continue

        if member.matched_user:
            notify_user_called_emergency_number.delay(message,
                                                      user.id,
                                                      member.matched_user.device_type,
                                                      member.matched_user.device_endpoint_arn)
        else:
            send_message_to_sms_or_email(member, subject, message)

    if errors:
        return {'message': 'Partial Success',
                'errors': errors}
    else:
        return {'message': 'Success'}


def send_yank_alert_notifications(user):

    message = yank_message(user)
    subject = yank_subject(user)
    entourage_members = user.entourage_members.all()
    errors = []
    for member in entourage_members:

        if not member.notify_yank:
            continue

        if member.matched_user:
            notify_user_yank_alert.delay(message,
                                         user.id,
                                         member.matched_user.device_type,
                                         member.matched_user.device_endpoint_arn)
        else:
            send_message_to_sms_or_email(member, subject, message)

    if errors:
        return {'message': 'Partial Success',
                'errors': errors}
    else:
        return {'message': 'Success'}

