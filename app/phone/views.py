from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token

from common.utils.sms import send_sms_code
from .serializers import PhoneNumberSerializer, VerifyOTPAndLoginSerializer
from .models import PhoneNumber


class PhoneViewset(viewsets.ModelViewSet):
    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        """Associate user with phone number"""

        serializer.save(user=self.request.user)


class SendSMS(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        send_sms_code(request.user)
        return Response(status=200)


# class VerifyPhone(APIView):
#
#     def get(self, request, *args, **kwargs):
#         sms_code = self.kwargs['sms_code']
#         try:
#             code = int(sms_code)
#             if request.user.authenticate(code):
#                 phone = request.user.phonenumber
#                 phone.verified = True
#                 phone.save()
#
#                 phone = request.get('phone')
#                 password = request.get('password')
#
#                 user = authenticate(
#                     request=self.context.get('request'),
#                     username=phone,
#                     password=password
#                 )
#
#                 return Response(dict(detail="Phone number verified "
#                                             "successfully"),
#                                 status=201)
#             return Response(
#                 dict(detail='The provided code did not match or has expired'),
#                 status=404)
#         except ValueError:
#             Response(dict(detail="Code should be integer"), status=400)


class VerifyOTPANDLogin(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = VerifyOTPAndLoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
