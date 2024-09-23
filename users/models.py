from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from organizations.models import Organization
from sites.models import Site
from django.contrib.auth import get_user_model

MFA_CHOICES = [
    ('none', 'None'),
    ('google_authenticator', 'Google Authenticator'),
    ('sms', 'SMS'),
    ('email', 'Email'),
    ('static_otp', 'Static OTP'),
]

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    badge_barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    badge_rfid = models.CharField(max_length=100, unique=True, null=True, blank=True)
    organization = models.ForeignKey('Organization', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    site = models.ForeignKey('Site', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    mfa_preference = models.CharField(max_length=50, choices=MFA_CHOICES, default='none')
    mfa_secret = models.CharField(max_length=100, null=True, blank=True)  # For Google Authenticator
    static_otp = models.TextField(null=True, blank=True)  # Comma-separated static OTPs
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    # Tracking fields
    date_joined = models.DateTimeField(default=timezone.now)
    date_created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='created_users')
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='modified_users')


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email