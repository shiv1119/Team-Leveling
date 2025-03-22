from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth.models import User
import re

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )
    password2 = forms.CharField(
        label="Confirm Password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            "email": forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if User.objects.filter(username=username).exists():
            self.add_error("username", "Username is already taken.")
    
        if User.objects.filter(email=email).exists():
            self.add_error("email", "Email is already registered.")

        if password1 and password2:
            if password1 != password2:
                self.add_error("password2", "Passwords do not match.")
            if len(password1) < 6:
                self.add_error("password1", "Password must be at least 6 characters long.")
            if not re.search(r"[A-Z]", password1):
                self.add_error("password1", "Password must contain at least one uppercase letter.")
            if not re.search(r"\d", password1):
                self.add_error("password1", "Password must contain at least one number.")
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password1):
                self.add_error("password1", "Password must contain at least one special character.")

        return cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone', 'date_of_birth', 'gender', 'address', 'city', 'state', 'zip_code', 'country', 'profile_photo']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter phone number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control dark-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select dark-input'}),
            'address': forms.Textarea(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter address', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter city'}),
            'state': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter state'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter zip code'}),
            'country': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter country'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control dark-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone', 'date_of_birth', 'gender', 'address', 'city', 'state', 'zip_code', 'country', 'profile_photo']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter phone number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control dark-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select dark-input'}),
            'address': forms.Textarea(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter address', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter city'}),
            'state': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter state'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter zip code'}),
            'country': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Enter country'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True

class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Your Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Your Phone (Optional)'}),
            'subject': forms.TextInput(attrs={'class': 'form-control dark-input', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control dark-input', 'placeholder': 'Your Message', 'rows': 4}),
        }

class NotificationPreferencesForm(forms.ModelForm):
    class Meta:
        model = NotificationPreferences
        fields = ['email_notifications', 'sms_notifications', 'push_notifications', 'in_app_notification']


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']