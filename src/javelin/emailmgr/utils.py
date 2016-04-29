import os
import random
import string
import time
from hashlib import sha1
import defaults
from django.conf import settings
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.sites.models import Site
from django.core.mail import send_mail


# get a random string of known length
def get_unique_random(length=10):
    randtime = str(time.time()).split('.')[0]
    rand = ''.join([random.choice(randtime+string.letters+string.digits) for i in range(length)])
    return sha1(rand).hexdigest()[:length]


# given a template name, return its path
def get_template(name):
    return os.path.join(getattr(defaults, "EMAIL_MGR_TEMPLATE_PATH"), name)


# send activation link to user's primary email address
def send_activation(email, is_secure):
    # import pdb; pdb.set_trace()
    this_site = Site.objects.get_current()

    # first try to use our views fuction to construct the activation path (deterministic)
    # if views didn't reverse to a path, then use named url (less deterministic as it is user configurable)
    try:
        p = reverse("emailargs.view.email_activate",args=[email.identifier])
    except NoReverseMatch:
        p = reverse('emailmgr_email_activate', kwargs={'identifier': email.identifier})
            
    proto = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "")
    if not proto:
        if is_secure:
            proto = "https"
        else:
            proto = "http"

    url = u"%s://%s%s" % (proto, unicode(this_site.domain), p)
    context = {"user": email.user, "activate_url": url, "this_site": this_site,"identifier": email.identifier,}
    subject = "".join(render_to_string(get_template("emailmgr_activation_subject.txt"), context).splitlines())
    message = render_to_string(get_template("emailmgr_activation_message.txt"), context)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email.email])


def sort_email():
    return ['-is_primary', '-is_active', '-is_activation_sent']




