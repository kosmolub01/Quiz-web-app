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
    title = forms.CharField(label="Wikipedia Article Title", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label="Description", max_length=350, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}))
