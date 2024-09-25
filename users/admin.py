from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(BaseUserAdmin):
    # Use the custom form for adding users
    add_form = CustomUserCreationForm

    # Use the custom form for changing (editing) users
    form = CustomUserChangeForm

    # Fields to display in the list view
    list_display = [_('email'), _('username'), _('first_name'), _('last_name'), _('is_active'), _('is_staff')]
    
    # Fields that can be searched
    search_fields = [_('email'), _('username'), _('first_name'), _('last_name')]
    
    # Fields to filter
    list_filter = [_('is_active'), _('is_staff'), _('organization'), _('site')]

    # Fields to order by (default)
    ordering = [_('email')]

    # Fieldsets for editing users (organizing fields in the admin)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'badge_barcode', 'badge_rfid')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('MFA Preferences'), {'fields': ('mfa_preference', 'mfa_secret')}),
        (_('Organization Info'), {'fields': ('organization', 'site')}),
    )

    # Fieldsets for adding users
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'badge_barcode', 'badge_rfid', 'mfa_preference', 'organization', 'site'),
        }),
    )

    # Groups and permissions (using a better UI widget)
    filter_horizontal = ('groups', 'user_permissions',)

    # Read-only fields
    readonly_fields = ['date_joined', 'last_login']

# Register the User model with the custom UserAdmin class
admin.site.register(User, CustomUserAdmin)