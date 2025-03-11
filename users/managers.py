from django.db import models
from django.apps import apps
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
import random
import string
import secrets
import re

"""
Custom Manager for the User Model

Provides methods for creating, updating, deleting, and querying users,
    while supporting manual foreign key handling due to multi-database constraints.

Create, Update & Deletion Methods:
    - `create_user(email, password=None, **extra_fields)`: Creates a new user while manually handling foreign keys.
    - `create_superuser(email, username, password=None, **extra_fields)`: Creates a superuser with full admin access.
    - `update_user(user_id, **updated_fields)`: Updates an existing user with the provided field values.
    - `delete_user(user_id)`: Deletes a user with verification.

Query Methods:
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

Why Manual Foreign Keys?
    - Django does not support cross-database foreign key relations.
    - Integer fields (`organization_id`, `site_id`, `created_by_id`, `modified_by_id`) are used instead of actual ForeignKey fields.
    - Query methods work by filtering based on these integer IDs.

Usage Example:
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
    Creates a new user while ensuring proper validation and unique constraints.

    Purpose:
        - Manages manual foreign key assignments (`organization_id`, `site_id`, `created_by_id`, `modified_by_id`).
        - Ensures that only **inactive** users can share an email, username, or badge with another user.
        - Normalizes the email before database interaction.
        - Generates a secure password and hashes it before saving.
        - Saves the user in the `users_db` database.

    Validation Rules:
        - Email is required.
        - At least one login identifier is required 
            - `username`, `badge_barcode`, or `badge_rfid`
        - An active user cannot share:
            - `email`, `username`, `badge_barcode`, `badge_rfid`
        - Ensures all login identifiers are unique among active users.
        - Prevents duplicate credentials before database insertion.

    Security Measures:
        - Automatically generates a secure password using `generate_secure_password()`.
        - Password is securely hashed before storing.
        - Sends credentials via email (console mail backend for development).

    Guarantees that user creation follows security and uniqueness constraints.
    """


    def create_user(self, email, password=None, **extra_fields):
    
        # Dynamically retrieve models using apps.get_model()
        User = apps.get_model("users", "User")

        username = extra_fields.get("username")
        badge_barcode = extra_fields.get("badge_barcode")
        badge_rfid = extra_fields.get("badge_rfid")

        # Ensure at least one login method is provided, with email required
        if not email:
            raise ValueError("The Email field must be set.")
        
        # Ensure at least one login identifier is provided
        if not any([username, badge_barcode, badge_rfid]):
            raise ValueError("At least one additional login identifier (username, badge) must be set.")

        # Normalize email
        extra_fields["email"] = self.normalize_email(email)

        # Ensure is_active is explicitly set
        if "is_active" not in extra_fields:
            extra_fields["is_active"] = True


        # Prevent duplicate login identifiers for **active** users
        duplicate_active_user = User.objects.using("users_db").filter(
            models.Q(is_active=True) & (
                models.Q(email=extra_fields["email"]) |
                models.Q(username=username) |
                models.Q(badge_barcode=badge_barcode) |
                models.Q(badge_rfid=badge_rfid)
            )
        ).exists()

        if duplicate_active_user:
            raise ValueError("An active user with this email, username, or badge already exists.")

        # Extract manually managed foreign key IDs
        organization_id = extra_fields.pop("organization_id", None)
        site_id = extra_fields.pop("site_id", None)
        created_by_id = extra_fields.pop("created_by_id", None)
        modified_by_id = extra_fields.pop("modified_by_id", None)

        # Generate a secure password if none is provided
        if password is None:
            password = self.generate_secure_password()

        # Create the user instance dynamically
        user = User(**extra_fields)
        user.set_password(password)  # Hash the password

        # Assign manually managed foreign key IDs
        user.organization_id = organization_id
        user.site_id = site_id
        user.created_by_id = created_by_id
        user.modified_by_id = modified_by_id

        # Ensure the user is saved in the correct database
        user.save(using="users_db")

        # Build login details for the email
        login_info = {
            "Email": user.email,
            "Username": user.username,
            "Badge Barcode": user.badge_barcode,
            "Badge RFID": user.badge_rfid,
        }

        # Only include non-empty values in the email message
        login_details = "\n".join(f"{key}: {value}" for key, value in login_info.items() if value)

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
    Updates an existing user while enforcing active-user uniqueness constraints 
    and manually managing foreign key IDs.

    Manual Foreign Key Assignments:
        - `organization_id` and `site_id` are stored as integers (not objects).
        - `modified_by_id` is updated to track the user performing the modification.

    Active-User Uniqueness Constraints:
        - Prevents modifying `email`, `username`, `badge_barcode`, or `badge_rfid` 
            if the new value already exists in an **active** user.
        - Allows reassignment of these fields if the user being updated is inactive.
        - Ensures a user retains at least **one login identifier** (`username`, `badge_barcode`, or `badge_rfid`).

    Additional Features:
        - Normalizes the email before saving (if changed).
        - Allows selective updates by only modifying provided fields.
        - Ensures changes are committed to the `users_db` database.

    Usage Example:
        - `User.objects.update_user(user_id=5, modified_by_id=2, username="new_name")`
    """

    def update_user(self, user_id, **updated_fields):

        try:
            # Retrieve the user model dynamically
            User = apps.get_model("users", "User")

            # Retrieve the user instance from the correct database
            user = User.objects.using("users_db").get(id=user_id)

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

            print(User.objects.using("users_db").values("id", "email", "is_active"))

            # Prevent duplicate active users BEFORE saving to avoid IntegrityError
            fields_to_check = ["email", "username", "badge_barcode", "badge_rfid"]
            q_objects = models.Q(is_active=True)  # Ensure we're only checking active users

            for field in fields_to_check:
                new_value = updated_fields.get(field)
                if new_value and new_value != getattr(user, field):  # Only check if field is changing
                    q_objects &= models.Q(**{field: new_value})

            # If at least one field is changing, check for conflicts
            if any(updated_fields.get(field) for field in fields_to_check):
                conflict_query = models.Q(is_active=True) & models.Q(
                    models.Q(email=updated_fields.get("email")) |
                    models.Q(username=updated_fields.get("username")) |
                    models.Q(badge_barcode=updated_fields.get("badge_barcode")) |
                    models.Q(badge_rfid=updated_fields.get("badge_rfid"))
                )

                existing_user = User.objects.using("users_db").filter(conflict_query).exclude(id=user.id).first()
                                
                if existing_user:
                    raise ValueError("An active user with this email, username, or badge already exists.")

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

        except User.DoesNotExist:
            print(f"ERROR: User with ID {user_id} does not exist.")
        raise ValueError(f"User with ID {user_id} does not exist.") 

    """
    Soft-deletes a user by setting `is_active=False` instead of permanently deleting them.

    Purpose:
        - Preserves user records for auditability and historical reference.
        - Prevents unintended behaviors caused by hard deletion.
        - Ensures compliance with unique constraints on active users.
        - Prevents accidental deletion of superusers.

    Behavior:
        - Sets `is_active=False` to deactivate the user.
        - Retains all unique identifiers (`email`, `username`, `badge_barcode`, `badge_rfid`).
        - Allows recovery by reactivating the user (`is_active=True` if needed).

    Usage Example:
        - `User.objects.delete_user(user_id=3)`

    Raises:
        - `ValueError` if the user does not exist.
        - `ValueError` if attempting to delete a superuser.
    """
    def delete_user(self, user_id):

        try:
            # Retrieve the user model dynamically
            User = apps.get_model("users", "User")

            # Retrieve the user instance from the correct database
            user = User.objects.using("users_db").get(id=user_id)

            # Prevent accidental deletion of superusers
            if user.is_superuser:
                raise ValueError("Cannot delete a superuser using this method. Use `delete_superuser()` instead.")

            # Soft-delete: Deactivate the user but retain all data
            user.is_active = False

            # Save changes
            user.save(using="users_db")

            return f"User with ID {user_id} has been deactivated."

        except User.DoesNotExist:
            raise ValueError(f"User with ID {user_id} does not exist.")

    """
    Creates a new superuser while enforcing required permissions.

    Inherits:
        - Email normalization and login identifier validation from `create_user`.
        - Manual foreign key handling from `create_user`.

    Ensures:
        - `is_staff=True` and `is_superuser=True` before creation.
        - `is_active=True` to prevent accidental inactive superuser creation.

    Raises:
        - `ValueError` if `is_staff` or `is_superuser` are not explicitly set to `True`.
    """

    def create_superuser(self, email, username, password=None, **extra_fields):
    
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)  # Ensure superusers are always active

        if extra_fields["is_staff"] is not True or extra_fields["is_superuser"] is not True:
            raise ValueError("Superuser must have is_staff=True and is_superuser=True.")

        return self.create_user(email=email, username=username, password=password, **extra_fields)


    """
    Updates an existing superuser while enforcing required permissions.

    Superuser Update Rules:
        - Prevents accidental deactivation (`is_active` is always `True`).
        - Ensures that `is_staff=True` and `is_superuser=True` remain unchanged.
        - Allows updating login identifiers (`username`, `email`, `badge_barcode`, `badge_rfid`), but ensures at least one remains.
        - Normalizes email before saving (if updated).
        - Tracks modifications using `modified_by_id`.
        - Saves changes only in the `users_db` database.

    Usage Example:
        - `User.objects.update_superuser(user_id=1, modified_by_id=2, email="admin@newdomain.com")`

    Raises:
        - `ValueError` if attempting to unset `is_staff` or `is_superuser`.
        - `ValueError` if no valid login method remains after the update.
        - `ValueError` if the specified user is not a superuser.
    """
    
    def update_superuser(self, user_id, **updated_fields):
        try:
            # Retrieve the user model dynamically
            User = apps.get_model("users", "User")

            # Retrieve the user instance from the correct database
            user = User.objects.using("users_db").get(id=user_id)

            # Ensure the user is a superuser
            if not user.is_superuser:
                raise ValueError(f"User with ID {user_id} is not a superuser.")

            # Extract manually managed foreign key IDs
            organization_id = updated_fields.pop("organization_id", None)
            site_id = updated_fields.pop("site_id", None)
            modified_by_id = updated_fields.pop("modified_by_id", None)

            # Prevent deactivating a superuser
            updated_fields["is_active"] = True

            # Ensure `is_staff` and `is_superuser` remain True
            updated_fields["is_staff"] = True
            updated_fields["is_superuser"] = True

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

            # Update only the provided fields
            for field, value in updated_fields.items():
                setattr(user, field, value)

            # Save changes to the correct database
            user.save(using="users_db")
            return user

        except User.DoesNotExist:
            raise ValueError(f"Superuser with ID {user_id} does not exist.")

    """
    Deactivates a superuser instead of permanently deleting the record.

    Superuser Deletion Rules:
        - Ensures that at least **one active superuser** remains.
        - Uses **soft delete** (`is_active=False`) instead of actual deletion.
        - Prevents potential race conditions by locking the query (`select_for_update()`).
        - Saves changes in the `users_db` database.

    Usage Example:
        - `User.objects.delete_superuser(user_id=5)`

    Raises:
        - `ValueError` if attempting to deactivate the last active superuser.
        - `ValueError` if the specified superuser does not exist.
    """
    
    def delete_superuser(self, user_id):
        try:
            # Retrieve the user model dynamically
            User = apps.get_model("users", "User")

            # Retrieve the superuser instance
            superuser = User.objects.using("users_db").select_for_update().get(id=user_id, is_superuser=True)

            # Prevent deleting the last superuser
            if User.objects.using("users_db").filter(is_superuser=True, is_active=True).count() == 1:
                raise ValueError("Cannot deactivate the last remaining active superuser.")

            # Perform a soft delete instead of actual deletion
            superuser.is_active = False
            superuser.save(using="users_db")

            return f"Superuser with ID {user_id} has been deactivated."

        except User.DoesNotExist:
            raise ValueError(f"Superuser with ID {user_id} does not exist.")

    """
    Retrieves an active user using a natural key (email, username, badge barcode, or badge RFID).

    Enforces:
        - User must be active (`is_active=True`).
        - Lookup is case-insensitive (`iexact`).
        - Supports login via:
            - `email`
            - `username`
            - `badge_barcode`
            - `badge_rfid`

    Raises:
        - ValueError: If no matching active user is found.
    """
        
    def get_by_natural_key(self, identifier):

        try:
            return self.get(
                models.Q(is_active=True) & (
                models.Q(email__iexact=identifier) |
                models.Q(username__iexact=identifier) |
                models.Q(badge_barcode__iexact=identifier) |
                models.Q(badge_rfid__iexact=identifier)
                )
            )
        except self.model.DoesNotExist:
            raise ValueError(f"No active user found with identifier: {identifier}")
    
    """
    Custom Manager Methods for User Model

    Optimized query methods to handle user-related queries efficiently.

    Key Features:
        - Query users based on login identifiers (email, username, badge_barcode, badge_rfid).
        - Filter users by active/inactive status.
        - Retrieve users by name (first name, last name, full name).
        - Fetch users associated with specific organizations and sites.
        - Handle Multi-Factor Authentication (MFA) preferences.
        - Identify staff users and recently joined users.

    **Why These Methods Do Not Use `get_queryset()`**
    These manager methods **operate on existing QuerySets**—they do not retrieve objects independently.
    - `get_queryset()` is **not needed** because we are working with `self.filter()`, which applies to an existing QuerySet.
    - This ensures optimal query execution without redefining how QuerySets are retrieved.

    **Why We Do Not Use `apps.get_model()` Here**
    - These methods **do not need explicit model references** since they only filter the User model itself.
    - `apps.get_model()` is only required when dynamically retrieving related models, which we handle elsewhere.

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