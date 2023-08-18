from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *


class UserRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

        # Loop through all fields and set help_text to an empty string
        for field_name, field in self.fields.items():
            field.help_text = ""

    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))

    class Meta:
        model = AppUser
        fields = ('username', 'email', 'date_of_birth', 'password1', 'password2')


TIME_CHOICES = [
    ('08:00-09:00', '08:00-09:00'),
    ('09:00-10:00', '09:00-10:00'),
    ('10:00-11:00', '10:00-11:00'),
    ('08:00-09:00', '08:00-09:00'),
    ('13:00-14:00', '13:00-14:00'),
    ('14:00-15:00', '14:00-15:00'),
    ('15:00-16:00', '15:00-16:00'),
    ('16:00-17:00', '16:00-17:00'),
    ('17:00-18:00', '17:00-18:00'),
]

GENRE_CHOICES = [
    ('fiction', 'Fiction'),
    ('non-fiction', 'Non-Fiction'),
    ('mystery', 'Mystery'),
    ('romance', 'Romance'),
]


class PredictionDataForm(forms.Form):
    time = forms.ChoiceField(choices=TIME_CHOICES, label='Time Slot')
    genre = forms.ChoiceField(choices=GENRE_CHOICES)
    price = forms.DecimalField(min_value=0, label='Price ($)')
    pages = forms.IntegerField(min_value=0, label='Pages')


class DataGenerationParamsForm(forms.ModelForm):
    class Meta:
        model = DataGenerationParams
        fields = ['time_mean', 'time_std', 'price_mean', 'price_std', 'pages_mean', 'pages_std', 'num_records']
        widgets = {
            'num_records': forms.NumberInput(attrs={'min': 100, 'max': 1000}),
        }