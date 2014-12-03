from django.contrib import admin
from django import forms
from secure_witness.models import Folder, Bulletin
from django.contrib.auth.models import User

class BulForm(forms.ModelForm):
    class Meta:
        model=Bulletin
        fields=()
class BulletinAdmin(admin.ModelAdmin):
    form=BulForm

admin.site.register(Bulletin, BulletinAdmin)

class FolForm(forms.ModelForm):
    class Meta:
        model=Folder
        fields=()
class FolderAdmin(admin.ModelAdmin):
    form=FolForm

class UForm(forms.ModelForm):
    class Meta:
        model=User
        fields=()
class UserAdmin(admin.ModelAdmin):
    form=UForm

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register your models here.
