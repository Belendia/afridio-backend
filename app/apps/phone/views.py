from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import VerifyPhoneNumberAndLoginSerializer


class VerifyPhoneNumberANDLoginViewSet(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = VerifyPhoneNumberAndLoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
