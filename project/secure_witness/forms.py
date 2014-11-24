from django.contrib.auth.models import User
from django.forms import ModelForm
from django import forms
from secure_witness.models import Folder

class UserForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    public_key_loc = forms.CharField(max_length=200, label='Public Key Location')
    private_key_loc = forms.CharField(max_length=200, label='Private Key Location')  
 
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
    #pub_key = forms.CharField(required=False, label = 'Public Key')
    is_encrypted = forms.BooleanField(required=False, label = 'Encrypt Bulletin?')
    is_public = forms.BooleanField(required=False, label = 'Make Public?')
    is_searchable = forms.BooleanField(required=False, label = 'Make Searchable?')
    docfile = forms.FileField(required=False, label='Filefield')
    folder = forms.ModelChoiceField(queryset=Folder.objects.all(), label='Parent Folder', empty_label='No parent folder.', required=False)

class FolderForm(forms.Form):
    title = forms.CharField(label='Title')
    parent_folder = forms.ModelChoiceField(queryset=Folder.objects.all(), label='Parent Folder', empty_label='No parent folder.', required=False)
    
class UserEditForm(forms.Form):
    current_password = forms.CharField(required=False, label='Current Password')
    new_password = forms.CharField(required=False, label='New Password')
    confirm_new_password = forms.CharField(required=False, label='Confirm New Password')
    public_key_loc = forms.CharField(required=False, max_length=200, label='Change Public Key Location')
    private_key_loc = forms.CharField(required=False, max_length=200, label='Change Private Key Location')

class UserDeleteForm(forms.Form):
    keep_data = forms.BooleanField(required=False, label='I confirm I would like to delete my Account')
