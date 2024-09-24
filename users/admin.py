from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff']
    
    # Fields that can be searched
    search_fields = ['email', 'username', 'first_name', 'last_name']
    
    # Fields to filter
    list_filter = ['is_active', 'is_staff', 'organization', 'site']
    
    # Fields to order by (default)
    ordering = ['email']