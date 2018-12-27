from django import forms
from dappx.models import UserProfileInfo
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput()
    )
    username = forms.CharField()
    email = forms.CharField()

    class Meta():
        model = User
        fields = ('username', 'email', 'password',)


class UserProfileInfoForm(forms.ModelForm):

    class Meta():
        model = UserProfileInfo
        fields = ('phone',)
