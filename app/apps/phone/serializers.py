from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .models import PhoneNumber
from apps.user.models import User


class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = '__all__'


class VerifyOTPAndLoginSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""

    phone = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    sms_code = serializers.IntegerField()

    def validate(self, attrs):
        """Validate and authenticate the user"""

        phone_number = attrs.get('phone')
        password = attrs.get('password')
        code = attrs.get('sms_code')
        try:
            user = User.objects.get(phone=phone_number)
            if not user.check_password(password):
                msg = _("Unable to authenticate the user")
                raise serializers.ValidationError({'detail': msg})
        except User.DoesNotExist:
            msg = _("User doesn't exist")
            raise serializers.ValidationError({'detail': msg})

        if user.authenticate(code):
            phone = user.phonenumber
            phone.verified = True
            phone.save()

            user = authenticate(
                request=self.context.get('request'),
                username=phone_number,
                password=password
            )

            if not user:
                msg = _('Unable to authenticate with provided credentials')
                raise serializers.ValidationError({'detail': msg})
        else:
            msg = _("The provided code did not match or has expired")
            raise serializers.ValidationError({'detail': msg})

        attrs['user'] = user

        return attrs
