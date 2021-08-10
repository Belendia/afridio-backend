from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.authtoken.models import Token
import logging

from apps.account.models import User
from .serializers import VerifyPhoneNumberAndLoginSerializer
from apps.phone.backends import get_sms_backend
from apps.common.utils.phone_verification_services import send_security_code_and_generate_session_token, \
    resend_security_code, get_otp_resend_time_remaining

logger = logging.getLogger(__name__)


class VerifyPhoneNumberANDLoginViewSet(ObtainAuthToken):
    """Create a new auth token for account"""

    serializer_class = VerifyPhoneNumberAndLoginSerializer
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


class ResendOTPView(APIView):

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number', None)
        password = request.data.get('password', None)
        session_token = request.data.get('session_token', None)

        try:
            user = User.objects.get(phone_number=phone_number)
            if not user.check_password(password):
                msg = _("Unable to authenticate the account")
                return Response({'detail': msg}, status=HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            msg = _("Unable to authenticate the account")
            return Response({'detail': msg}, status=HTTP_400_BAD_REQUEST)

        user = authenticate(
            request=request,
            username=phone_number,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise Response({'detail': msg}, status=HTTP_400_BAD_REQUEST)

        backend = get_sms_backend()
        verification, token_validation = backend.status_of_security_code(
            phone_number=phone_number,
            session_token=session_token,
        )

        resend_new_otp = False
        resend_old_otp = False
        resend_time_remaining = False

        if verification is None:
            resend_new_otp = True
        elif token_validation == backend.SESSION_TOKEN_INVALID:
            return Response({'detail': _("Session Token mis-match")}, status=HTTP_400_BAD_REQUEST)
        elif token_validation == backend.SECURITY_CODE_EXPIRED:
            resend_new_otp = True
        elif token_validation == backend.SESSION_CODE_WAITING_TIME_EXPIRED:
            resend_old_otp = True
        elif token_validation == backend.SEND_TIME_REMAINING:
            resend_time_remaining = True

        otp_resend_time = settings.PHONE_VERIFICATION.get('OTP_RESEND_TIME', 300)

        attrs = {}
        if resend_new_otp or resend_old_otp or resend_time_remaining:
            device_session_token = None
            if user.phone_number:
                try:
                    if resend_new_otp:
                        device_session_token = send_security_code_and_generate_session_token(
                            user.phone_number, user
                        )
                    elif resend_old_otp:
                        device_session_token = resend_security_code(
                            user.phone_number
                        )
                    elif resend_time_remaining:
                        otp_resend_time, device_session_token = get_otp_resend_time_remaining(user.phone_number)
                except Exception as e:
                    logger.error(e)
                    msg = _('Account verification SMS could not be sent')
                    return Response({'detail': msg}, status=HTTP_400_BAD_REQUEST)

                if device_session_token is None:
                    msg = _('Account verification SMS could not be sent')
                    logger.error(msg)
                    return Response({'detail': msg}, status=HTTP_400_BAD_REQUEST)

            attrs = {
                'phone_number': user.phone_number,
                'session_token': device_session_token,
                'otp_resend_time': otp_resend_time
            }

        return Response(attrs, status=HTTP_200_OK)
