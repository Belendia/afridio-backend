from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from rest_framework import serializers
from apps.phone.backends import get_sms_backend
from apps.common.utils.phone_verification_services import send_security_code_and_generate_session_token, \
    get_otp_resend_time_remaining
from django.conf import settings
from rest_framework.exceptions import PermissionDenied


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    password2 = serializers.CharField(style={'input_type': 'password'},
                                      write_only=True)
    session_token = serializers.CharField(required=False)
    otp_resend_time = serializers.IntegerField(required=False)

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'name',
            'sex',
            'phone_number',
            'date_of_birth',
            'picture',
            'session_token',
            'otp_resend_time',
            'password',
            'password2'
        )
        read_only_fields = ['session_token']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8
            }
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""

        password = validated_data.get('password', None)
        confirm_password = validated_data.pop('password2', None)

        if password != confirm_password:
            msg = _('Passwords must match')
            raise serializers.ValidationError({'password': msg})

        user = get_user_model().objects.create_user(**validated_data)

        if password:
            user.set_password(password)
            user.save()

        # set default group
        try:
            group = Group.objects.get(name='User')
            user.groups.add(group)
            user.save()
        except Group.DoesNotExist:
            pass

        # send SMS verification code
        device_session_token = None
        if user.phone_number:
            try:
                device_session_token = send_security_code_and_generate_session_token(
                    user.phone_number, user
                )
            except:
                msg = _('Account verification SMS could not be sent')
                res = serializers.ValidationError({'detail': msg})
                res.status_code = 500
                raise res

            if device_session_token is None:
                msg = _('Account verification SMS could not be sent')
                res = serializers.ValidationError({'detail': msg})
                res.status_code = 500
                raise res

        attrs = {
            'user': {
                'name': user.name,
                'sex': user.sex,
                'phone_number': user.phone_number,
                'date_of_birth': user.date_of_birth,
            },
            'session_token': device_session_token,
            'otp_resend_time': settings.PHONE_VERIFICATION.get('OTP_RESEND_TIME', 300)
        }
        return attrs


class UpdateUserSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""

    class Meta:
        model = get_user_model()
        fields = (
            'name',
            'sex',
            'date_of_birth'
        )


class LoginSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""

    phone_number = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""

        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        sms_backend = get_sms_backend()

        user = authenticate(
            request=self.context.get('request'),
            username=phone_number,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError({'detail': msg})

        if not sms_backend.is_phone_number_verified(phone_number):
            # session_token = sms_backend.get_session_token(phone_number)
            msg = _('Please verify your phone.')
            otp_resend_time, session_token = get_otp_resend_time_remaining(user.phone_number)
            raise PermissionDenied({'detail': msg, 'phone_number': phone_number, 'session_token': session_token,
                                    'otp_resend_time': otp_resend_time})

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password"""

    password = serializers.CharField(required=True, style={'input_type': 'password'}, trim_whitespace=False,
                                     min_length=8)
    password2 = serializers.CharField(required=True, style={'input_type': 'password'}, trim_whitespace=False)
    old_password = serializers.CharField(required=True, style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password2": "Password fields didn't match."})

        return attrs
