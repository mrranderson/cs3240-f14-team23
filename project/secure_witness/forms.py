from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms

class UserForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(u'user_exists')

class BasicSearchForm(forms.Form):
    keywords = forms.CharField(label="Keywords", max_length=200)

class BulletinForm(forms.Form):
    title = forms.CharField(label='Title')
    description = forms.CharField(label = 'Description')
    location = forms.CharField(label = 'Location')
    pub_key = forms.CharField(required=False, label = 'Public Key')
    is_encrypted = forms.BooleanField(required=False, label = 'Encrypt Bulletin?')
    is_public = forms.BooleanField(required=False, label = 'Make Public?')
    is_searchable = forms.BooleanField(required=False, label = 'Make Searchable?')
    docfile = forms.FileField(label='Filefield')
