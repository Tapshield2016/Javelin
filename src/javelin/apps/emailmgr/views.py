from forms import EmailAddressForm
from django import forms
from django.core.exceptions import ValidationError
from models import EmailAddress
from django.conf import settings
from utils import send_activation, get_template, sort_email
from signals import user_added_email, user_sent_activation, user_activated_email
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages as Msg
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
# from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, serializers, viewsets
from emailmgr.serializers import (EmailAddressGETSerializer, EmailAddressUpdateSerializer,
                                  EmailAddressViewSet,)
from django.contrib.auth import (authenticate, get_user_model,
                                 login as auth_login)
from core.api.serializers.v1 import UserSerializer

User = get_user_model()


@api_view(['POST'])
def email_add(request):
    """
    User is logged and has a primary email address already
    This will add an additional email address to this User

    email -- (Required) The user's new email address
    """

    f = forms.EmailField()
    email = request.DATA.get('email', None)

    try:
        f.clean(email)
    except ValidationError as e:
        return Response({"message": "Enter a valid email address."},
                        status=status.HTTP_400_BAD_REQUEST)

    email = email.lower()

    if EmailAddress.objects.filter(user=request.user, email=email).exists():
        return Response({"message": "Email already in use."},
                        status=status.HTTP_400_BAD_REQUEST)

    email = EmailAddress(**{'user': request.user, 'email': email})
    email.save()
    user_added_email.send(sender=EmailAddress, email_address=email)

    send_activation(email, request.is_secure())
    email.is_activation_sent = True
    email.save()
    user_sent_activation.send(sender=EmailAddress, email_address=email)

    return Response(UserSerializer(instance=request.user, context={'request': request}).data,
                    status=status.HTTP_201_CREATED)

@api_view(['POST'])
def email_make_primary(request):
    """
    User is logged in, has a second email that is already activated and 
    wants to make that the primary email address.
    The User objects' email address will also be replace with this newly
    primary email address, so Django internals work it the new primary address too

    email -- (Required) The user's secondary email address
    """
    f = forms.EmailField()
    email = request.DATA.get('email', None)

    try:
        f.clean(email)
    except ValidationError as e:
        return Response({"message": "Enter a valid email address."},
                        status=status.HTTP_400_BAD_REQUEST)

    email_to_make_primary = email.lower()


    try:
        email = EmailAddress.objects.get(user=request.user, email__iexact=email_to_make_primary)
    except EmailAddress.DoesNotExist:
        return Response({"message": "Email could not be found."},
                        status=status.HTTP_404_NOT_FOUND)
    if email.is_active:
        if email.is_primary:
            return Response(UserSerializer(instance=request.user, context={'request': request}).data,
                        status=status.HTTP_200_OK)
        else:
            emails = EmailAddress.objects.filter(user=email.user)
            for e in emails:
                e.is_primary = False
                e.save()

            email.is_primary = True
            email.save()
            return Response(UserSerializer(instance=request.user, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    return Response({"message": "Email must first be activated."},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def email_send_activation(request):
    """
    The user is logged in, has added a new email address to his/her account.
    User can do anything with the newly added email, unless it is first activated.
    This function will send an activation email to the currently primary email address 
    associated with the User's account

    email -- (Required) The user's secondary email address
    """
    f = forms.EmailField()
    email = request.DATA.get('email', None)

    try:
        f.clean(email)
    except ValidationError as e:
        return Response({"message": "Enter a valid email address."},
                        status=status.HTTP_400_BAD_REQUEST)

    email_to_activate = email.lower()


    try:
        email = EmailAddress.objects.get(user=request.user, email__iexact=email_to_activate)
    except EmailAddress.DoesNotExist:
        return Response({"message": "Email could not be found."},
                        status=status.HTTP_404_NOT_FOUND)

    if email.is_active:
        return Response({"message": "Email already activated."},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        send_activation(email, request.is_secure())
        email.is_activation_sent = True
        email.save()
        user_sent_activation.send(sender=EmailAddress, email_address=email)

    return Response({"message": "Email activation sent."},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
def email_check_activated(request, email=None):
    """
    User is logged in, has a second email that is added and
    wants to make check if it has been activated.

    email -- (Required) The user's secondary email address
    """
    email = request.DATA.get('email', None)
    if not email:
        email = request.GET.get('email', None)
    f = forms.EmailField()

    try:
        f.clean(email)
    except ValidationError as e:
        return Response({"message": "Enter a valid email address."},
                        status=status.HTTP_400_BAD_REQUEST)

    email = email.lower()

    try:
        email_object = EmailAddress.objects.get(user=request.user, email__iexact=email)
    except EmailAddress.DoesNotExist:
        return Response({"message": "Email could not be found."},
                        status=status.HTTP_404_NOT_FOUND)

    if email_object.is_active:
        return Response(UserSerializer(instance=request.user, context={'request': request}).data,
                    status=status.HTTP_200_OK)

    return Response({"message": "Email not yet activated."},
                        status=status.HTTP_400_BAD_REQUEST)


def email_activate(request, identifier="somekey"):
    """
    User is already logged in and the activation link will trigger the email address
    in question to be activated. If the account is already active, then a message is 
    put in the message buffer indicating that the email is already active

    identifier -- (Required) Randomly generated identifier for email
    """
    title = "Verification complete"
    message_response = None

    try:
        email = EmailAddress.objects.get(identifier__iexact=identifier.lower())
    except EmailAddress.DoesNotExist:
        Msg.add_message (request, Msg.ERROR, _('email address not found'))
        title = "Error"
        message_response = "This link is no longer valid"
    else:
        if email.is_active:
            Msg.add_message (request, Msg.SUCCESS, _('email address already active'))
            message_response = "Email address already verified"
        else:
            email.is_active = True
            # if not email.user.email:
            #     email.user.email = email.email
            #     email.is_primary = True
            #     email.user.save()
            email.save()
            user_activated_email.send(sender=EmailAddress, email_address=email)
            Msg.add_message (request, Msg.SUCCESS, _('email address is now active'))
            message_response = "Email address verified"
    context = {"title": title, "message_response": message_response,}
    return render_to_response(get_template('verification_complete.html'), context,
                              context_instance=RequestContext(request))

@api_view(['POST'])
def email_delete(request):
    """
    Email needs to be removed from User's account, primary email address cannot be removed
    """
    f = forms.EmailField()
    email = request.DATA.get('email', None)

    try:
        f.clean(email)
    except ValidationError as e:
        return Response({"message": "Enter a valid email address."},
                        status=status.HTTP_400_BAD_REQUEST)

    email_to_delete = email.lower()


    try:
        email = EmailAddress.objects.get(user=request.user, email__iexact=email_to_delete)
    except EmailAddress.DoesNotExist:
        return Response({"message": "Email could not be found."},
                        status=status.HTTP_404_NOT_FOUND)

    if email.email == request.user.email:
        return Response({"message": "Cannot remove primary email address."},
                        status=status.HTTP_400_BAD_REQUEST)
    elif email.user != request.user:
        return Response({"message": "Email address is not associated with this account."},
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        email.delete()

    return Response(UserSerializer(instance=request.user, context={'request': request}).data,
                        status=status.HTTP_200_OK)


# @api_view(['GET'])
def email_list(request):
    """
    All email address associated with User account will be passed into the template as a list
    An ``add`` email form will be passed in the template so user can add new email inline
    """
    form = EmailAddressForm(user=request.user)
    emails_list = EmailAddress.objects.filter(user=request.user).order_by(*sort_email())
    return render_to_response(get_template('emailmgr_email_list.html'),
                              {
                                'email_list': emails_list,
                                'email_form': form
                              },
                              context_instance=RequestContext(request)
                              )








