from django import forms
from .models import OrganizationType
from django.utils.translation import gettext_lazy as _

class OrganizationTypeForm(forms.ModelForm):
    class Meta:
        # Link the form to the OrganizationType model
        model = OrganizationType

        # field(s) to display in the form
        fields = ['name', 'description']  
        
        widgets = {

            # Use dropdown widget to choose organization type.
            'name': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': _('Name'),
            }),

            # Make the description field read-only.
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'readonly': True,
                'placeholder': _('Description'),
                'rows': 4,
            }),
        }

        # Defines human-readable label(s) for form field(s).
        labels = {
            'name': 
                _('Type Name'),
            'description': 
                _('Description'),
        }

        help_texts = {
            'name': 
                _('Select the name of the organization type.'),
            'description': 
                _('The description will be auto-populated based on the selected name.'),
        }
