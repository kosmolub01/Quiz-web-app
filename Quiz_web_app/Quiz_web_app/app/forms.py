from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class QuizCreationForm(forms.Form):
    """title = forms.CharField(label="Wikipedia Article Title", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={
            'required': 'Wikipedia Article Title field is required.',
            'invalid': 'Enter a valid value for this field.',
            'max_length': 'The maximum length allowed is 255 characters.',
        })"""
    title = forms.CharField(label="Quiz Title", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={
            'required': 'Quiz Title field is required.',
            'invalid': 'Enter a valid value for this field.',
            'max_length': 'The maximum length allowed is 255 characters.',
        })
    description = forms.CharField(label="Description", max_length=350, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}), error_messages={
            'required': 'Description field is required.',
            'invalid': 'Enter a valid value for this field.',
            'max_length': 'The maximum length allowed is 350 characters.',
        })
    text = forms.CharField(label="Text To Generate Quiz", max_length=5000, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}), error_messages={
            'required': 'Text To Generate Quiz field is required.',
            'invalid': 'Enter a valid value for this field.',
            'max_length': 'The maximum length allowed is 5000 characters.',
        })
