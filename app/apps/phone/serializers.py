from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
import logging
from apps.common.utils.phone_verification_services import send_security_code_and_generate_session_token, \
    resend_security_code, get_otp_resend_time_remaining

from .models import PhoneVerification
from apps.user.models import User
from apps.phone.backends import get_sms_backend

logger = logging.getLogger(__name__)


class VerifyPhoneNumberAndLoginSerializer(serializers.Serializer):
    """
    Serializer for the phone number verification and user authentication
    """

    phone_number = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    session_token = serializers.CharField(required=True)
    security_code = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validate and authenticate the user"""
        attrs = super().validate(attrs)

        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        security_code, session_token = (
            attrs.get("security_code", None),
            attrs.get("session_token", None),
        )

        try:
            user = User.objects.get(phone_number=phone_number)
            if not user.check_password(password):
                msg = _("Unable to authenticate the user")
                raise serializers.ValidationError({'detail': msg})
        except User.DoesNotExist:
            msg = _("User doesn't exist")
            raise serializers.ValidationError({'detail': msg})

        backend = get_sms_backend()
        verification, token_validation = backend.validate_security_code(
            security_code=security_code,
            phone_number=phone_number,
            session_token=session_token,
        )

        if verification is None:
            raise serializers.ValidationError({'detail': _("Security code is not valid")})
        elif token_validation == backend.SESSION_TOKEN_INVALID:
            raise serializers.ValidationError({'detail': _("Session Token mis-match")})
        elif token_validation == backend.SECURITY_CODE_EXPIRED:
            raise serializers.ValidationError({'detail': _("Security code has expired")})
        elif token_validation == backend.SECURITY_CODE_VERIFIED:
            raise serializers.ValidationError({'detail': _("Security code is already verified")})

        user = authenticate(
            request=self.context.get('request'),
            username=phone_number,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError({'detail': msg})

        attrs['user'] = user

        return attrs


class ResendOTPSerializer(serializers.Serializer):
    """
    Serializer for the resend OTP and user authentication
    """

    phone_number = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    session_token = serializers.CharField(required=True)
    security_code = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validate and authenticate the user"""
        attrs = super().validate(attrs)

        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        security_code, session_token = (
            attrs.get("security_code", None),
            attrs.get("session_token", None),
        )

        try:
            user = User.objects.get(phone_number=phone_number)
            if not user.check_password(password):
                msg = _("Unable to authenticate the user")
                raise serializers.ValidationError({'detail': msg})
        except User.DoesNotExist:
            msg = _("Unable to authenticate the user")
            raise serializers.ValidationError({'detail': msg})

        user = authenticate(
            request=self.context.get('request'),
            username=phone_number,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError({'detail': msg})

        backend = get_sms_backend()
        verification, token_validation = backend.validate_security_code(
            security_code=security_code,
            phone_number=phone_number,
            session_token=session_token,
        )

        resend_new_otp = False
        resend_old_otp = False
        send_opt_resend_time_remaining = False

        if verification is None:
            raise serializers.ValidationError({'detail': _("Security code is not valid")})
        elif token_validation == backend.SESSION_TOKEN_INVALID:
            raise serializers.ValidationError({'detail': _("Session Token mis-match")})
        elif token_validation == backend.SECURITY_CODE_EXPIRED:
            resend_new_otp = True
        elif token_validation == backend.SESSION_CODE_WAITING_TIME_EXPIRED:
            resend_old_otp = True
        elif token_validation == backend.SECURITY_CODE_VERIFIED:
            raise serializers.ValidationError({'detail': _("Security code is already verified")})
        else:
            send_opt_resend_time_remaining = True

        otp_resend_time = settings.PHONE_VERIFICATION.get('OTP_RESEND_TIME', 300)

        attrs = {}
        if resend_new_otp or resend_old_otp or send_opt_resend_time_remaining:
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
                    elif send_opt_resend_time_remaining:
                        otp_resend_time = get_otp_resend_time_remaining(user.phone_number)
                except:
                    msg = _('Account verification SMS could not be sent')
                    res = serializers.ValidationError({'detail': msg})
                    res.status_code = 500
                    logger.error(msg)
                    raise res

                if device_session_token is None:
                    msg = _('Account verification SMS could not be sent')
                    res = serializers.ValidationError({'detail': msg})
                    res.status_code = 500
                    logger.error(msg)
                    raise res

            attrs = {
                'phone_number': user.phone_number,
                'session_token': device_session_token,
                'otp_resend_time': otp_resend_time
            }

        return attrs
