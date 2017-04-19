from django import forms
from django.contrib.auth.models import User

from .models import Department

class NewUserTicket(forms.Form):
    username = forms.CharField(label='Username', max_length=32)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    firstname = forms.CharField(label='First Name', max_length=32, required=False)
    lastname = forms.CharField(label='Last Name', max_length=32, required=False)
    address = forms.CharField(max_length=256, required=False)
    city = forms.CharField(max_length=128, required=False)
    state = forms.CharField(max_length=128, required=False)
    postal_code = forms.CharField(max_length=16, required=False)
    phone = forms.CharField(max_length=16, required=False)
    department = forms.ModelChoiceField(Department.objects.all())

    # form validator to ensure unique username
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(u'Username "{}" is already in use.'.format(username))


class UserSearchForm(forms.Form):
    username = forms.CharField(label='Username', max_length=32, required=False)
    first_name = forms.CharField(label='First Name', max_length=32, required=False)
    last_name = forms.CharField(label='Last Name', max_length=32, required=False)

    def get_users(self):
        users = User.objects
        is_filtered = False
        for f in ['first_name', 'last_name', 'username']:
            if self.cleaned_data[f]:
                is_filtered = True
                users = users.filter(**{
                    f+'__icontains': self.cleaned_data[f]
                })
        if is_filtered:
            return users
        return []