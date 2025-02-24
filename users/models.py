print("DEBUG: Starting to load models for users app...")

from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from organizations.models import Organization
from sites.models import Site
from django.utils.timezone import now, timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
# from passlib.pwd import genword
# import importlib.resources
import random
import string
import secrets
import re

"""
    Custom Manager for the User Model

    Provides methods for creating, updating, deleting, and querying users,
    while supporting manual foreign key handling due to multi-database constraints.

    **Create, Update & Deletion Methods:**
        - `create_user(email, password=None, **extra_fields)`: Creates a new user while manually handling foreign keys.
        - `create_superuser(email, username, password=None, **extra_fields)`: Creates a superuser with full admin access.
        - `update_user(user_id, **updated_fields)`: Updates an existing user with the provided field values.
        - `delete_user(user_id)`: Deletes a user with verification.

    **Query Methods:**
        - `by_email(email)`: Retrieves a user by email.
        - `by_username(username)`: Retrieves a user by username.
        - `by_badge_barcode(barcode)`: Retrieves a user by badge barcode.
        - `by_badge_rfid(rfid)`: Retrieves a user by badge RFID.
        - `active()`: Retrieves all active users.
        - `inactive()`: Retrieves all inactive users.
        - `by_first_name(first_name)`: Retrieves users by first name (case-insensitive).
        - `by_last_name(last_name)`: Retrieves users by last name (case-insensitive).
        - `by_full_name(first_name, last_name)`: Retrieves users by full name.
        - `from_site(site_id)`: Retrieves users belonging to a specific site.
        - `from_organization(organization_id)`: Retrieves users belonging to a specific organization.
        - `active_from_site(site_id)`: Retrieves active users from a specific site.
        - `inactive_from_site(site_id)`: Retrieves inactive users from a specific site.
        - `active_from_organization(organization_id)`: Retrieves active users from a specific organization.
        - `inactive_from_organization(organization_id)`: Retrieves inactive users from a specific organization.
        - `without_mfa()`: Retrieves users who do not have MFA enabled.
        - `with_google_authenticator()`: Retrieves users using Google Authenticator for MFA.
        - `with_sms()`: Retrieves users using SMS for MFA.
        - `with_email_mfa()`: Retrieves users using Email for MFA.
        - `staff()`: Retrieves all staff users.
        - `staff_from_site(site_id)`: Retrieves staff users from a specific site.
        - `staff_from_organization(organization_id)`: Retrieves staff users from a specific organization.
        - `recently_joined(days=30)`: Retrieves users who joined within the last `X` days.
        - `recently_joined_from_site(site_id, days=30)`: Retrieves users who joined within the last `X` days from a specific site.
        - `recently_joined_from_organization(organization_id, days=30)`: Retrieves users who joined within the last `X` days from a specific organization.

    **Why Manual Foreign Keys?**
        - Django does not support cross-database foreign key relations.
        - Integer fields (`organization_id`, `site_id`, `created_by_id`, `modified_by_id`) are used instead of actual ForeignKey fields.
        - Query methods work by filtering based on these integer IDs.

    **Usage Example:**
        - `active_users = User.objects.active()`
        - `staff_at_site = User.objects.staff_from_site(site_id=2)`
        - `new_users = User.objects.recently_joined(days=15)`
"""

class UserManager(models.Manager):

    """
    Manually normalizes and validates email addresses.
        - Converts all characters to lowercase.
        - Strips leading and trailing whitespace.
        - Ensures the email contains a valid format (e.g., "user@example.com").
        - Prevents potential authentication mismatches due to case sensitivity.

    Args:
        email (str): The email address to normalize and validate.
    
    Raises:
        ValueError: If the email is invalid.
    """

    # manually normalizes email if not caught by front end checks
    def normalize_email(self, email):
        if not email:
            # Allow None values ("None handled module creat_user)
            return None
    
        email = email.lower().strip()

        r""" Regex for basic email validation
            Ensures email format follows standard structure:
            - Starts with alphanumeric characters, underscores, dots, plus, or hyphens.
                - ^[a-zA-Z0-9_.+-]+
            - Contains exactly one "@" symbol separating the local part and domain, but allows for subdomains (e.g., "user@mail.example.com").
                - @
            - Domain must contain at least one dot (".") to indicate a valid TLD.
                - \.
            - Ends with valid TLD (e.g., .com, .co.uk)
                - [a-zA-Z0-9-.]+$
            - Prevents spaces, special characters like "!", "#", "$", etc., outside of allowed ones.
        """
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, email):
            raise ValueError(f"Invalid email format: {email}")

        return email


    # uses passlib to genereate a strong password.
    # generates password to meet all validator requirements.
    # def generate_secure_password(self, length=16):
        
    #     max_attempts = 10  # Prevents infinite loop
        
    #     for _ in range(max_attempts):
    #         password = genword(length=length)  # Generate password

    #         # Check if password meets all rules
    #         if (
    #             any(c.isupper() for c in password) and
    #             any(c.islower() for c in password) and
    #             any(c.isdigit() for c in password) and
    #             any(c in string.punctuation for c in password)
    #         ):
    #             return password
    #     raise ValueError("Failed to generate a secure password after multiple attempts.")


    """
    Generates a secure random password meeting the following complexity requirements:
        - At least one uppercase letter (A-Z)
        - At least one lowercase letter (a-z)
        - At least one digit (0-9)
        - At least one special character (!@#$%^&* etc.)
        - Ensures password length is at least 4 to satisfy these constraints
        - Uses `secrets.choice()` for better cryptographic randomness

    Args:
        length (int): Desired password length (default: 16)
    """
    def generate_secure_password(self, length=16):
        if length < 16:
            raise ValueError("Password length must be at least 16 characters to comply with security policies.")

        # Required character sets:

        # Ensures at least one uppercase
        uppercase = secrets.choice(string.ascii_uppercase)
        
        # Ensures at least one lowercase
        lowercase = secrets.choice(string.ascii_lowercase)
        
        # Ensures at least one digit
        digit = secrets.choice(string.digits)
        
        # Ensures at least one special character
        special = secrets.choice(string.punctuation)

        # Remaining random characters
        remaining_length = length - 4
        all_characters = string.ascii_letters + string.digits + string.punctuation
        random_chars = [secrets.choice(all_characters) for _ in range(remaining_length)]

        # Combine all characters and shuffle
        password_list = [uppercase, lowercase, digit, special] + random_chars
        random.shuffle(password_list)

        return ''.join(password_list)
    
    """
    Creates a new user while manually managing foreign key IDs.

    Handles Manual Foreign Key Assignments:
        - `organization_id` and `site_id` are extracted as integers (not objects).
        - `created_by_id` and `modified_by_id` are stored as IDs.

    Additional Features:
        - Normalizes email and ensures login methods are valid.
        - Generates a secure password and hashes it before saving.
        - Ensures the user is stored in the `users_db` database.

    Sends Credentials via Email (Console Mail for Development).
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

        # Normalize email
        extra_fields["email"] = self.normalize_email(email)

        # Extract manually managed foreign key IDs
        organization_id = extra_fields.pop("organization_id", None)
        site_id = extra_fields.pop("site_id", None)
        created_by_id = extra_fields.pop("created_by_id", None)
        modified_by_id = extra_fields.pop("modified_by_id", None)

        # Generate a secure password
        password = self.generate_secure_password()

        # Create the user instance
        user = self.model(**extra_fields)
        user.set_password(password)  # Hash the password

        # Assign manually managed foreign key IDs
        user.organization_id = organization_id
        user.site_id = site_id
        user.created_by_id = created_by_id
        user.modified_by_id = modified_by_id

        # Ensure the user is saved in the correct database
        user.save(using="users_db")

        # Send credentials via email (Django console mail for development)
        send_mail(
            subject="Your Account Credentials",
            message=f"Your account has been created.\nEmail: {user.email}\nTemporary Password: {password}",
            from_email="noreply@example.com",
            recipient_list=[user.email],
            fail_silently=True,
        )
        return user
    
    """
    Updates an existing user while manually managing foreign key IDs.

    **Manual Foreign Key Assignments:**
        - `organization_id` and `site_id` are stored as integers (not objects).
        - `modified_by_id` is updated to track the user performing the modification.

    **Additional Features:**
        - Normalizes the email before saving (if changed).
        - Ensures that login identifiers (`username`, `badge_barcode`, `badge_rfid`) remain valid.
        - Allows selective updates by only modifying provided fields.
        - Ensures the user is saved in the `users_db` database.

    **Usage Example:**
        - `User.objects.update_user(user_id=5, modified_by_id=2, username="new_name")`
    """
    def update_user(self, user_id, **updated_fields):
        try:
            # Retrieve the user instance from the correct database
            user = self.get_queryset().using("users_db").get(id=user_id)

            # Extract manually managed foreign key IDs
            organization_id = updated_fields.pop("organization_id", None)
            site_id = updated_fields.pop("site_id", None)
            modified_by_id = updated_fields.pop("modified_by_id", None)

            # Normalize email if provided
            if "email" in updated_fields:
                updated_fields["email"] = self.normalize_email(updated_fields["email"])

            # Ensure login identifiers remain valid
            if not any([
                updated_fields.get("username", user.username),
                updated_fields.get("badge_barcode", user.badge_barcode),
                updated_fields.get("badge_rfid", user.badge_rfid)
            ]):
                raise ValueError("At least one login identifier (username, badge) must remain set.")

            # Assign manually managed foreign key IDs
            if organization_id is not None:
                user.organization_id = organization_id
            if site_id is not None:
                user.site_id = site_id
            if modified_by_id is not None:
                user.modified_by_id = modified_by_id

            # Update the user fields with provided values
            for field, value in updated_fields.items():
                setattr(user, field, value)

            # Save changes to the correct database
            user.save(using="users_db")
            return user

        except self.model.DoesNotExist:
            raise ValueError(f"User with ID {user_id} does not exist.")

    """
        Deletes a user from the users_db.

        **Usage Example:**
            - `User.objects.delete_user(user_id=3)`

        **Handles:**
            - Ensuring the user exists before deletion.
            - Preventing accidental deletion of superusers.
            - Removing the user only from `users_db`.

        Raises:
            - `ValueError` if the user does not exist.
            - `ValueError` if trying to delete a superuser.
    """
    def delete_user(self, user_id):
        try:
            # Retrieve the user instance
            user = self.get_queryset().using("users_db").get(id=user_id)

            # Prevent accidental deletion of superusers
            if user.is_superuser:
                raise ValueError("Cannot delete a superuser using this method. Use `delete_superuser()` instead.")

            # Delete the user
            user.delete(using="users_db")
            return f"User with ID {user_id} deleted successfully."

        except self.model.DoesNotExist:
            raise ValueError(f"User with ID {user_id} does not exist.")

    """
    Creates and returns a superuser with full administrative access.

    Superuser Creation Rules:
        - Automatically sets `is_staff=True` and `is_superuser=True`.
        - Ensures only valid superusers are created.
        - Uses `create_user()` to apply additional password security.

    Raises:
    - `ValueError` if `is_staff` or `is_superuser` are not explicitly set to `True`.
    """

    def create_superuser(self, email, username, password=None, **extra_fields):
    
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True or extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_staff=True and is_superuser=True.")

        return self.create_user(email=email, username=username, password=password, **extra_fields)

    """
    Updates an existing superuser while manually managing foreign key IDs.

    **Superuser Update Rules:**
        - Ensures that `is_staff` and `is_superuser` remain `True`.
        - Allows updating login identifiers (`username`, `email`, etc.), but maintains required fields.
        - Tracks modifications using `modified_by_id`.
        - Saves the user in the `users_db` database.

    **Usage Example:**
        - `User.objects.update_superuser(user_id=1, modified_by_id=2, email="admin@newdomain.com")`

    Raises:
        - `ValueError` if attempting to unset `is_staff` or `is_superuser`.
        - `ValueError` if no valid login method remains after the update.
    """
    def update_superuser(self, user_id, **updated_fields):
        try:
            # Retrieve the user instance from the correct database
            user = self.get_queryset().using("users_db").get(id=user_id)

            # Ensure the user is a superuser
            if not user.is_superuser:
                raise ValueError(f"User with ID {user_id} is not a superuser.")

            # Extract manually managed foreign key IDs
            organization_id = updated_fields.pop("organization_id", None)
            site_id = updated_fields.pop("site_id", None)
            modified_by_id = updated_fields.pop("modified_by_id", None)

            # Ensure `is_staff` and `is_superuser` remain True
            if "is_staff" in updated_fields and not updated_fields["is_staff"]:
                raise ValueError("Superuser must have is_staff=True.")
            if "is_superuser" in updated_fields and not updated_fields["is_superuser"]:
                raise ValueError("Superuser must have is_superuser=True.")

            # Normalize email if provided
            if "email" in updated_fields:
                updated_fields["email"] = self.normalize_email(updated_fields["email"])

            # Ensure at least one login identifier remains set
            if not any([
                updated_fields.get("username", user.username),
                updated_fields.get("badge_barcode", user.badge_barcode),
                updated_fields.get("badge_rfid", user.badge_rfid)
            ]):
                raise ValueError("At least one login identifier (username, badge) must remain set.")

            # Assign manually managed foreign key IDs
            if organization_id is not None:
                user.organization_id = organization_id
            if site_id is not None:
                user.site_id = site_id
            if modified_by_id is not None:
                user.modified_by_id = modified_by_id

            # Update the user fields with provided values
            for field, value in updated_fields.items():
                setattr(user, field, value)

            # Save changes to the correct database
            user.save(using="users_db")
            return user

        except self.model.DoesNotExist:
            raise ValueError(f"Superuser with ID {user_id} does not exist.")

    """
        Deletes a superuser from the users_db with extra safety checks.

        **Usage Example:**
            - `User.objects.delete_superuser(user_id=1)`

        **Handles:**
            - Ensuring the superuser exists before deletion.
            - Preventing deletion of the last remaining superuser.
            - Removing the superuser only from `users_db`.

        Raises:
            - `ValueError` if the superuser does not exist.
            - `ValueError` if deleting the last superuser.
    """
    def delete_superuser(self, user_id):
        try:
            # Retrieve the superuser instance
            superuser = self.get_queryset().using("users_db").get(id=user_id, is_superuser=True)

            # Prevent deleting the last superuser
            if self.get_queryset().using("users_db").filter(is_superuser=True).count() == 1:
                raise ValueError("Cannot delete the last remaining superuser.")

            # Delete the superuser
            superuser.delete(using="users_db")
            return f"Superuser with ID {user_id} deleted successfully."

        except self.model.DoesNotExist:
            raise ValueError(f"Superuser with ID {user_id} does not exist.")

    """
    Fetches an active user based on a unique identifier.

    Login Identifier Options:
        - Email (`email`)
        - Username (`username`)
        - Badge Barcode (`badge_barcode`)
        - Badge RFID (`badge_rfid`)

    Behavior:
        - Case-insensitive lookup (`iexact`) for flexible authentication.
        - Ensures only **active** users can authenticate.
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
    Custom QuerySet Methods for User Model

    Optimized query methods to handle user-related queries efficiently.
    
    Key Features:
        - Query users based on login identifiers (email, username, badge_barcode, badge_rfid).
        - Filter users by active/inactive status.
        - Retrieve users by name (first name, last name, full name).
        - Fetch users associated with specific organizations and sites.
        - Handle Multi-Factor Authentication (MFA) preferences.
        - Identify staff users and recently joined users.
    
    **Manual Foreign Key Handling**
    Since Django does not natively support cross-database foreign keys, we store organization, 
        site, and user relationships using **IntegerFields** (organization_id, site_id, created_by_id, modified_by_id).
    
    To retrieve related objects:
        - Use `User.get_organization()` to manually fetch the related Organization.
        - Use `User.get_site()` to manually fetch the related Site.
        - Use `User.get_created_by()` and `User.get_modified_by()` to fetch user references.

    This ensures compatibility with multi-database architecture while maintaining flexibility.
    """

    # Returns users created by a specific user
    def created_by(self, user_id):
        return self.filter(created_by_id=user_id)

    # Returns users modified by a specific user
    def modified_by(self, user_id):
        return self.filter(modified_by_id=user_id)

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
    def from_site(self, site_id):
        return self.filter(site_id=site_id)

    # Returns all users from organization
    def from_organization(self, organization_id):
        return self.filter(organization_id=organization_id)

    # Returns all active users from site
    def active_from_site(self, site_id):
        return self.filter(is_active=True, site_id=site_id)

    # Returns all inactive users from site
    def inactive_from_site(self, site_id):
        return self.filter(is_active=False, site_id=site_id)

    # Returns all active users from organization
    def active_from_organization(self, organization_id):
        return self.filter(is_active=True, organization_id=organization_id)    

    # Returns all inactive users from organization
    def inactive_from_organization(self, organization_id):
        return self.filter(is_active=False, organization_id=organization_id)  
    
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
    def staff_from_site(self, site_id):
        return self.filter(is_staff=True, site_id=site_id)
        
    # Returns all staff users from organization
    def staff_from_organization(self, organization_id):
        return self.filter(is_staff=True, organization_id=organization_id)

    # Returns all users created in the last X days (default: 30)
    def recently_joined(self, days=30):
        return self.filter(date_joined__gte=now() - timedelta(days=days))

    # Returns all users created in the last X days from a specific site
    def recently_joined_from_site(self, site_id, days=30):
        return self.filter(date_joined__gte=now() - timedelta(days=days), site_id=site_id)

    # Returns all users created in the last X days from a specific organization
    def recently_joined_from_organization(self, organization_id, days=30):
        return self.filter(date_joined__gte=now() - timedelta(days=days), organization_id=organization_id)


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

    Usage Example:
        user = User.objects.using("users_db").get(id=1)
        organization = user.get_organization()  # Fetch organization manually
    """

    def get_organization(self):
        if self.organization_id:
            # Keep import inside method when doing cross app references.
            from organizations.models import Organization
            return Organization.objects.using("organizations_db").filter(id=self.organization_id).first()
        return None

    def get_site(self):
        if self.site_id:
            # Keep import inside method when doing cross app references.
            from sites.models import Site
            return Site.objects.using("sites_db").filter(id=self.site_id).first()
        return None

    def get_created_by(self):
        if self.created_by_id:
            return User.objects.using("users_db").filter(id=self.created_by_id).first()
        return None

    def get_modified_by(self):
        if self.modified_by_id:
            return User.objects.using("users_db").filter(id=self.modified_by_id).first()
        return None



    
print("DEBUG: Finished loading models for users app.")