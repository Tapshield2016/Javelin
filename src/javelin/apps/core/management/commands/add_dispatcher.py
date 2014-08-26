__author__ = 'adamshare'

import string
import random
from django.contrib.auth.models import Group
from core.models import AgencyUser, Agency
from optparse import make_option
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--agency',
                    dest='agency',
                    help='The numerical ID or name of the agency to add dispatcher'),
        make_option('--email',
                    dest='email',
                    help='Email of the dispatcher user to add'),
        make_option('--list',
                    dest='list',
                    help='Email of the dispatcher user to add "first,last,email"'),
    )

    def handle(self, *args, **options):

        user_group = Group.objects.get(name='Dispatchers')
        agency_name = options['agency']
        agency = Agency.objects.get(name=agency_name)

        if not agency:
            agency_id = int(options['agency'])
            agency = Agency.objects.get(pk=agency_id)

        list = options['list']
        print "%s" % (list)
        if not list:
            list = []
            email = options['email']
            list.append(" , ,"+email)

        for user in list:
            tokens = user.split(',')
            first_name = tokens[0].strip()
            last_name = tokens[1].strip()
            email = tokens[2].strip()

            password = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(6)])
            print "%s, %s" % (email, password)
            new_user = AgencyUser.objects.create_user(email, email, password)
            new_user.groups.add(user_group)
            new_user.agency = agency
            new_user.first_name = first_name.title()
            new_user.last_name = last_name.title()
            new_user.disarm_code = 0000
            new_user.phone_number = '(555) 555-5555'
            new_user.is_active = True
            new_user.email_verified = True
            new_user.save()