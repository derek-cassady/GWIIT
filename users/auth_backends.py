from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.apps import apps

class MultiFieldModelBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in with 
    email, username, badge_barcode, or badge_rfid, while ensuring 
    only active users can authenticate.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Attempts to authenticate a user using email, username, badge_barcode, or badge_rfid.
        Only active users are considered.
        """
        try:
            User = apps.get_model("users", "User")
            user = User.objects.using("users_db").filter(
                Q(email=username) | 
                Q(username=username) | 
                Q(badge_barcode=username) | 
                Q(badge_rfid=username),
                is_active=True  # Ensures only active users can log in
            ).first()

            print(f"DEBUG: Found user: {user}")

        except User.DoesNotExist:
            print("DEBUG: No matching user found")
            return None  # No matching user found

        if user:
            print(f"DEBUG: Checking password for {user.email}")
        # Check the password
            if user.check_password(password):
                print("DEBUG: Password check passed")
                return user  # Return authenticated user object
            else:
                print("DEBUG: Password check failed")
        return None  # Authentication failed

    def user_can_authenticate(self, user):
        """Ensures that only active users can authenticate."""
        return user.is_active

    def has_perm(self, user_obj, perm, obj=None):
        """Overrides permission checks to prevent interference."""
        return True
    
    def get_group_permissions(self, user_obj, obj=None):
        """Returns an empty set to prevent Django errors with group permissions."""
        return set()

    def get_user(self, user_id):
        """
        Retrieves a user by their ID.
        """
        try:
            User = apps.get_model("users", "User")
            return User.objects.using("users_db").get(pk=user_id)
        except User.DoesNotExist:
            return None
