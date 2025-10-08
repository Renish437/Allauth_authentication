# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from datetime import date
import datetime
from .models import CustomProfiles


YEARS = range(1900, date.today().year + 1)

# Month names without dots
MONTHS = [(f"{i:02d}", month_name) for i, month_name in enumerate([
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
], start=1)]

# Days
DAYS = [(f"{i:02d}", str(i)) for i in range(1, 32)]



class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")
    phone = forms.CharField(max_length=30, label="Phone Number")

    day = forms.ChoiceField(choices=DAYS, required=True, widget=forms.Select(attrs={
        'x-ref': 'daySelect',
        'class': 'hidden'
    }))
    month = forms.ChoiceField(choices=MONTHS, required=True, widget=forms.Select(attrs={
        'x-ref': 'monthSelect',
        'class': 'hidden'
    }))
    year = forms.ChoiceField(choices=[(str(y), str(y)) for y in reversed(YEARS)], required=True, widget=forms.Select(attrs={
        'x-ref': 'yearSelect',
        'class': 'hidden'
    }))

    def save(self, request):
        user = super().save(request)
        user.phone = self.cleaned_data['phone']
        user.dob = f"{self.cleaned_data['year']}-{self.cleaned_data['month']}-{self.cleaned_data['day']}"
        user.save()
        return user
    
# forms.py
class ProfileForm(forms.ModelForm):
    day = forms.ChoiceField(choices=DAYS, required=False, widget=forms.Select(attrs={'hidden': True}))
    month = forms.ChoiceField(choices=MONTHS, required=False, widget=forms.Select(attrs={'hidden': True}))
    year = forms.ChoiceField(choices=[(str(y), str(y)) for y in reversed(YEARS)], required=False, widget=forms.Select(attrs={'hidden': True}))

    class Meta:
        model = CustomProfiles
        fields = ['username', 'email', 'phone', 'dob', 'day', 'month', 'year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.dob:
            self.fields['day'].initial = self.instance.dob.day
            self.fields['month'].initial = f"{self.instance.dob.month:02d}"
            self.fields['year'].initial = str(self.instance.dob.year)

    def clean(self):
        cleaned_data = super().clean()
        day = cleaned_data.get('day')
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')
        if day and month and year:
            cleaned_data['dob'] = f"{year}-{month}-{day}"  # YYYY-MM-DD
        return cleaned_data
