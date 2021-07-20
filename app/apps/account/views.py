from django.contrib.auth import logout

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import generics, authentication, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from apps.account.serializers import LoginSerializer, UserSerializer


class LoginView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = LoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class RegisterUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer


class MeView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authentication user"""

        return self.request.user


class LogoutView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        request.user.auth_token.delete()

        logout(request)

        return Response(status=HTTP_200_OK)
