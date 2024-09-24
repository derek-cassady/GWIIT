from django.contrib import admin
from .models import Organization, Contact

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ['name', 'description', 'active', 'date_created', 'created_by', 'last_modified', 'modified_by']
    
    # Fields that can be searched
    search_fields = ['name', 'description']
    
    # Fields to filter
    list_filter = ['active', 'date_created', 'created_by', 'modified_by']
    
    # Fields to order by (default)
    ordering = ['name', 'date_created']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'organization', 'date_created']
    
    # Fields that can be searched
    search_fields = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'organization__name']
    
    # Fields to filter
    list_filter = ['organization', 'role', 'date_created']
    
    # Fields to order by (default)
    ordering = ['last_name', 'first_name', 'organization', 'date_created']