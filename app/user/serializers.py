from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    confirm_password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True
    )

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'password',
            'confirm_password',
            'name',
            'sex',
            'phone',
            'date_of_birth',
            'picture'
        )
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""

        password = validated_data.get('password', None)
        confirm_password = validated_data.pop('confirm_password', None)

        if password != confirm_password:
            msg = _('Passwords must match')
            raise serializers.ValidationError({'password': msg})

        user = get_user_model().objects.create_user(**validated_data)
        # set default group
        try:
            group = Group.objects.get(name='User')
            user.groups.add(group)
            user.save()
        except Group.DoesNotExist:
            pass

        return user

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""

        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""

    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""

        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user

        return attrs
