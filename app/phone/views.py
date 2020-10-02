from .serializers import PhoneNumberSerializer
from .models import PhoneNumber
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from common.utils.sms import send_sms_code


class PhoneViewset(viewsets.ModelViewSet):
    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        """Associate user with phone number"""

        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def send_sms(request, format=None):
    send_sms_code(request.user)
    return Response(status=200)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verify_phone(request, sms_code, format=None):
    code = int(sms_code)
    if request.user.authenticate(code):
        phone = request.user.phonenumber
        phone.verified = True
        phone.save()
        return Response(dict(detail="Phone number verified successfully"),
                        status=201)
    return Response(
        dict(detail='The provided code did not match or has expired'),
        status=200)
