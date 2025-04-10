import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    """
    Enforces password rules:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one special character (@, #, $, etc.)
    - At least one digit
    """
    
    def validate(self, password, user=None):
        """Checks if the password meets the complexity requirements."""
        if not re.search(r'[A-Z]', password):
            raise ValidationError(_("Password must contain at least one uppercase letter."), code='password_no_upper')
        if not re.search(r'[a-z]', password):
            raise ValidationError(_("Password must contain at least one lowercase letter."), code='password_no_lower')
        if not re.search(r'\d', password):
            raise ValidationError(_("Password must contain at least one digit."), code='password_no_digit')
        if not re.search(r'[@#$%^&*()-_+=]', password):
            raise ValidationError(_("Password must contain at least one special character."), code='password_no_special')

    def get_help_text(self):
        """Returns a description of the password rules."""
        return _(
            "Your password must contain at least one uppercase letter, one lowercase letter, one digit, and "
            "one special character (@ # $ % ^ & * ( ) - _ + =)"
        )
