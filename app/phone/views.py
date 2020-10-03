from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from common.utils.sms import send_sms_code
from .serializers import PhoneNumberSerializer
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


class VerifyPhone(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        sms_code = self.kwargs['sms_code']
        try:
            code = int(sms_code)
            if request.user.authenticate(code):
                phone = request.user.phonenumber
                phone.verified = True
                phone.save()
                return Response(dict(detail="Phone number verified "
                                            "successfully"),
                                status=201)
            return Response(
                dict(detail='The provided code did not match or has expired'),
                status=404)
        except ValueError:
            Response(dict(detail="Code should be integer"), status=400)
