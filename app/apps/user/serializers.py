from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from rest_framework import serializers
from apps.phone.backends import get_sms_backend
from apps.common.utils.phone_verification_services import send_security_code_and_generate_session_token
from django.conf import settings


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    password2 = serializers.CharField(style={'input_type': 'password'},
                                      write_only=True)
    session_token = serializers.CharField(required=False)
    otp_expiration_time = serializers.IntegerField(required=False)

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
            'otp_expiration_time',
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
            'email': user.email,
            'name': user.name,
            'sex': user.sex,
            'phone_number': user.phone_number,
            'date_of_birth': user.date_of_birth,
            'picture': user.picture,
            'session_token': device_session_token,
            'otp_expiration_time': settings.PHONE_VERIFICATION.get('SECURITY_CODE_EXPIRATION_TIME', 300)
        }
        return attrs


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
            """
            TODO: 
             - check if the phone is is registered in the PhoneVerification model
             - if phone is registered
             -      check if it is expired
             -      if it is not expired resend the code
             -      if it is expired generate another and send it
             - If not, register the phone and  
            """
            msg = _('Please verify your phone.')
            raise serializers.ValidationError({'detail': msg})

        attrs['user'] = user

        return attrs
