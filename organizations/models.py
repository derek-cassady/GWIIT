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