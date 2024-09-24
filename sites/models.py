from django.db import models
from organizations.models import Organization
from django.contrib.auth import get_user_model
from django.utils import timezone

class SiteManager(models.Manager):
    # Returns all active sites
    def active(self):
        return self.filter(active=True)

    # Returns all inactive sites
    def inactive(self):
        return self.filter(active=False)

    # Returns all sites belonging to a specific organization
    def from_organization(self, organization):
        return self.filter(organization=organization)

    # Returns all active sites from a specific organization
    def active_from_organization(self, organization):
        return self.filter(active=True, organization=organization)
    
    # Returns all inactive sites from a specific organization
    def inactive_from_organization(self, organization):
        return self.filter(active=False, organization=organization)

    # Returns all sites of a type
    def of_type(self, site_type):
        return self.filter(type=site_type)

    # Returns all sites created by a user
    def created_by_user(self, user):
        return self.filter(created_by=user)

    # Returns all sites modified by a user
    def modified_by_user(self, user):
        return self.filter(modified_by=user)

class Site(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='sites')  # Reference to Organization
    
    # Extensible fields
    site_type = models.CharField(max_length=100, null=True, blank=True)  # Site type (e.g., Warehouse, Office, Clinic)
    address = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)
    
    # Tracking fields
    date_created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='created_sites')
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='modified_sites')

    def __str__(self):
        return self.name

    objects = SiteManager()

class ContactManager(models.Manager):
    # Returns all contacts from a specific site
    def from_site(self, site):
        return self.filter(site=site)

    # Returns all contacts with a specific role
    def with_role(self, role):
        return self.filter(role=role)

    # Returns all contacts created by a specific user
    def created_by_user(self, user):
        return self.filter(created_by=user)

    # Returns all contacts modified by a specific user
    def modified_by_user(self, user):
        return self.filter(modified_by=user)
    
    # Returns all contacts with a specific phone number
    def with_phone_number(self, phone_number):
        return self.filter(phone_number=phone_number)

class Contact(models.Model):
    site = models.ForeignKey('Site', on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')
    name = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(null=True, blank=True, db_index=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=100, null=True, blank=True)  # Role in the site (e.g., Manager)

    # Tracking fields
    date_created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='created_site_contacts')
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='modified_site_contacts')

    objects = ContactManager()

    def __str__(self):
        return f"{self.name} ({self.site.name if self.site else 'No Site'})"