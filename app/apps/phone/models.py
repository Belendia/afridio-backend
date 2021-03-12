from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from apps.common.models import TimeStampedModel


class PhoneVerification(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='phonenumber'
    )
    phone_number = models.CharField(_("Phone Number"), max_length=17, blank=True)
    security_code = models.CharField(_("Security Code"), max_length=120)
    session_token = models.CharField(_("Device Session Token"), max_length=500)
    is_verified = models.BooleanField(_("Security Code Verified"), default=False)

    class Meta:
        ordering = ['-created_at', '-updated_at']
        verbose_name = _("Phone Number Verification")
        verbose_name_plural = _("Phone Number Verifications")
        unique_together = ("security_code", "phone_number", "session_token")

    def __str__(self):
        if self.user.name:
            return '{} - ({})'.format(self.user.name, self.user.phone_number)
        return self.user.phone_number
