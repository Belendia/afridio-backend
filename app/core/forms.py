from allauth.account.forms import SignupForm
from django import forms
from .models import User


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(max_length=100)
        self.fields['date_of_birth'] = forms.DateField(required=True)
        self.fields['sex'] = forms.ChoiceField(
            widget=forms.RadioSelect, choices=User.Sex.choices()
        )
