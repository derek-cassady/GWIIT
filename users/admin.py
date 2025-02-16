from django.contrib import admin
from .models import User
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(admin.ModelAdmin):  # Changed from BaseUserAdmin to ModelAdmin
    # Fields to display in the list view
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff']
    
    # Fields that can be searched
    search_fields = ['email', 'username', 'first_name', 'last_name']
    
    # Fields to filter
    list_filter = ['is_active', 'is_staff', 'organization', 'site']

    # Fields to order by (default)
    ordering = ['email']

    # Fieldsets for editing users (organizing fields in the admin)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'badge_barcode', 'badge_rfid')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff')}),  # No more groups/user_permissions
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

    # No need for groups or permissions
    filter_horizontal = ()

    # Read-only fields
    readonly_fields = ['date_joined', 'last_login']

# Register the User model with the custom UserAdmin class
admin.site.register(User, CustomUserAdmin)
