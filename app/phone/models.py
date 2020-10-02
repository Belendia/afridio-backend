from django.db import models
from django.conf import settings


class PhoneNumber(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    number = models.CharField(max_length=17, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-updated_at']

    def __str__(self):
        if self.user.name:
            return '{} - ({})'.format(self.user.name, self.user.phone)
        return self.user.phone
