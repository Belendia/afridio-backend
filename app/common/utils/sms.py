import pyotp
from twilio.rest import Client as TwilioClient
from decouple import config
from django.conf import settings

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
twilio_phone = settings.TWILIO_PHONE

client = TwilioClient(account_sid, auth_token)


def send_sms_code(user):
    # Time based otp
    time_otp = pyotp.TOTP(user.slug, interval=300)
    time_otp = time_otp.now()
    user_phone_number = user.phonenumber.number  # Must start with a plus '+'
    client.messages.create(
        body="Your verification code is " + time_otp,
        from_=twilio_phone,
        to=user_phone_number
    )
