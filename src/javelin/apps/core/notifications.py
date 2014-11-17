__author__ = 'adamshare'


from models import (AgencyUser, EntourageMember)


def readable_name_for_user(user):

    name = user.username

    if user.first_name:

        name = user.first_name + " (" + user.username + ")"

        if user.last_name:
            name = user.first_name + " " + user.last_name

    return name


def added_by_user_message(user):

    return u"%s added you to their entourage." % readable_name_for_user(user)