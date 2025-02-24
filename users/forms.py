# from django import forms
# from .models import User
# from django.core.exceptions import ValidationError
# import phonenumbers
# from phonenumbers.phonenumberutil import NumberParseException
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth.password_validation import validate_password

# class CustomUserCreationForm(forms.ModelForm):
#     password = forms.CharField(
#         widget=forms.PasswordInput,
#         help_text="Enter a secure password."
#     )
    
#     class Meta:
#         model = User
#         # Adding all relevant fields from the User model
#         fields = (
#             'email', 'username', 'first_name', 'last_name', 'badge_barcode', 'badge_rfid', 'organization',
#             'site', 'phone_number', 'mfa_preference', 'mfa_secret', 'password')

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])  # Hash the password manually
#         if commit:
#             user.save()
#         return user
    
#     # Clean and validate email (remove trailing spaces)
#     def clean_email(self):
#         email = self.cleaned_data.get('email').strip()  # Remove spaces at end of entry
#         if User.objects.filter(email=email).exists(): # Check to see if it already exists
#             raise ValidationError(_("A user with this email already exists."))
#         return email

#     # Clean and validate username (all lowercase, remove trailing spaces)
#     def clean_username(self):
#         username = self.cleaned_data.get('username').strip().lower()  # Remove spaces and lowercase
#         if User.objects.filter(username=username).exists(): # Check to see if it already exists
#             raise ValidationError(_("A user with this username already exists."))
#         return username

#     # Clean and validate first name (capitalize first letter, strip trailing spaces)
#     def clean_first_name(self):
#         first_name = self.cleaned_data.get('first_name').strip() # Remove spaces at end of entry
#         return first_name.title()  # Capitalize first letter of each word

#     # Clean and validate last name (capitalize first letter, strip trailing spaces)
#     def clean_last_name(self):
#         last_name = self.cleaned_data.get('last_name').strip() # Remove spaces at end of entry
#         return last_name.title()  # Capitalize first letter of each word

#     # Clean and validate badge_barcode (optional)
#     def clean_badge_barcode(self):
#         badge_barcode = self.cleaned_data.get('badge_barcode', '').strip() # Remove spaces at end of entry
#         return badge_barcode or None  # Return None if it's blank

#     # Clean and validate badge_rfid (optional)
#     def clean_badge_rfid(self):
#         badge_rfid = self.cleaned_data.get('badge_rfid', '').strip() # Remove spaces at end of entry
#         return badge_rfid or None  # Return None if it's blank

#     # Clean and validate MFA preference
#     def clean_mfa_preference(self):
#         mfa_preference = self.cleaned_data.get('mfa_preference')
#         if mfa_preference not in ['none', 'google_authenticator', 'sms', 'email', 'static_otp']:
#             raise ValidationError(_("Invalid MFA preference."))
#         return mfa_preference
    
#     # Clean and validate phone number with specific error handling (optional)
#     def clean_phone_number(self):
#         phone_number = self.cleaned_data.get('phone_number', '').strip()  # Remove trailing spaces
#         if not phone_number:
#             return None
        
#         try:
#             # Parse phone number (assuming US format for now)
#             parsed_number = phonenumbers.parse(phone_number, "US")
            
#             # Validate if it's a valid phone number for that country
#             if not phonenumbers.is_valid_number(parsed_number):
#                 raise ValidationError(_("The phone number entered is not valid for the US."))
            
#             # Return phone number in standardized E.164 format (+1XXXXXXXXXX)
#             return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        
#         except NumberParseException as e:
#             # Handle different types of number parsing exceptions
#             if e.error_type == NumberParseException.TOO_SHORT_AFTER_IDD:
#                 raise ValidationError(_("The phone number is too short after the international dialing code."))
#             elif e.error_type == NumberParseException.TOO_SHORT_NSN:
#                 raise ValidationError(_("The phone number is too short."))
#             elif e.error_type == NumberParseException.INVALID_COUNTRY_CODE:
#                 raise ValidationError(_("The country code is invalid."))
#             elif e.error_type == NumberParseException.NOT_A_NUMBER:
#                 raise ValidationError(_("The input is not a valid phone number."))
#             else:
#                 raise ValidationError(_("Invalid phone number format."))

#     # Clean and validate MFA secret (optional)
#     def clean_mfa_secret(self):
#         mfa_secret = self.cleaned_data.get('mfa_secret', '').strip() # Remove spaces at end of entry
#         return mfa_secret or None
    
# class CustomSuperUserCreationForm(CustomUserCreationForm):  # Inheriting from CustomUserCreationForm
#     class Meta(CustomUserCreationForm.Meta):
#         model = User  # Ensures it's still for User model
#         fields = CustomUserCreationForm.Meta.fields + ('is_staff', 'is_superuser')
    
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.is_staff = True  # Ensure superuser properties
#         user.is_superuser = True
#         if commit:
#             user.save()
#         return user

# class CustomUserChangeForm(forms.ModelForm):
#     password = forms.CharField(
#         widget=forms.PasswordInput,
#         required=False,  # Allow users to keep their existing password
#         help_text="Leave blank to keep the current password."
#     )

#     class Meta:
#         model = User
#         fields = (
#             'email', 'username', 'first_name', 'last_name', 'badge_barcode', 'badge_rfid',
#             'organization', 'site', 'phone_number', 'mfa_preference', 'mfa_secret', 'is_active', 'is_staff', 'password')

#     def clean_password(self):
#         password = self.cleaned_data.get("password")

#         if password:
#             validate_password(password)  # Enforce all password validation rules

#         return password

#     def save(self, commit=True):
#         user = super().save(commit=False)

#         # Only update password if a new one was provided
#         if self.cleaned_data["password"]:
#             user.set_password(self.cleaned_data["password"])  # Securely hash password

#         if commit:
#             user.save()
#         return user
    
# class CustomSuperUserChangeForm(CustomUserChangeForm):  # Inheriting from CustomUserChangeForm
#     class Meta(CustomUserChangeForm.Meta):
#         model = User  # Ensures it's still for User model
#         fields = CustomUserChangeForm.Meta.fields + ('is_staff', 'is_superuser')

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.is_staff = True  # Ensure superuser properties
#         user.is_superuser = True
#         if commit:
#             user.save()
#         return user   