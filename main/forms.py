from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError

from main.models import WebUser

class LoadDataForm(forms.Form):

    autocasion_pages = forms.IntegerField(label="Nº de páginas de Autocasion", min_value=0, max_value=100, initial=3, required=True)
    coches_com_pages = forms.IntegerField(label="Nº de páginas de coches.com", min_value=0, max_value=100, initial=3, required=True)
    motor_es_pages = forms.IntegerField(label="Nº de páginas de motor.es", min_value=0, max_value=100, initial=3, required=True)

class RegisterForm(UserCreationForm):
    
    email = forms.EmailField()

    class Meta:
        model = WebUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
            "password1",
            "password2",
        ]

class SearchTitleForm(forms.Form):

    title = forms.CharField(label="",
                            widget=forms.TextInput(
                                attrs={
                                    "placeholder": "Introduce el título del coche",
                                    "class": "form-control form-input"
                                }
                            ), 
                            max_length=100, 
                            required=False)

class RecommendationsForm(forms.Form):

    num_cars = forms.IntegerField(label="Nº de coches recomendados", min_value=0, max_value=100, initial=12, required=True)