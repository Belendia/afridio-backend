from django.contrib.auth import logout
from django.contrib.auth import get_user_model

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import generics, authentication, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from apps.account.serializers import LoginSerializer, UserSerializer, \
    UpdateUserSerializer, ChangePasswordSerializer


class LoginView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = LoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {
                'name': user.name,
                'sex': user.sex,
                'phone_number': user.phone_number,
                'date_of_birth': user.date_of_birth
            }
        })


class RegisterUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer


class UpdateUserView(generics.UpdateAPIView):
    """Update the currently logged in user in the system"""

    serializer_class = UpdateUserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)


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


class ChangePasswordView(generics.UpdateAPIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.serializer_class(data=request.data, partial=True)
        # serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        # Check old password
        if not user.check_password(serializer.data.get("old_password")):
            return Response({"old_password": ["Wrong password."]}, status=HTTP_400_BAD_REQUEST)

        # set_password also hashes the password that the user will get
        user.set_password(serializer.data.get("password"))
        user.save()
        return Response(status=HTTP_200_OK)
