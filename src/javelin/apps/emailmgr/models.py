from utils import get_unique_random
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals


class EmailAddress(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="secondary_email")
    email = models.EmailField(_("Email Address"))
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_activation_sent = models.BooleanField(default=False)
    identifier = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name = _("email address")
        verbose_name_plural = _("email addresses")
        unique_together = (("user", "email"),)

    def __unicode__(self):
        return u"%s (%s)" % (self.email, self.user.username)

    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = get_unique_random(20).lower()
        super(EmailAddress, self).save(*args, **kwargs)

