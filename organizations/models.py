print("DEBUG: Starting to load models for organizations app...")
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.db import models

class OrganizationTypeManager(models.Manager):
    """Custom manager for the OrganizationType model."""
    
    def get_queryset(self):
        """Ensure all queries return results ordered by name."""
        return super().get_queryset().order_by("name")

    def by_name(self, name):
        """Fetch an organization type by name (case insensitive)."""
        return self.get_queryset().filter(name__iexact=name).first()

    def with_description(self):
        """Fetch organization types that have a description."""
        return self.get_queryset().exclude(description__isnull=True).exclude(description="")

    def without_description(self):
        """Fetch organization types that do not have a description."""
        return self.get_queryset().filter(models.Q(description__isnull=True) | models.Q(description=""))


class OrganizationType(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Type Name"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Type Description"))

    objects = OrganizationTypeManager()

    class Meta:
        
        app_label = "organizations"
        
        # Specifies the singular display name for the model.
        # Used in places like the admin panel or form labels.
        verbose_name = _("Organization Type")

        # Specifies the plural display name for the model.
        # Used in places like the admin panel or form labels.
        verbose_name_plural = _("Organization Types")

        # Defines the default order for query results involving this model.
        # when querying this model (e.g., OrganizationType.objects.all()), 
        # the results will be sorted alphabetically by the name field.
        ordering = ["name"]

        # Explicit table name for DB creation
        db_table = "organization_type"

    def __str__(self):
        return self.name

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

# Core organization details
class Organization(models.Model):
    id = models.BigAutoField(primary_key=True)   
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Organization Name'))
    type = models.ForeignKey('OrganizationType', on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('Type'))
    active = models.BooleanField(default=True, verbose_name=_('Organization Active'))
    contact = models.OneToOneField('organizations.OrganizationContact', on_delete=models.SET_NULL, null=True, blank=True, related_name="contact_organization", verbose_name=_("Contact"))
    login_options = models.JSONField(default=dict, verbose_name=_("Login Options"))
    mfa_required = models.BooleanField(default=False, verbose_name=_("MFA Required"))

    # Tracking fields
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Created'))
    
    # Reference to User model
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_organizations', null=True, blank=True, verbose_name=_('Created By'))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last Modified'))
    
    # Reference to User model
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='modified_organizations', null=True, blank=True, verbose_name=_('Modified By'))

    objects = OrganizationManager()

    class Meta:

        app_label = "organizations"
        db_table = 'organizations_Organization'
        # Singular for 'Organization' model
        verbose_name = _('Organization')
        # Plural for 'Organization' model
        verbose_name_plural = _('Organizations')

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

class OrganizationContact(models.Model):
    id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_organization', verbose_name=_('contact_organization'))
    first_name = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('Last Name'))
    email = models.EmailField(null=True, blank=True, verbose_name=_('Email Address'))
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('Phone Number'))
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Organization Mailing Address'))
    role = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Role'))  # Role in the organization (e.g., CEO, Manager)

    # Tracking fields
    date_created = models.DateTimeField(default=timezone.now, verbose_name=_('Date Created'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='created_organization_contacts', verbose_name=_('Created By'))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last Modified'))
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='modified_organization_contacts', verbose_name=_('Modified By'))

    objects = ContactManager()

    class Meta:

        app_label = "organizations"

        # Singular for 'Contact' model
        verbose_name = _('Contact')
        # Plural for 'Contact' model
        verbose_name_plural = _('Contacts')

    # Property for the full name
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def __str__(self):
        return f"{self.name} ({self.organization.name if self.organization else _('No Organization')})"   



    print("DEBUG: Finished loading models for organizations app.") 