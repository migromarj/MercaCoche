from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError

from main.models import WebUser

class RegisterForm(UserCreationForm):
    
    email = forms.EmailField()

    class Meta:
        model = WebUser
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        ]