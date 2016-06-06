import datetime
import requests
import json

from time import mktime
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login as auth_login
)
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
)
from django.views.decorators.csrf import csrf_exempt

from tasks import new_alert

from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialLogin, SocialToken, SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.linkedin_oauth2.provider \
    import LinkedInOAuth2Provider
from allauth.socialaccount.providers.linkedin_oauth2.views \
    import LinkedInOAuth2Adapter
from allauth.socialaccount.providers.facebook.forms import FacebookConnectForm
from allauth.socialaccount.providers.facebook.provider import FacebookProvider
from allauth.socialaccount.providers.facebook.views import fb_complete_login
from allauth.socialaccount.providers.twitter.provider import TwitterProvider
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter

from allauth.socialaccount.helpers import complete_social_login

from registration.models import RegistrationProfile

from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from twilio.util import TwilioCapability


from agency.models import Agency

from models import (EntourageMember, Alert)
from api.serializers.v1 import (
    UserSerializer,
    AgencySerializer,
    AlertSerializer,
    EntourageMemberSerializer,
    UserLoginSerializer
)

User = get_user_model()


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)


@api_view(['POST'])
def register_user(request):
    """
    Registers a new user under the specified agency. If a phone number is
    provided, an SMS verification message will be sent to the user with an
    auto-generated verification code.

    The user will receive a verification email with a link back to our site,
    which will activate the user's account and mark the email_verified field
    as 'True'. The verification link will expire after 30 days, after which
    time the user can re-register with the same info if needed.

    Email addresses are unique identifiers in this system and registration
    will fail if a user has previously registered with the provided address.

    agency -- (Required) Numerical ID of the agency
    username -- (Required) The user's email address
    email -- (Required) The user's email address
    password -- (Required) The user's desired password in plain text
    phone_number -- (Optional) The user's phone number
    disarm_code -- (Optional) The user's alert disarm code
    first_name -- (Optional) The user's first name
    last_name -- (Optional) The user's last name

    """
    request_data = request.data.copy()
    agency_id = request_data.get('agency', None)
    agency = None
    if agency_id:
        del request_data['agency']
        try:
            agency = Agency.objects.get(pk=agency_id)
        except Agency.DoesNotExist:
            pass

    email = request_data.get('email', None)
    if email:
        email = email.lower()

    if 'username' not in request_data:
        request_data['username'] = email

    try:
        existing_user = User.objects.get(email=email)
        if existing_user:
            if not existing_user.email_verified and not existing_user.is_active:
                profile = RegistrationProfile.objects.get(user=existing_user)
                profile.delete()
                existing_user.delete()

    except User.DoesNotExist, RegistrationProfile.DoesNotExist:
        pass

    serialized = UserSerializer(data=request_data, context={'request': request})
    if serialized.is_valid():
        user = RegistrationProfile.objects.create_inactive_user(
            serialized.init_data['email'].lower(),
            serialized.init_data['username'].lower(),
            serialized.init_data['password'],
            get_current_site(request),
        )
        user_group = Group.objects.get(name='Users')
        user.groups.add(user_group)
        if agency:
            user.agency = agency
        user.phone_number = request_data.get('phone_number', '')
        user.disarm_code = request_data.get('disarm_code', '')
        user.first_name = request_data.get('first_name', '')
        user.last_name = request_data.get('last_name', '')
        user.save()
        return Response(UserSerializer(instance=user, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def resend_verification_email(request):
    """
    Sends another email to verify the email address provided by the user.
    If the email is sent without issue, a 200 status code will be returned.
    Other scenarios can occur and result in a 400, such as:

    - No registration profile found for user: This happens when a user is
      created through the Django admin and not the API's register method.
    - User has already been actived
    - User not found (e.g. email address is unknown)
    - Email required (email address is missing from query parameters)

    email -- (Required) The email address of the user requesting resending.
    """
    email = request.data.get('email', None)
    message = "Ok"
    response_status = status.HTTP_200_OK
    if email:
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                try:
                    profile = RegistrationProfile.objects.get(user=user)
                    if profile.activation_key_expired():
                        profile.delete()
                        profile = \
                            RegistrationProfile.objects.create_profile(user)
                    profile.send_activation_email(get_current_site(request))
                    user.date_joined = datetime.datetime.now()
                    user.save()
                except RegistrationProfile.DoesNotExist:
                    message = "No registration profile found for user."
                    response_status = status.HTTP_400_BAD_REQUEST
            else:
                message = "User has already been activated"
                response_status = status.HTTP_400_BAD_REQUEST
        except User.DoesNotExist, RegistrationProfile.DoesNotExist:
            message = "User not found"
            response_status = status.HTTP_400_BAD_REQUEST
    else:
        message = "Email required"
        response_status = status.HTTP_400_BAD_REQUEST
    return Response({"message": message}, status=response_status)


@csrf_exempt
def login(request):
    """
    Attempts to login the user represented by the provided username and
    password. The username should be the user's email address.

    The flow works as follows:

    1. If request method is GET:
       a. Returns a 200 if the user is already logged in.
       b. Otherwise, returns a 401 and an 'Auth-Response' header with a 'Login
          failed' message. An attempt should be made to POST login info now.
    2. If request method is POST:
       a. Attempts to authenticate the user
          1. If successful:
             a. Logs in user if the user is active and has a verified 
                email address. 
             b. Otherwise, returns a 401 or 403 with a message specifying which
                check failed. Since we must resend verification if the email 
                address is not verified, that error is prioritized.
                This also allows for deactivation of users to prevent login
                after email verification is complete (403).
          2. Otherwise, returns a 401 and an 'Auth-Response' header with a 
             'Login failed' message.
    """
    login_failed = False
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active and user.email_verified:
                auth_login(request, user)
            else:
                if not user.email_verified:
                    response = HttpResponse(content='User email address has not been verified')
                    response.status_code = 401
                    response['Auth-Response'] = 'Email unverified'
                    if not user.is_active:
                        try:
                            profile = RegistrationProfile.objects.get(user=user)
                            if profile.activation_key_expired():
                                profile.delete()
                                profile = RegistrationProfile.objects.create_profile(user)
                                profile.send_activation_email(get_current_site(request))
                                user.date_joined = datetime.datetime.now()
                                user.save()
                        except RegistrationProfile.DoesNotExist:
                            pass
                    return response
                if not user.is_active:
                    return HttpResponseForbidden(
                        content='Your account is not active.'
                    )
        else:
            login_failed = True

    if request.user.is_authenticated():
        status = 200
        serialized = UserLoginSerializer(request.user, context={'request': request})
        message = json.dumps(serialized.data, cls=DjangoJSONEncoder)
    else:
        status = 401
        message = "Authorization required."

    response = HttpResponse(content=message)
    response.status_code = status
    if status == 200:
        response.content_type = 'application/json'

    if login_failed:
        response['Auth-Response'] = 'Login failed'

    return response


@api_view(['GET'])
def verified(request):
    """
    Checks if the supplied email address has been verified.

    email -- (Required) The email address to check
    """
    user_email = request.GET.get('email', None)
    message = ''
    if user_email:
        try:
            user = User.objects.get(email=user_email)
            message = user.email_verified
            return Response({'message': message})
        except User.DoesNotExist:
            message = 'user not found'
        except ValueError:
            message = 'user must be an integer'
    else:
        message = 'user is a required parameters'
    return Response({'message': message},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def twilio_call_token(request):
    """
    Returns a Twilio capability token allowing for an outbound client call
    to be made with an expiration of 2 hours.
    """
    capability = TwilioCapability(settings.TWILIO_ACCOUNT_SID,
                                  settings.TWILIO_AUTH_TOKEN)
    capability.allow_client_outgoing(settings.TWILIO_APP_SID)
    return Response({'token': capability.generate(expires=60 * 120)},
                    status=status.HTTP_200_OK)


def dial(request):
    from_number = settings.TWILIO_SMS_FROM_NUMBER
    content = """<Response>
    <Dial callerId="%s">
        <Number>%s</Number>
    </Dial>
    <Say>Thank you, goodbye!</Say>
</Response>""" % (from_number, request.GET.get('To', None))
    return HttpResponse(content, mimetype='text/xml')


def set_necessary_fields_on_social_user(user):
    if not user.email:
        user.email = user.username

    user.email_verified = True
    user.user_logged_in_via_social = True
    user_group = Group.objects.get(name='Users')
    user.groups.add(user_group)
    user.save()
    return user


@api_view(['POST'])
def create_facebook_user(request):
    """Allows REST calls to programmatically create new facebook users.     
    
    This code is very heavily based on                                      
    allauth.socialaccount.providers.facebook.views.login_by_token           
    as of allauth 0.15.0.                                                   
    """
    form = FacebookConnectForm(request.data)
    if form.is_valid():
        try:
            app = providers.registry.by_id(FacebookProvider.id) \
                .get_app(request)
            access_token = form.cleaned_data['access_token']
            token = SocialToken(app=app,
                                token=access_token)
            login = fb_complete_login(request, app, token)
            login.token = token
            login.state = SocialLogin.state_from_request(request)
            complete_social_login(request, login)
            user = set_necessary_fields_on_social_user(login.account.user)

            serialized = UserLoginSerializer(user, context={'request': request})

            return Response(serialized.data,
                            status=status.HTTP_201_CREATED)

        except requests.RequestException:
            errors = {'access_token': ['Error accessing FB user profile.']}
    else:
        errors = dict(form.errors.items())

    return Response(errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_twitter_user(request):
    app = providers.registry.by_id(TwitterProvider.id) \
        .get_app(request)
    oauth_token = request.data.get('oauth_token')
    oauth_token_secret = request.data.get('oauth_token_secret')
    token = SocialToken(app=app,
                        token=oauth_token,
                        token_secret=oauth_token_secret)
    request.session['oauth_api.twitter.com_access_token'] = \
        {"oauth_token": oauth_token,
         "oauth_token_secret": oauth_token_secret}
    adapter = TwitterOAuthAdapter(request)
    login = adapter.complete_login(request, app, token, None)
    login.token = token
    login.state = SocialLogin.state_from_request(request)
    complete_social_login(request, login)
    user = set_necessary_fields_on_social_user(login.account.user)
    user.save()

    serialized = UserLoginSerializer(user, context={'request': request})

    return Response(serialized.data,
                    status=status.HTTP_201_CREATED)


@api_view(['POST'])
def create_google_user(request):
    app = providers.registry.by_id(GoogleProvider.id) \
        .get_app(request)
    access_token = request.data.get('access_token')
    refresh_token = request.data.get('refresh_token')
    token = SocialToken(app=app,
                        token=access_token)
    adapter = GoogleOAuth2Adapter(request)
    login = adapter.complete_login(request, app, token)
    login.token = token
    login.state = SocialLogin.state_from_request(request)
    complete_social_login(request, login)
    user = set_necessary_fields_on_social_user(login.account.user)

    serialized = UserLoginSerializer(user, context={'request': request})

    return Response(serialized.data,
                    status=status.HTTP_201_CREATED)


@api_view(['POST'])
def create_linkedin_user(request):
    app = providers.registry.by_id(LinkedInOAuth2Provider.id) \
        .get_app(request)
    access_token = request.data.get('access_token')
    token = SocialToken(app=app,
                        token=access_token)
    adapter = LinkedInOAuth2Adapter(request)
    login = adapter.complete_login(request, app, token)
    login.token = token
    login.state = SocialLogin.state_from_request(request)
    complete_social_login(request, login)
    user = set_necessary_fields_on_social_user(login.account.user)

    serialized = UserLoginSerializer(user, context={'request': request})
    if user.agency:
        serialized.data['agency'] = \
            AgencySerializer(user.agency, context={'request': request}).data

    token, created = Token.objects.get_or_create(user=user)
    serialized.data['token'] = token.key

    return Response(serialized.data,
                    status=status.HTTP_201_CREATED)


@api_view(['POST'])
def create_alert(request):
    request_data = request.data.copy()

    if request_data:
        request_data['user'] = request.user.username
        created = new_alert(request_data)
        active_alerts = Alert.active.filter(agency_user=request.user)
        if created:
            if active_alerts:
                return Response(AlertSerializer(instance=active_alerts[0], context={'request': request}).data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Could not find active alert"},
                                status=status.HTTP_404_NOT_FOUND)

    return Response({"message": "Failed to create alert"},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def find_active_alert(request):
    active_alerts = Alert.active.filter(agency_user=request.user)

    if not active_alerts:
        response = HttpResponse(content="No active alert found")
        response.status_code = 404
        return response

    return Response(AlertSerializer(instance=active_alerts[0], context={'request': request}).data,
                    status=status.HTTP_200_OK)


@api_view(['POST'])
def set_entourage_members(request):
    """
    Sync entourage members.
    Send no params for remove all.
    """

    current_members = []

    for member in request.data:

        member['user'] = UserSerializer(request.user, context={'request': request}).data['url']
        serializer = EntourageMemberSerializer(data=member, context={'request': request})

        if serializer.is_valid():

            serializer.object.user = request.user

            existing = None

            if serializer.object.phone_number:
                existing = EntourageMember.objects.filter(user=serializer.object.user,
                                                          phone_number=serializer.object.phone_number)

            if not existing and serializer.object.email_address:
                existing = EntourageMember.objects.filter(user=serializer.object.user,
                                                          email_address=serializer.object.email_address)

            member_to_save = serializer.object

            if existing:
                member_to_save = existing[0]
                member['user'] = request.user
                member_to_save.__dict__.update(member)

            member_to_save.save()

            if member_to_save.matched_user:
                if member_to_save.matched_user == request.user:
                    member_to_save.delete()
                else:
                    for old_member in request.user.entourage_members.all().exclude(pk=member_to_save.pk):
                        if old_member.matched_user == member_to_save.matched_user:
                            member_to_save.delete()

            current_members.append(member_to_save.pk)

    members_to_delete = EntourageMember.objects.filter(user=request.user).exclude(pk__in=current_members)
    for member in members_to_delete:
        member.delete()

    return Response(EntourageMemberSerializer(EntourageMember.objects.filter(user=request.user), many=True,
                                              context={'request': request}).data,
                    status=status.HTTP_200_OK)
