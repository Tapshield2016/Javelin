__author__ = 'adamshare'

import string
import random
from django.contrib.auth.models import Group
from core.models import AgencyUser, Agency
user_group = Group.objects.get(name='Dispatchers')
agency = Agency.objects.get(name='University of Florida') # set agency name
users = ["Jessica,Zarate,jzarate@ufl.edu",] # set users list
for user in users:
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