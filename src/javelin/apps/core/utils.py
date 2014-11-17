import time
import uuid
import ast

from django.conf import settings

from core.aws.dynamodb import DynamoDBManager
from core.models import Agency, AgencyUser
from core.tasks import notify_new_chat_message_available
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models import get_models, Model
from django.contrib.contenttypes.generic import GenericForeignKey


def send_message_to_user_for_alert(alert, message):
    message_id = str(uuid.uuid1())
    if not alert.agency_dispatcher:
        # If no dispatcher assigned to alert, get last logged in dispatcher
        # from agency and use as sender.
        last_logged_in =\
            AgencyUser.objects.filter(agency=alert.agency,
                                      groups__name='Dispatchers')\
            .order_by('-last_login')
        if last_logged_in:
            sender_id = last_logged_in[0].id
    else:
        sender_id = alert.agency_dispatcher.id
    dynamo_db = DynamoDBManager()
    dynamo_db.save_item_to_table(\
        settings.DYNAMO_DB_CHAT_MESSAGES_TABLE,
        {'alert_id': alert.id, 'sender_id': sender_id,
         'message': message, 'timestamp': time.time(),
         'message_id': message_id})
    user = alert.agency_user
    if len(message) > 112:
        # truncate to prevent issue with push notification send
        message = "%s..." % message[:109]
    notify_new_chat_message_available.delay(\
        message, message_id,
        alert.agency_user.device_type,
        alert.agency_user.device_endpoint_arn)


def get_agency_from_unknown(unknown_object):

    agency = None

    try:
        agency = Agency.objects.get(name__iexact=unknown_object)
    except Agency.DoesNotExist:
        agency_id = ''.join(x for x in unknown_object if x.isdigit())
        if type(ast.literal_eval(agency_id)) is int:
            try:
                agency = Agency.objects.get(pk=agency_id)
            except Agency.DoesNotExist:
                return None

    return agency


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups)


def readable_name_for_user(user):

    name = user.username

    if user.get_full_name():
        # name = user.first_name + " (" + user.username + ")"
        # if user.last_name:
        #     name = user.first_name + " " + user.last_name
        name = user.get_full_name()

    return name



@transaction.atomic
def merge_model_objects(primary_object, alias_objects=[], keep_old=False):
    """
        Use this function to merge model objects (i.e. Users, Organizations, Polls,
        etc.) and migrate all of the related fields from the alias objects to the
        primary object.

        Usage:
        from django.contrib.auth.models import User
        primary_user = User.objects.get(email='good_email@example.com')
        duplicate_user = User.objects.get(email='good_email+duplicate@example.com')
        merge_model_objects(primary_user, duplicate_user)
        """
    if not isinstance(alias_objects, list):
        alias_objects = [alias_objects]

    # check that all aliases are the same class as primary one and that
    # they are subclass of model
    primary_class = primary_object.__class__

    if not issubclass(primary_class, Model):
        raise TypeError('Only django.db.models.Model subclasses can be merged')

    for alias_object in alias_objects:
        if not isinstance(alias_object, primary_class):
            raise TypeError('Only models of same class can be merged')

    # Get a list of all GenericForeignKeys in all models
    # TODO: this is a bit of a hack, since the generics framework should provide a similar
    # method to the ForeignKey field for accessing the generic related fields.
    generic_fields = []
    for model in get_models():
        for field_name, field in filter(lambda x: isinstance(x[1], GenericForeignKey), model.__dict__.iteritems()):
            generic_fields.append(field)

    blank_local_fields = set([field.attname for field in primary_object._meta.local_fields if getattr(primary_object, field.attname) in [None, '']])

    # Loop through all alias objects and migrate their data to the primary object.
    for alias_object in alias_objects:
        # Migrate all foreign key references from alias object to primary object.
        for related_object in alias_object._meta.get_all_related_objects():
            # The variable name on the alias_object model.
            alias_varname = related_object.get_accessor_name()
            # The variable name on the related model.
            obj_varname = related_object.field.name
            related_objects = getattr(alias_object, alias_varname)
            for obj in related_objects.all():
                setattr(obj, obj_varname, primary_object)
                obj.save()

        # Migrate all many to many references from alias object to primary object.
        for related_many_object in alias_object._meta.get_all_related_many_to_many_objects():
            alias_varname = related_many_object.get_accessor_name()
            obj_varname = related_many_object.field.name

            if alias_varname is not None:
                # standard case
                related_many_objects = getattr(alias_object, alias_varname).all()
            else:
                # special case, symmetrical relation, no reverse accessor
                related_many_objects = getattr(alias_object, obj_varname).all()
            for obj in related_many_objects.all():
                getattr(obj, obj_varname).remove(alias_object)
                getattr(obj, obj_varname).add(primary_object)

        # Migrate all generic foreign key references from alias object to primary object.
        for field in generic_fields:
            filter_kwargs = {}
            filter_kwargs[field.fk_field] = alias_object._get_pk_val()
            filter_kwargs[field.ct_field] = field.get_content_type(alias_object)
            for generic_related_object in field.model.objects.filter(**filter_kwargs):
                setattr(generic_related_object, field.name, primary_object)
                generic_related_object.save()

        # Try to fill all missing values in primary object by values of duplicates
        filled_up = set()
        for field_name in blank_local_fields:
            val = getattr(alias_object, field_name)
            if val not in [None, '']:
                setattr(primary_object, field_name, val)
                filled_up.add(field_name)
        blank_local_fields -= filled_up

        if not keep_old:
            alias_object.delete()
    primary_object.save()
    return primary_object