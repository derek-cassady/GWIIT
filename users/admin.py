from django.contrib import admin
from .models import User
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.admin import SimpleListFilter

# Custom filter: users who logged in today, last week, or last month
class LastLoginFilter(SimpleListFilter):
    title = "Last Login"
    parameter_name = "last_login"

    def lookups(self, request, model_admin):
        return [
            ('last_7_days', "Last 7 Days"),
            ('last_30_days', "Last 30 Days"),
            ('last_90_days', "Last 90 Days"),
            ('never_logged_in', "Never Logged In")
        ]

    def queryset(self, request, queryset):
               
        if self.value() == 'last_7_days':
            return queryset.filter(last_login__gte=now() - timedelta(days=7))
        if self.value() == 'last_30_days':
            return queryset.filter(last_login__gte=now() - timedelta(days=30))
        if self.value() == 'last_90_days':
            return queryset.filter(last_login__gte=now() - timedelta(days=90))
        if self.value() == 'never_logged_in':
            return queryset.filter(last_login__isnull=True)
        return queryset

# Custom filter: users who were created in the last 7, 30, or 90 days
class RecentlyCreatedFilter(SimpleListFilter):
    title = "Recently Joined"
    parameter_name = "date_joined"

    def lookups(self, request, model_admin):
        return [
            ('last_7_days', "Last 7 Days"),
            ('last_30_days', "Last 30 Days"),
            ('last_90_days', "Last 90 Days"),
        ]

    def queryset(self, request, queryset):
        
        if self.value() == 'last_7_days':
            return queryset.filter(date_joined__gte=now() - timedelta(days=7))
        if self.value() == 'last_30_days':
            return queryset.filter(date_joined__gte=now() - timedelta(days=30))
        if self.value() == 'last_90_days':
            return queryset.filter(date_joined__gte=now() - timedelta(days=90))
        return queryset

# Custom filter: users who were created in the last 7, 30, or 90 days
class RecentlyModifiedFilter(SimpleListFilter):
    title = "Recently Modified"
    parameter_name = "last_modified"

    def lookups(self, request, model_admin):
        return [
            ('last_7_days', "Last 7 Days"),
            ('last_30_days', "Last 30 Days"),
            ('last_90_days', "Last 90 Days"),
        ]

    def queryset(self, request, queryset):
        
        if self.value() == 'last_7_days':
            return queryset.filter(last_modified__gte=now() - timedelta(days=7))
        if self.value() == 'last_30_days':
            return queryset.filter(last_modified__gte=now() - timedelta(days=30))
        if self.value() == 'last_90_days':
            return queryset.filter(last_modified__gte=now() - timedelta(days=90))
        return queryset

class CustomUserAdmin(admin.ModelAdmin):
    
    # Disable bulk actions
    actions = None

    # Speeds up queries for large databases
    # Hides full count (only shows “Page 1 of X”)
    show_full_result_count = False

    list_per_page = 50

    # Shows "N/A" instead of empty fields
    empty_value_display = "N/A"

    # Only email and username are clickable
    list_display_links = ['email', 'username']

    # Fields to display in the list view
    list_display = [
        'email', 'username', 'first_name', 'last_name', 'badge_barcode', 'badge_rfid', 
        'organization', 'site', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined',
        'date_created', 'created_by', 'last_modified', 'modified_by'
    ]
    
    # Fields that can be searched
    search_fields = [
        'email', 'username', 'first_name', 'last_name', 'badge_barcode', 'badge_rfid', 
        'organization', 'site', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined',
        'date_created', 'created_by', 'last_modified', 'modified_by'
    ]
    
    # Fields to filter
    list_filter = [
        'organization', 'site', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined',
        'date_created', 'created_by', 'last_modified', 'modified_by', LastLoginFilter,
        RecentlyCreatedFilter, RecentlyModifiedFilter
    ]

    # Fields to order by default (newest user first, then by email)
    ordering = ['-date_joined', 'email']

    # Read-only fields
    readonly_fields = ['email', 'username', 'first_name', 'last_name', 'badge_barcode', 'badge_rfid', 
                       'organization', 'site', 'is_active', 'is_staff', 'last_login', 'date_joined',
                       'date_created', 'created_by', 'last_modified', 'modified_by']

    def has_add_permission(self, request):
        """Prevents user creation in Django Admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevents user editing in Django Admin."""
        return False

# Register the User model with the custom UserAdmin class
admin.site.register(User, CustomUserAdmin)
