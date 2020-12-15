from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group

from rest_framework import serializers

from common.utils.sms import send_sms_code
from phone.models import PhoneNumber


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    password2 = serializers.CharField(style={'input_type': 'password'},
                                      write_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'name',
            'sex',
            'phone',
            'date_of_birth',
            'picture',
            'password',
            'password2'
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8
            }
        }

    # def create(self, validated_data):
    #     """Create a new user with encrypted password and return it"""
    #
    #     password = validated_data.get('password', None)
    #     password2 = validated_data.pop('confirm_password', None)
    #
    #     if password != password2:
    #         msg = _('Passwords must match')
    #         raise serializers.ValidationError({'password': msg})
    #
    #     return get_user_model().objects.create_user(**validated_data)

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
        if user.phone:
            try:
                send_sms_code(user)
            except:
                msg = _('Account verification SMS could not be sent')
                res = serializers.ValidationError({'detail': msg})
                res.status_code = 500
                raise res

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""

    phone = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""

        phone = attrs.get('phone')
        password = attrs.get('password')

        has_verified_phone = PhoneNumber.objects.filter(number=phone,
                                                        verified=True).exists()

        user = authenticate(
            request=self.context.get('request'),
            username=phone,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError({'detail': msg})

        if not has_verified_phone:
            msg = _('Please verify your phone.')
            raise serializers.ValidationError({'detail': msg})

        attrs['user'] = user

        return attrs
