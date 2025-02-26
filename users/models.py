from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from .managers import UserManager
from django.apps import apps
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

"""
Custom User Model for Multi-Database Setup

This class defines the `User` model, which is designed to support multi-database
    environments where relationships between different apps (Users, Organizations, Sites)
    must be managed manually. 

Key Features:
    - Uses email as the primary authentication field.
    - Supports multiple login identifiers (`username`, `badge_barcode`, `badge_rfid`).
    - Implements manual foreign key handling (`organization_id`, `site_id`, `created_by_id`, `modified_by_id`).
    - Supports Multi-Factor Authentication (MFA) preferences.
    - Includes tracking fields for audit purposes (`date_created`, `created_by_id`, `last_modified`, `modified_by_id`).
    
Manual Foreign Key Handling:
    - `organization_id`: Stores the ID of an organization, instead of using a direct ForeignKey.
    - `site_id`: Stores the ID of a site, instead of using a direct ForeignKey.
    - `created_by_id` & `modified_by_id`: Track which user created or modified this user.

Why Manual Foreign Keys?
    - Django does not natively support ForeignKey relations across multiple databases.
    - Instead of direct relations, ID fields are used and related objects are fetched manually.
    - Getter methods (`get_organization()`, `get_site()`, etc.) are provided to retrieve related objects.

Authentication and User Management:
    - `USERNAME_FIELD = 'email'` ensures authentication is done via email.
    - The `UserManager` handles user creation, ensuring valid login identifiers.
"""

class User(AbstractBaseUser):
    MFA_CHOICES = [
        ('none', _('None')),
        ('google_authenticator', _('Google Authenticator')),
        ('sms', _('SMS')),
        ('email', _('Email')),
        ('static_otp', _('Static OTP')),
    ]

    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True, blank=False, null=False, db_index=True, verbose_name=_('Email Address'))
    username = models.CharField(max_length=30, unique=True, null=True, blank=True, db_index=True, verbose_name=_('Username'))
    password = models.CharField(max_length=128, verbose_name=_("Password"))
    first_name = models.CharField(max_length=30, null=True, blank=True, db_index=True, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=30, null=True, blank=True, db_index=True, verbose_name=_('Last Name'))
    badge_barcode = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True, verbose_name=_('Badge Barcode'))
    badge_rfid = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True, verbose_name=_('Badge RFID'))
    
    # Store IDs for manual foreign key handling
    organization_id = models.IntegerField(null=True, blank=True, verbose_name=_('Organization ID'))
    site_id = models.IntegerField(null=True, blank=True, verbose_name=_('Site ID'))
    
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name=_('Phone Number'))
    mfa_preference = models.CharField(max_length=50, choices=MFA_CHOICES, default='none', verbose_name=_('MFA Preference'))
    mfa_secret = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('MFA Secret'))
    static_otp = models.TextField(null=True, blank=True, verbose_name=_('Static OTP'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    is_superuser = models.BooleanField(default=False, verbose_name=_('Is Superuser'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Is Staff'))
    last_login = models.DateTimeField(null=True, blank=True, verbose_name=_('Last Login'))

    # Tracking fields
    date_joined = models.DateTimeField(default=now, verbose_name=_('Date Joined'))
    date_created = models.DateTimeField(default=now, verbose_name=_('Date Created'))
    created_by_id = models.IntegerField(null=True, blank=True, verbose_name=_('Created By ID'))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last Modified'))
    modified_by_id = models.IntegerField(null=True, blank=True, verbose_name=_('Modified By ID'))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    """
    Metadata options for the model:

        - app_label: Explicitly associates the model with its Django app.
        - verbose_name: Human-readable singular name for the model.
        - verbose_name_plural: Human-readable plural name for the model.
        - ordering: Defines the default ordering of query results. If not present, consider adding an appropriate default.

    Notes:
        - app_label is required for multi-database setups to ensure correct app referencing.
        - ordering improves query efficiency by specifying a default sort order.
        - verbose_name settings enhance readability in admin and UI interfaces.
    """

    class Meta:
        app_label = "users"
        ordering = ['email', 'username', 'first_name', 'last_name', 'badge_barcode', 'badge_rfid']
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    """
    Computed Property: Full Name
        - Returns the full name of the user by combining `first_name` and `last_name`.
        - If either field is missing, it gracefully returns the available name component.
        - Ensures consistent formatting for display purposes.
    """

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    """
    String Representation of the User Model
        - Provides a human-readable representation of the user object.
        - Dynamically retrieves the related organization and site names using manual foreign key lookups.
        - Ensures that user information remains informative even in a multi-database setup.
        - Returns the user’s email along with their associated organization and site names.
    """

    def __str__(self):
        organization = self.get_organization()
        site = self.get_site()

        organization_name = organization.name if organization else _('No Organization')
        site_name = site.name if site else _('No Site')

        return f"{self.email} ({organization_name} - {site_name})"
    
    """
    Manual Foreign Key Lookup Methods

    Since Django does not natively support cross-database foreign key relations,
        these methods manually retrieve related objects from their respective databases.

    Why These Methods Are Inside the `User` Model:
        - They operate at the instance level, retrieving related records dynamically.
        - They provide a way to access related objects without an actual ForeignKey.
        - Unlike `UserManager`, which handles QuerySet-level operations, these methods
          return a single related object or `None`.
        - **Uses `apps.get_model()`** to ensure dynamic and reliable model resolution
          across different apps.

    Usage Example:
        user = User.objects.using("users_db").get(id=1)
        organization = user.get_organization()  # Fetch organization manually
    """

    def get_organization(self):
        if self.organization_id:
            Organization = apps.get_model("organizations", "Organization")
            return Organization.objects.using("organizations_db").filter(id=self.organization_id).first()
        return None

    def get_site(self):
        if self.site_id:
            Site = apps.get_model("sites", "Site")
            return Site.objects.using("sites_db").filter(id=self.site_id).first()
        return None

    def get_created_by(self):
        if self.created_by_id:
            User = apps.get_model("users", "User")
            return User.objects.using("users_db").filter(id=self.created_by_id).first()
        return None

    def get_modified_by(self):
        if self.modified_by_id:
            User = apps.get_model("users", "User")
            return User.objects.using("users_db").filter(id=self.modified_by_id).first()
        return None