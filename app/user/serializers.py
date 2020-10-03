from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group

from rest_framework import serializers

from common.utils.sms import send_sms_code


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
                'write_only': True
            }
        }

    def save(self, request):
        """Create a new user with encrypted password and return it"""

        password = self.validated_data.get('password', None)
        confirm_password = self.validated_data.pop('password2', None)

        if password != confirm_password:
            msg = _('Passwords must match')
            raise serializers.ValidationError({'password': msg})

        user = get_user_model().objects.create_user(**self.validated_data)

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

        send_sms_code(user)

        return user
