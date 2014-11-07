from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms

class UserForm(forms.Form):
    username = forms.CharField(label='Username', min_length=5)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
