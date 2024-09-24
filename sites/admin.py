from django.contrib import admin
from .models import Site, Contact

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ['name', 'organization', 'site_type', 'address', 'active']
    
    # Fields that can be searched
    search_fields = ['name', 'organization', 'site_type']
    
    # Fields to filter
    list_filter = ['organization', 'active']
    
    # Fields to order by (default)
    ordering = ['organization', 'name']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'site', 'date_created']
    
    # Fields that can be searched
    search_fields = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'site__name']
    
    # Fields to filter
    list_filter = ['site', 'role', 'date_created']
    
    # Fields to order by (default)
    ordering = ['last_name', 'first_name', 'email']