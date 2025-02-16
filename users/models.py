print("DEBUG: Starting to load models for users app...")

from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from passlib.pwd import genword
import importlib.resources
import random
import string

MFA_CHOICES = [
    ('none', _('None')),
    ('google_authenticator', _('Google Authenticator')),
    ('sms', _('SMS')),
    ('email', _('Email')),
    ('static_otp', _('Static OTP')),
]

"""
Custom manager for User model that provides helper methods
to create regular users and superusers.
"""

class UserManager(models.Manager):

    # manually normalizes email if not caught by front end checks
    def normalize_email(self, email):
        """Manually normalize email if BaseUserManager is not used."""
        return email.lower().strip() if email else None

    # uses passlib to genereate a strong password.
    # generates password to meet all validator requirements.
    def generate_secure_password(self, length=16):
        
        max_attempts = 10  # Prevents infinite loop
        
        for _ in range(max_attempts):
            password = genword(length=length)  # Generate password

            # Check if password meets all rules
            if (
                any(c.isupper() for c in password) and
                any(c.islower() for c in password) and
                any(c.isdigit() for c in password) and
                any(c in string.punctuation for c in password)
            ):
                return password
        raise ValueError("Failed to generate a secure password after multiple attempts.")

    """
    Creates and returns a regular user. 
    Supports login via email, username, badge barcode, or badge RFID.
    Password is randomly generated.
    """

    def create_user(self, email, password=None, **extra_fields):
        
        username = extra_fields.get("username")
        badge_barcode = extra_fields.get("badge_barcode")
        badge_rfid = extra_fields.get("badge_rfid")
        
        # Ensure at least one login method is provided, with email required
        if not email:
            raise ValueError("The Email field must be set.")
        if not any([username, badge_barcode, badge_rfid]):
            raise ValueError("At least one additional login identifier (username, badge) must be set.")

        # Normalize email if provided
        if email:
            extra_fields["email"] = self.normalize_email(email)

        # Generate a secure password
        password = self.generate_secure_password()

        user = self.model(**extra_fields)
        # Django will hash the password when handing to DB
        user.set_password(password)
        user.save(using=self._db)

        # Send credentials via email (DJango console mail for development)
        send_mail(
            subject="Your Account Credentials",
            message=f"Your account has been created.\nEmail: {user.email}\nTemporary Password: {password}",
            # Placeholder; update later for production
            from_email="noreply@example.com",
            recipient_list=[user.email],
            # Prevents errors if email backend isn't configured
            fail_silently=True,
        )
        return user
    
    """
    Creates and returns a superuser. 
    Supports login via email, username, badge barcode, or badge RFID.
    The password is always randomly generated.
    """
    def create_superuser(self, email, **extra_fields):
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True or extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_staff=True and is_superuser=True.")

        return self.create_user(email, **extra_fields)
    
    """
    Allows users to log in using email, username, badge barcode, or badge RFID,
    but ignores inactive users.
    """
        
    def get_by_natural_key(self, identifier):

        return self.get(
            models.Q(is_active=True) & (
                models.Q(email__iexact=identifier) |
                models.Q(username__iexact=identifier) |
                models.Q(badge_barcode__iexact=identifier) |
                models.Q(badge_rfid__iexact=identifier)
            )
        )
    
    """
    - Set of query methods to filter users based on:
    - Active/inactive status.
    - Name (first, last, full name).
    - Organization and site associations.
    - Multi-factor authentication (MFA) preferences.
    - Badge-based identification.
    - Staff users and recently joined users.
    
    methods allow for flexible querying in both Django admin and applogic.
    """

    # returns users filtered by email
    def by_email(self, email):
        return self.filter(email=email)

    # returns users filtered by username.
    def by_username(self, username):
        return self.filter(username=username)

    # returns users filtered by badge barcode.
    def by_badge_barcode(self, barcode):
        return self.filter(badge_barcode=barcode)

    # returns users filtered by badge RFID.
    def by_badge_rfid(self, rfid):
        return self.filter(badge_rfid=rfid)
    
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

class User(AbstractBaseUser):
    email = models.EmailField(unique=True, blank=False, null=False, db_index=True, verbose_name=_('Email Address'))
    username = models.CharField(max_length=30, unique=True, null=True, blank=True, db_index=True, verbose_name=_('Username'))
    first_name = models.CharField(max_length=30, null=True, blank=True, db_index=True, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=30, null=True, blank=True, db_index=True, verbose_name=_('Last Name'))
    badge_barcode = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True, verbose_name=_('Badge Barcode'))
    badge_rfid = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True, verbose_name=_('Badge RFID'))
    organization = models.ForeignKey('organizations.Organization', on_delete=models.SET_NULL, null=True, blank=True, related_name='users', verbose_name=_('Organization Name'))
    site = models.ForeignKey('sites.Site', on_delete=models.SET_NULL, null=True, blank=True, related_name='users', verbose_name=_('Site Name'))
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Phone Number'))
    mfa_preference = models.CharField(max_length=50, choices=MFA_CHOICES, default='none', verbose_name=_('MFA Preference'))
    mfa_secret = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('MFA Secret'))  # For Google Authenticator
    static_otp = models.TextField(null=True, blank=True, verbose_name=_('Static OTP'))  # Comma-separated static OTPs
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Is Staff'))
    last_login = models.DateTimeField(null=True, blank=True, verbose_name=_('Last Login'))

    # Tracking fields
    date_joined = models.DateTimeField(default=timezone.now, verbose_name=_('Date Joined'))
    date_created = models.DateTimeField(default=timezone.now, verbose_name=_('Date Created'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='created_users', verbose_name=_('Created By'))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last Modified'))
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='modified_users', verbose_name=_('Modified By'))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ['email', 'username', 'first_name', 'last_name', 'badge_barcode', 'badge_rfid']
        # Singular for 'User' model
        verbose_name = _('User')
        # Plural for 'User' model
        verbose_name_plural = _('Users')
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
        organization_name = self.organization.name if self.organization else _('No Organization')
        site_name = self.site.name if self.site else _('No Site')
        return f"{self.email} ({organization_name} - {site_name})"
    
print("DEBUG: Finished loading models for users app.")