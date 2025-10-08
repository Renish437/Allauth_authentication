# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from datetime import date
import datetime


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
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']