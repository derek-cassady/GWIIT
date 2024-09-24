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

class UserManager(models.Manager):
    # Returns all active users
    def active(self):
        return self.filter(is_active=True)

    # Returns all inactive users
    def inactive(self):
        return self.filter(is_active=False)
    
    # Returns users by first name
    def by_first_name(self, first_name):
        # Case-insensitive search
        return self.filter(first_name__icontains=first_name)
    
    # Returns users by last name
    def by_last_name(self, last_name):
        # Case-insensitive search
        return self.filter(last_name__icontains=last_name)
    
    # Returns users by both first and last name
    def by_full_name(self, first_name, last_name):
        # Case-insensitive search
        return self.filter(first_name__icontains=first_name, last_name__icontains=last_name)

    # Returns all users from site
    def from_site(self, site):
        return self.filter(site=site)

    # Returns all users from organization
    def from_organization(self, organization):
        return self.filter(organization=organization)

    # Returns all active users from site
    def active_from_site(self, site):
        return self.filter(is_active=True, site=site)

    # Returns all inactive users from site
    def inactive_from_site(self, site):
        return self.filter(is_active=False, site=site)

    # Returns all active users from organization
    def active_from_organization(self, organization):
        return self.filter(is_active=True, organization=organization)    

    # Returns all inactive users from organization
    def inactive_from_organization(self, organization):
        return self.filter(is_active=False, organization=organization) 
    
    # Users without MFA setup
    def without_mfa(self):
        return self.filter(mfa_preference='none')

    # Users using Google Authenticator MFA
    def with_google_authenticator(self):
        return self.filter(mfa_preference='google_authenticator')

    # Users using SMS MFA
    def with_sms(self):
        return self.filter(mfa_preference='sms')

    # Users using Email MFA
    def with_email_mfa(self):
        return self.filter(mfa_preference='email')

    # Users by 'badge_barcode'
    def by_badge_barcode(self, barcode):
        return self.filter(badge_barcode=barcode)

    # Users by 'badge_rfid'
    def by_badge_rfid(self, rfid):
        return self.filter(badge_rfid=rfid)
    
    # Returns all staff users
    def staff(self):
        return self.filter(is_staff=True)

    # Returns all staff users from site
    def staff_from_site(self, site):
        return self.filter(is_staff=True, site=site)
        
    # Returns all staff users from organization
    def staff_from_organization(self, organization):
        return self.filter(is_staff=True, organization=organization)

    # Returns all users created in last 30 days
    def recently_joined(self):
        last_30_days = timezone.now() - timezone.timedelta(days=30)
        return self.filter(date_joined__gte=last_30_days)

    # Returns all users created in last 30 days from site
    def recently_joined_from_site(self, site):
        last_30_days = timezone.now() - timezone.timedelta(days=30)
        return self.filter(date_joined__gte=last_30_days, site=site)     

    # Returns all users created in last 30 days from organization
    def recently_joined_from_organization(self, organization):
        last_30_days = timezone.now() - timezone.timedelta(days=30)
        return self.filter(date_joined__gte=last_30_days, organization=organization)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, db_index=True, verbose_name='Email Address')
    username = models.CharField(max_length=30, unique=True, null=True, blank=True, db_index=True, verbose_name='Username')
    first_name = models.CharField(max_length=30, null=True, blank=True, db_index=True, verbose_name='First Name')
    last_name = models.CharField(max_length=30, null=True, blank=True, db_index=True, verbose_name='Last Name')
    badge_barcode = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True, verbose_name='Badge Barcode')
    badge_rfid = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True, verbose_name='Badge RFID')
    organization = models.ForeignKey('Organization', on_delete=models.SET_NULL, null=True, blank=True, related_name='users', verbose_name='Organization Name')
    site = models.ForeignKey('Site', on_delete=models.SET_NULL, null=True, blank=True, related_name='users', verbose_name='Site Name')
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name='Phone Number')
    mfa_preference = models.CharField(max_length=50, choices=MFA_CHOICES, default='none', verbose_name='MFA Preference')
    mfa_secret = models.CharField(max_length=100, null=True, blank=True, verbose_name='MFA Secret')  # For Google Authenticator
    static_otp = models.TextField(null=True, blank=True, verbose_name='Static OTP')  # Comma-separated static OTPs
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    is_staff = models.BooleanField(default=False, verbose_name='Is Staff')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='Last Login')

    # Tracking fields
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Date Joined')
    date_created = models.DateTimeField(default=timezone.now, verbose_name='Date Created')
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='created_users', verbose_name='Created By')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Last Modified')
    modified_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='modified_users', verbose_name='Modified By')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['email', 'username', 'first_name', 'last_name', 'badge_barcode', 'badge_rfid']
        # Singular for 'User' model
        verbose_name = 'User'
        # Plural for 'User' model
        verbose_name_plural = 'Users'
        # Combined Indexing for faster queries
        indexes = [
            models.Index(fields=['email', 'username'], name='email_username_idx'),
            models.Index(fields=['first_name', 'last_name'], name='first_last_name_idx'),
            models.Index(fields=['username', 'first_name', 'last_name'], name='username_first_last_name_idx'),
        ]

    # Property for the full name
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        organization_name = self.organization.name if self.organization else 'No Organization'
        site_name = self.site.name if self.site else 'No Site'
        return f"{self.email} ({organization_name} - {site_name})"