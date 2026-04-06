from django.forms import ModelForm
from django import forms
from .models import * 


class ChatMessageChatForm(ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body']
        widgets = {
            'body': forms.TextInput(attrs={'placeholder': "New Message...", 'class': 'p-4 text-black', 'max-length': '300', 'autofocus': True}),   
        }