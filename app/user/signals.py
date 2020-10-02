from django.db.models.signals import pre_save
from django.dispatch import receiver
from core.models import User
import pyotp


def generate_key():
    """ User otp key generator """
    key = pyotp.random_base32()
    if is_unique(key):
        return key
    generate_key()


def is_unique(slug):
    try:
        User.objects.get(slug=slug)
    except User.DoesNotExist:
        return True
    return False


@receiver(pre_save, sender=User)
def create_key(sender, instance, **kwargs):
    """This creates the slug for users that don't have slugs"""
    if not instance.slug:
        instance.slug = generate_key()
