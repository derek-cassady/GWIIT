from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

class Organization(models.Model):
    # Extensible fields    
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    
    # Tracking fields
    date_created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='created_organizations', null=True, blank=True)  # Reference to User model
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='modified_organizations', null=True, blank=True)  # Reference to User model

    def __str__(self):
        return self.name
    
class Contact(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=100, null=True, blank=True)  # Role in the organization (e.g., CEO, Manager)

    def __str__(self):
        return f"{self.name} ({self.organization.name if self.organization else 'No Organization'})"    