# from django import forms
# from django.core.exceptions import ValidationError
# from .models import Site
# from django.utils.translation import gettext_lazy as _

# class CustomSiteCreationForm(forms.ModelForm):
#     class Meta:
#         model = Site
#         # Adding all relevant fields from the Site model
#         fields = ('name', 'organization', 'site_type', 'address', 'active')

#     # Clean and validate name (Remove trailing spaces and ensure uniqueness)
#     def clean_name(self):
#         name = self.cleaned_data.get('name').strip() # Remove trailing spaces
#         if Site.objects.filter(name=name).exists():
#             raise ValidationError(_("A site with this name already exists."))
#         return name.title()  # Capitalize first letter of each word
    
#     # Clean and validate organization (Make sure organization is not null)
#     def clean_organization(self):
#         organization = self.cleaned_data.get('organization').strip() # Remove trailing spaces
#         if not organization:
#             raise ValidationError(_("An organization must be assigned to the site."))
#         return organization.title()  # Capitalize first letter of each word

#     # Clean and validate site type (Optional, but enforce proper format if provided)
#     def clean_site_type(self):
#         site_type = self.cleaned_data.get('site_type', '').strip()  # Remove trailing spaces
#         # Capitalize first letter of each word
#         return site_type.title() or None  # Return None if it's blank

#     # Clean and validate address (Optional, but enforce format if provided)
#     def clean_address(self):
#         address = self.cleaned_data.get('address', '').strip()  # Remove trailing spaces
#         return address or None  # Return None if it's blank

#     # Ensure active field is set (Default True, but can be changed)
#     def clean_active(self):
#         active = self.cleaned_data.get('active', True)  # Default to True if not provided
#         return active

# class CustomSiteChangeForm(forms.ModelForm):
#     class Meta:
#         model = Site
#         fields = ('name', 'organization', 'site_type', 'address', 'active', 'created_by', 'last_modified')