__author__ = 'adamshare'

from models import (Agency, EntourageMember)
from core.utils import readable_name_for_user


def added_by_user_message(user):

    return u"%s added you to their entourage." % readable_name_for_user(user)


def called_emergency_number_message(user):

    return u"%s dialed 911.\nThey may be in need of assistance." % readable_name_for_user(user)