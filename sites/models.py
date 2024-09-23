from django.db import models
from organizations.models import Organization
from django.contrib.auth import get_user_model
from django.utils import timezone

class Site(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='sites')  # Reference to Organization
    
    # Extensible fields
    type = models.CharField(max_length=100, null=True, blank=True)  # Site type (e.g., Warehouse, Office, Clinic)
    address = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)
    
    # Tracking fields
    date_created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='created_sites')
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='modified_sites')

    def __str__(self):
        return self.name