from django.contrib import admin
from .models import Site

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'site_type', 'address', 'active']
    search_fields = ['name', 'organization', 'site_type']
    list_filter = ['organization', 'active']
    ordering = ['organization', 'name']