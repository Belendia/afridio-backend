from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.models import Group


class AccountAdapter(DefaultAccountAdapter):

    # disable allauth user signup
    def is_open_for_signup(self, request):
        return False

    def save_user(self, request, user, form, commit=True):
        """
        This is called when saving user via allauth registration.
        We override this to set additional data on user object.
        """
        # Do not persist the user yet so we pass commit=False
        # (last argument)
        user = super(AccountAdapter, self).save_user(request, user, form,
                                                     commit=False)
        user.name = form.cleaned_data.get('name')
        user.sex = form.cleaned_data.get('sex')
        user.date_of_birth = form.cleaned_data.get('date_of_birth')
        user.phone = form.cleaned_data.get('phone')

        user.save()

        # Add user role to the current user
        group = Group.objects.get(name='User')
        user.groups.add(group)
        user.save()
