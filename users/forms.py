from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User
from django.core.exceptions import ValidationError
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Enter a secure password."
    )

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'badge_barcode', 'badge_rfid',
            'organization', 'site', 'phone_number', 'mfa_preference', 'mfa_secret', 'password'
        )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)  # Enforce password validation
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Securely hash password
        if commit:
            user.save()
        return user


class CustomSuperUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Enter a secure password for the superuser."
    )

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password'
        )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)  # Enforce password validation
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Securely hash password
        user.is_staff = True  # Ensure superuser properties
        user.is_superuser = True
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank to keep the current password."
    )

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'badge_barcode', 'badge_rfid',
            'organization', 'site', 'phone_number', 'mfa_preference', 'mfa_secret', 'is_active', 'is_staff', 'password'
        )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password)  # Enforce all password validation rules
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])  # Securely hash password
        if commit:
            user.save()
        return user


class CustomSuperUserChangeForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="Leave blank to keep the current password."
    )

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'password'
        )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password)  # Enforce all password validation rules
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["password"]:
            user.set_password(self.cleaned_data["password"])  # Securely hash password
        if commit:
            user.save()
        return user
