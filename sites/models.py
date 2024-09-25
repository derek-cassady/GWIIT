from django.db import models
from organizations.models import Organization
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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
    name = models.CharField(max_length=255, db_index=True, verbose_name=_('Site Name'))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name='sites', verbose_name=_('Organization Name'))  # Reference to Organization
    
    # Extensible fields
    site_type = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Site Type'))  # Site type (e.g., Warehouse, Office, Clinic)
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Site Address'))
    active = models.BooleanField(default=True, verbose_name=_('Site Active'))
    
    # Tracking fields
    date_created = models.DateTimeField(default=timezone.now, verbose_name=_('Date Created'))
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='created_sites', verbose_name=_('Created By'))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last Modified'))
    modified_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='modified_sites', verbose_name=_('Modified By'))

    class Meta:
        # Singular for 'Site' model
        verbose_name = _('Site')
        # Plural for 'Site' model
        verbose_name_plural = _('Sites')

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
    site = models.ForeignKey('Site', on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts', verbose_name=_('Site Name'))
    first_name = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('Last Name'))
    email = models.EmailField(null=True, blank=True, db_index=True, verbose_name=_('Email Address'))
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('Phone Number'))
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Site Mailing Address'))
    role = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Role'))  # Role in the site (e.g., Manager)

    # Tracking fields
    date_created = models.DateTimeField(default=timezone.now, verbose_name=_('Date Created'))
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='created_site_contacts', verbose_name=_('Created By'))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last Modified'))
    modified_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='modified_site_contacts', verbose_name=_('Modified By'))

    objects = ContactManager()

    class Meta:
        # Singular for 'Contact' model
        verbose_name = _('Contact')
        # Plural for 'Contact' model
        verbose_name_plural = _('Contacts')
    
    # Property for the full name
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def __str__(self):
        return f"{self.name} ({self.site.name if self.site else _('No Site')})"