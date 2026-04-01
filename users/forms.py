from django.forms import ModelForm
from django import forms
from .models import *


# For the edit Profile page 
class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']
        widgets = {
            'image': forms.FileInput(),
            'displayname' : forms.TextInput(attrs={'placeholder': 'Enter your Alias'}),
            'info': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Whats the Topic of the Day?'})
        }