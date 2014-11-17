__author__ = 'adamshare'

from models import (Agency, EntourageMember)
from core.utils import readable_name_for_user


def added_by_user_message(user):

    return u"%s added you to their entourage." % readable_name_for_user(user)