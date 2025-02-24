from django.contrib import admin
from .models import OrganizationType
from .models import Organization
from .models import OrganizationContact

admin.site.register(OrganizationType)
admin.site.register(Organization)
admin.site.register(OrganizationContact)

# from django.contrib import admin
# from .models import Organization, OrganizationContact, OrganizationType

# # Register (add) 'Organization' model
# @admin.register(Organization)
# class OrganizationAdmin(admin.ModelAdmin):
#     # Display field(s) in the list view
#     list_display = ['name', 'type', 'active', 'date_created', 'created_by', 'last_modified', 'modified_by']
    
#     # Enable search by field(s)
#     search_fields = ['name', 'type']
    
#     # Enable filter by field(s)
#     list_filter = ['active', 'date_created', 'created_by', 'modified_by']
    
#     # Field(s) to order by (default)
#     ordering = ['name', 'date_created']


# # Register (add) 'OrganizationType' model
# @admin.register(OrganizationType)
# class OrganizationTypeAdmin(admin.ModelAdmin):
#     # Display field(s) in the list view
#     list_display = ('name', 'description')
    
#     # Enable search by field(s)
#     search_fields = ('name',)
    
#     # Field(s) to order by (default)
#     ordering = ('name',)

# # Register (add) 'Contact' model   
# @admin.register(OrganizationContact)
# class ContactAdmin(admin.ModelAdmin):
#     # Display field(s) in the list view
#     list_display = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'organization', 'date_created']
    
#     # Enable search by field(s)
#     search_fields = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'organization__name']
    
#     # Enable filter by field(s)
#     list_filter = ['organization', 'role', 'date_created']
    
#     # Field(s) to order by (default)
#     ordering = ['last_name', 'first_name', 'organization', 'date_created']