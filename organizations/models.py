from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

class OrganizationManager(models.Manager):
    
    # Returns all active organizations
    def active(self):
        return self.filter(active=True)

    # Returns all inactive organizations
    def inactive(self):
        return self.filter(active=False)

    # Returns all organizations created by a specific user
    def created_by_user(self, user):
        return self.filter(created_by=user)

    # Returns all organizations modified by a specific user
    def modified_by_user(self, user):
        return self.filter(modified_by=user)

class Organization(models.Model):
    # Extensible fields    
    name = models.CharField(max_length=255, unique=True, verbose_name='Organization Name')
    description = models.TextField(null=True, blank=True, verbose_name='Organization Description')
    active = models.BooleanField(default=True, verbose_name='Organization Active')
    
    # Tracking fields
    date_created = models.DateTimeField(default=timezone.now, verbose_name='Date Created')
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='created_organizations', null=True, blank=True, verbose_name='Created By')  # Reference to User model
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Last Modified')
    modified_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='modified_organizations', null=True, blank=True, verbose_name='Modified By')  # Reference to User model

    objects = OrganizationManager()

    class Meta:
        # Singular for 'Organization' model
        verbose_name = 'Organization'
        # Plural for 'Organization' model
        verbose_name_plural = 'Organizations'

    def __str__(self):
        return self.name
    
class ContactManager(models.Manager):
    # Returns all contacts from a specific organization
    def from_organization(self, organization):
        return self.filter(organization=organization)

    # Returns all contacts with a specific role
    def with_role(self, role):
        return self.filter(role=role)

    # Returns all contacts created by a specific user
    def created_by_user(self, user):
        return self.filter(created_by=user)

    # Returns all contacts modified by a specific user
    def modified_by_user(self, user):
        return self.filter(modified_by=user)

class Contact(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=100, null=True, blank=True)  # Role in the organization (e.g., CEO, Manager)

    # Tracking fields
    date_created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='created_organization_contacts')
    last_modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='modified_organization_contacts')

    objects = ContactManager()

    class Meta:
        # Singular for 'Contact' model
        verbose_name = 'Contact'
        # Plural for 'Contact' model
        verbose_name_plural = 'Contacts'

    # Property for the full name
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def __str__(self):
        return f"{self.name} ({self.organization.name if self.organization else 'No Organization'})"    