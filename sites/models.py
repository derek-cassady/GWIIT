print("DEBUG: Starting to load models for sites app...")
from django.db import models
from django.conf import settings
from django.utils.timezone import now, timedelta
from django.utils.translation import gettext_lazy as _

"""
Custom Manager for the Site Model

This manager provides optimized methods for filtering, creating, updating, and deleting sites,
    while supporting manual foreign key handling due to multi-database constraints.

**Create, Update & Deletion Methods:**
    - `create_site(...)`: Creates a new site and saves it in the database.
    - `update_site(site_id, **updated_fields)`: Updates an existing site
          with the provided field values.
    - `delete_site(site_id)`: Deletes a site with verification.

**Query Methods:**
    - `active_sites()`: Retrieves all active sites.
    - `inactive_sites()`: Retrieves all inactive sites.
    - `from_organization(organization_id)`: Retrieves sites belonging to a specific organization.
    - `active_from_organization(organization_id)`: Retrieves active sites linked to an organization.
    - `inactive_from_organization(organization_id)`: Retrieves inactive sites linked to an organization.
    - `by_type(site_type)`: Retrieves all sites matching a specific type.
    - `created_by_user(user_id)`: Retrieves sites created by a specific user.
    - `modified_by_user(user_id)`: Retrieves sites last modified by a specific user.
    - `recently_created(days=30)`: Retrieves sites created within the last `X` days.
    - `recently_modified(days=30)`: Retrieves sites modified within the last `X` days.

**Why Manual Foreign Keys?**
    - Django does not support cross-database foreign key relations.
    - Integer fields (e.g., `organization_id`, `created_by_id`, `modified_by_id`) are used instead of actual ForeignKey fields.
    - Query methods work by filtering based on these integer IDs.

**Usage Example:**
    - `sites = Site.objects.active_sites()`
    - `recent_sites = Site.objects.recently_created(days=15)`
"""

class SiteManager(models.Manager):
    """
    Creates and returns a Site instance.

    Args:
        - `name` (str, required): The name of the site.
        - `organization_id` (int, required): The ID of the associated organization.
        - `site_type` (str, optional): The type of the site (e.g., Warehouse, Office).
        - `address` (str, optional): Address of the site.
        - `active` (bool, optional): Whether the site is active (default: True).
        - `created_by_id` (int, optional): ID of the user who created this site.

    Returns:
        Site: A new Site instance.
    """
    def create_site(self, name, organization_id, site_type=None, address=None, active=True, created_by_id=None):
        
        site = self.model(
            name=name,
            organization_id=organization_id,
            site_type=site_type,
            address=address,
            active=active,
            created_by_id=created_by_id,
        )
        site.save(using=self._db)
        return site

    """
    Updates an existing site with provided fields.

    Args:
        - `site_id` (int): The ID of the site to update.
        - `updated_fields` (dict): Fields to update.

    Returns:
        Site: The updated Site instance or None if not found.
    """
    
    def update_site(self, site_id, **updated_fields):
        
        site = self.filter(id=site_id).first()
        if site:
            for field, value in updated_fields.items():
                setattr(site, field, value)
            site.save(using=self._db)
        return site

    """
    Deletes a site from the sites_db.

    **Usage Example:**
        - `Site.objects.delete_site(site_id=10)`

    **Handles:**
        - Ensuring the site exists before deletion.
        - Removing the site only from `sites_db`.
    
    Raises:
        - `ValueError` if the site does not exist.
    """
    
    def delete_site(self, site_id):
        try:
            # Retrieve the site instance
            site = self.using("sites_db").get(id=site_id)

            # Delete the site
            site.delete(using="sites_db")
            return f"Site with ID {site_id} deleted successfully."

        except self.model.DoesNotExist:
            raise ValueError(f"Site with ID {site_id} does not exist.")

    """
    Query Methods for Site Retrieval

    These methods retrieve sites based on various filters and constraints.

    - Organization-Based Queries (`from_organization`, `active_from_organization`, `inactive_from_organization`):
        - Allow fetching sites based on organization associations.

    - Active & Inactive Queries (`active_sites`, `inactive_sites`):
        - Retrieve sites based on their active status.

    - Type-Based Queries (`by_type`):
        - Fetch sites of a specific type.

    - Tracking Queries (`created_by_user`, `modified_by_user`, `recently_created`, `recently_modified`):
        - Retrieve sites based on who created or modified them.
        - `recently_created()` and `recently_modified()` allow dynamic time filtering (default: last 30 days).

    **Why These Methods?**
        - Efficient retrieval and filtering of sites for better UI and reporting.
        - Supports **manual foreign key management** across different databases.
    """

    # Returns all active sites
    def active_sites(self):
        return self.filter(active=True)

    # Returns all inactive sites
    def inactive_sites(self):
        return self.filter(active=False)

    # Returns all sites belonging to a specific organization
    def from_organization(self, organization_id):
        return self.filter(organization_id=organization_id)

    # Returns all active sites from a specific organization
    def active_from_organization(self, organization_id):
        return self.filter(active=True, organization_id=organization_id)

    # Returns all inactive sites from a specific organization
    def inactive_from_organization(self, organization_id):
        return self.filter(active=False, organization_id=organization_id)

    # Returns all sites of a given type
    def by_type(self, site_type):
        return self.filter(site_type=site_type)

    # Returns all sites created by a specific user
    def created_by_user(self, user_id):
        return self.filter(created_by_id=user_id)

    # Returns all sites modified by a specific user
    def modified_by_user(self, user_id):
        return self.filter(modified_by_id=user_id)

    # Returns all sites created in the last X days (default: 30)
    def recently_created(self, days=30):
        return self.filter(date_created__gte=now() - timedelta(days=days))

    # Returns all sites modified in the last X days (default: 30)
    def recently_modified(self, days=30):
        return self.filter(last_modified__gte=now() - timedelta(days=days))

"""
Represents a physical or virtual site associated with an organization.

This model stores essential site details such as name, type, address, and
    active status while managing relationships with organizations and users
    manually due to Django's lack of cross-database ForeignKey support.

**Fields:**
    - `organization_id`: Manually manages the foreign key reference to an organization.
    - `name`: The name of the site, used for identification.
    - `site_type`: Defines the type of site (e.g., Warehouse, Office, Clinic).
    - `address`: The physical or mailing address of the site.
    - `active`: Boolean flag indicating if the site is currently active.

**Tracking Fields:**
    - `date_created`: Automatically records when the site entry was created.
    - `created_by_id`: Tracks the ID of the user who created the site.
    - `last_modified`: Auto-updates when changes are made to the record.
    - `modified_by_id`: Tracks the ID of the user who last modified the site.

**Why Manual Foreign Keys?**
    - Django does not natively support cross-database ForeignKey relations.
    - Integer fields (`organization_id`, `created_by_id`, `modified_by_id`) store
      references to related models instead of using ForeignKey fields.
    - `get_organization()`, `get_created_by()`, and `get_modified_by()` methods
      dynamically retrieve related records from their respective databases.

**Example Usage:**
    site = Site.objects.using("sites_db").get(id=1)
    organization = site.get_organization()  # Retrieves associated organization
    creator = site.get_created_by()  # Retrieves the user who created this site
"""

class Site(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True, verbose_name=_('Site Name'))
    organization_id = models.IntegerField(null=True, blank=True, verbose_name=_("Organization ID"))
    site_type = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Site Type'))
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Site Address'))
    active = models.BooleanField(default=True, verbose_name=_('Site Active'))

    # Tracking fields
    date_created = models.DateTimeField(default=now, verbose_name=_('Date Created'))
    created_by_id = models.IntegerField(null=True, blank=True, verbose_name=_("Created By ID"))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last Modified'))
    modified_by_id = models.IntegerField(null=True, blank=True, verbose_name=_("Modified By ID"))

    objects = SiteManager()

    """
    Metadata options for the model:
        - app_label: Explicitly associates the model with its Django app.
        - verbose_name: Human-readable singular name for the model.
        - verbose_name_plural: Human-readable plural name for the model.
        - ordering: Defines the default ordering of query results.

    Notes:
        - app_label is required for multi-database setups to ensure correct app referencing.
        - ordering improves query efficiency by specifying a default sort order.
        - verbose_name settings enhance readability in admin and UI interfaces.
    """
    class Meta:
        app_label = "sites"
        verbose_name = _('Site')
        verbose_name_plural = _('Sites')
        ordering = ["name", "-active", "-date_created"]

    """
    String Representation and Active Status for Site

    - `is_active_label`: Converts the boolean `active` field into `"Active"` or `"Inactive"`.
    - `__str__()`: Provides a formatted string containing:
        - Site name
        - Organization name (retrieved via `get_organization()`)
        - Active status (`Active` / `Inactive`)

    Why These Methods?
        - Ensures consistency and clarity when displaying sites in logs, admin, and UI.
        - Uses a manual lookup (`get_organization()`) since ForeignKey relationships are not available.
        - Helps differentiate between sites with similar names by showing additional context.
    """
    @property
    def is_active_label(self):
        return _("Active") if self.active else _("Inactive")

    def __str__(self):
        organization = self.get_organization()
        organization_name = organization.name if organization else _("Unknown Organization")
        return f"{self.name} ({organization_name} - {self.is_active_label})"

    """
    These methods manually retrieve related objects from their respective databases
    due to Django’s lack of native cross-database ForeignKey support.

    **Why These Methods Are Inside the `Site` Model:**
        - They operate at the instance level, dynamically fetching related records.
        - They allow retrieval of associated organizations and users without an actual ForeignKey.
        - Unlike `SiteManager`, which handles QuerySet-level operations, these methods
          return a single related object or `None`.

    **Usage Example:**
        site = Site.objects.using("sites_db").get(id=1)
        organization = site.get_organization()  # Fetch associated organization
        created_by_user = site.get_created_by()  # Fetch the creator of the site
        modified_by_user = site.get_modified_by()  # Fetch the last user who modified the site
    """

    def get_organization(self):
        if self.organization_id:
            # Keep import inside method when doing cross app references.
            from organizations.models import Organization
            return Organization.objects.using("organizations_db").filter(id=self.organization_id).first()
        return None

    def get_created_by(self):
        if self.created_by_id:
            # Keep import inside method when doing cross app references.
            from users.models import User
            return User.objects.using("users_db").filter(id=self.created_by_id).first()
        return None

    def get_modified_by(self):
        if self.modified_by_id:
            # Keep import inside method when doing cross app references.
            from users.models import User
            return User.objects.using("users_db").filter(id=self.modified_by_id).first()
        return None

"""
Custom Manager for the Contact Model in Sites App

This manager provides database query methods tailored for contacts associated with sites.
It supports manual foreign key handling, ensuring compatibility across multiple databases.

**Create, Update & Deletion Methods:**
    - `create_contact(...)`: Creates a new contact and saves it in the database.
    - `update_contact(contact_id, **updated_fields)`: Updates an existing contact
          with the provided field values.
    - `delete_contact(contact_id)`: Deletes a contact with verification.

**Query Methods:**
    - `by_first_name(first_name)`: Retrieves contacts by first name (case-insensitive).
    - `by_last_name(last_name)`: Retrieves contacts by last name (case-insensitive).
    - `by_full_name(first_name, last_name)`: Retrieves contacts by full name.
    - `by_email(email)`: Retrieves contacts by their email.
    - `with_phone_number(phone_number)`: Retrieves contacts by phone number.
    - `from_site(site_id)`: Retrieves contacts belonging to a specific site.
    - `with_role(role)`: Retrieves contacts with a specific role in a site.
    - `created_by_user(user_id)`: Retrieves contacts created by a specific user.
    - `modified_by_user(user_id)`: Retrieves contacts last modified by a specific user.
    - `recently_created(days=30)`: Retrieves contacts created within the last `X` days.
    - `recently_modified(days=30)`: Retrieves contacts modified within the last `X` days.

**Why Manual Foreign Keys?**
    - Django does not support cross-database foreign key relations.
    - Integer fields (e.g., `site_id`, `created_by_id`, `modified_by_id`) are used instead of actual ForeignKey fields.
    - Query methods work by filtering based on these integer IDs.

**Usage Example:**
    - `contacts = Contact.objects.from_site(site_id=1)`
    - `recent_contacts = Contact.objects.recently_created(days=7)`
"""

class ContactManager(models.Manager):
    
    """
    Creates and returns a Contact instance for a Site.

    Args:
        - `site_id` (int, required): The ID of the associated site.
        - `first_name` (str, optional): First name of the contact.
        - `last_name` (str, optional): Last name of the contact.
        - `email` (str, optional): Email of the contact.
        - `phone_number` (str, optional): Contact's phone number.
        - `address` (str, optional): Contact's address.
        - `role` (str, optional): Contact's role in the site.
        - `created_by_id` (int, optional): ID of the user who created this contact.

    Returns:
        Contact: A new Contact instance.
    """
    def create_contact(self, site_id, first_name=None, last_name=None, email=None, phone_number=None, address=None, role=None, created_by_id=None):
        
        contact = self.model(
            site_id=site_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            address=address,
            role=role,
            created_by_id=created_by_id
        )
        contact.save(using=self._db)
        return contact

    """
    Updates an existing contact with provided fields.

    Args:
        - `contact_id` (int): The ID of the contact to update.
        - `updated_fields` (dict): Fields to update.

    Returns:
        Contact: The updated Contact instance or None if not found.
    """
    def update_contact(self, contact_id, **updated_fields):
        
        contact = self.filter(id=contact_id).first()
        if contact:
            for field, value in updated_fields.items():
                setattr(contact, field, value)
            contact.save(using=self._db)
        return contact

    """
    Deletes a contact from the sites_db.

    **Usage Example:**
        - `Contact.objects.delete_contact(contact_id=5)`

    **Handles:**
        - Ensuring the contact exists before deletion.
        - Removing the contact only from `sites_db`.
    
    Raises:
        - `ValueError` if the contact does not exist.
    """
    def delete_contact(self, contact_id):
        try:
            # Retrieve the contact instance
            contact = self.using("sites_db").get(id=contact_id)

            # Delete the contact
            contact.delete(using="sites_db")
            return f"Contact with ID {contact_id} deleted successfully."

        except self.model.DoesNotExist:
            raise ValueError(f"Contact with ID {contact_id} does not exist.")
    
    """
    Query Methods for Contact Retrieval

    These methods retrieve contacts based on various filters and constraints.

    - Name-Based Queries (`by_first_name`, `by_last_name`, `by_full_name`):
        - Allow searching for contacts based on partial or full name matches.
        - Case-insensitive queries are used for better usability.

    - Site & Role Queries (`from_site`, `with_role`):
        - Fetch contacts belonging to a specific site or holding a specific role.
    
    - Tracking Queries (`created_by_user`, `modified_by_user`, `recently_created`, `recently_modified`):
        - Retrieve contacts based on when they were created or modified.
        - `recently_created()` and `recently_modified()` allow dynamic time filtering (default: last 30 days).

    **Why These Methods?**
        - Efficient retrieval and filtering of contacts for better UI and reporting.
        - Supports **manual foreign key management** across different databases.
    """

    # Returns all contacts with a specific first name
    def by_first_name(self, first_name):
        return self.filter(first_name__icontains=first_name)

    # Returns all contacts with a specific last name
    def by_last_name(self, last_name):
        return self.filter(last_name__icontains=last_name)
    
    # Returns all contacts matching a full name.
    def by_full_name(self, first_name, last_name):
        return self.filter(first_name__icontains=first_name, last_name__icontains=last_name)

    # Returns contacts filtered by email address
    def by_email(self, email):
        return self.filter(email=email)

    # Returns all contacts from a specific site (manual foreign key handling)
    def from_site(self, site_id):
        return self.filter(site_id=site_id)

    # Returns all contacts with a specific role
    def with_role(self, role):
        return self.filter(role=role)

    # Returns all contacts created by a specific user
    def created_by_user(self, user_id):
        return self.filter(created_by_id=user_id)

    # Returns all contacts modified by a specific user
    def modified_by_user(self, user_id):
        return self.filter(modified_by_id=user_id)
    
    # Returns all contacts with a specific phone number
    def with_phone_number(self, phone_number):
        return self.filter(phone_number=phone_number)

    # Returns all contacts created in the last X days (default: 30)
    def recently_created(self, days=30):
        return self.filter(date_created__gte=now() - timedelta(days=days))

    # Returns all contacts modified in the last X days (default: 30)
    def recently_modified(self, days=30):
        return self.filter(last_modified__gte=now() - timedelta(days=days))

"""
Represents a contact person associated with a site.

This model stores contact details such as name, email, phone number, and role
    within a site. Relationships to sites and users (for tracking)
    are managed manually due to multi-database constraints.

**Fields:**
    - `site_id`: Manually manages the foreign key to a site.
    - `first_name`, `last_name`: Contact's full name (either can be optional).
    - `email`, `phone_number`: Preferred communication methods.
    - `address`: Mailing address for reference.
    - `role`: Job title or function within the site.

**Tracking Fields:**
    - `date_created`: Timestamp when the contact was added.
    - `created_by_id`: Tracks the user who created this contact.
    - `last_modified`: Auto-updates when changes occur.
    - `modified_by_id`: Tracks the user who last modified this record.

**Why Manual Foreign Keys?**
    - Django does not support cross-database foreign key relations.
    - `get_site()`, `get_created_by()`, and `get_modified_by()` methods
        dynamically retrieve related objects from the appropriate database.

**Example Usage:**
    contact = Contact.objects.using("sites_db").get(id=1)
    site = contact.get_site()  # Retrieves associated site
    creator = contact.get_created_by()  # Retrieves the user who added this contact
"""    

class Contact(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('Last Name'))
    email = models.EmailField(null=True, blank=True, db_index=True, verbose_name=_('Email Address'))
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('Phone Number'))
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Site Mailing Address'))
    role = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Role'))

    # Tracking fields
    date_created = models.DateTimeField(default=now, verbose_name=_('Date Created'))
    created_by_id = models.IntegerField(null=True, blank=True, verbose_name=_('Created By ID'))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last Modified'))
    modified_by_id = models.IntegerField(null=True, blank=True, verbose_name=_('Modified By ID'))

    objects = ContactManager()

    """
    Metadata options for the model:
        - app_label: Explicitly associates the model with its Django app.
        - verbose_name: Human-readable singular name for the model.
        - verbose_name_plural: Human-readable plural name for the model.
        - ordering: Defines the default ordering of query results.
            - Orders contacts by first name, then last name.
            - Uses `-date_created` to prioritize recently created records.

    Notes:
        - app_label is required for multi-database setups to ensure correct app referencing.
        - ordering improves query efficiency by defining a consistent query structure.
        - verbose_name settings enhance readability in the admin panel and UI interfaces.
    """

    class Meta:
        app_label = "sites"
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')
        ordering = ["first_name", "last_name", "-date_created"]
    
    """
    String Representation and Naming for Contact
        - `name()`: Computes the full name of the contact, handling cases where first or last name may be missing.
        - `__str__()`: Returns a formatted string representing the contact and their associated site.

    Why These Methods?
        - Ensures consistent and user-friendly identification of contacts across the application.
        - Handles missing name fields gracefully to avoid returning empty strings.
        - Uses a manual lookup (`get_site()`) to retrieve the site name since ForeignKey relationships are not used.
        - Provides meaningful output even when site data is unavailable.
    """
    @property
    def name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.first_name or self.last_name or _("Unnamed Contact")

    def __str__(self):
        site = self.get_site()
        site_name = site.name if site else _('No Site')
        return f"{self.name} ({site_name})"

    """
    Manual Foreign Key Lookup Methods

    These methods manually retrieve related user objects from the users database (`users_db`)
        due to Django’s lack of native cross-database ForeignKey support.

    Why These Methods Are Inside the `Contact` Model:
        - They operate at the instance level, dynamically fetching related user records.
        - They allow retrieval of associated users (`created_by` and `modified_by`)
          without using an actual ForeignKey.
        - Unlike `ContactManager`, which handles QuerySet-level operations, these methods
          return a single related object or `None`.

    Usage Example:
        contact = Contact.objects.using("sites_db").get(id=1)
        created_by_user = contact.get_created_by()  # Fetch the user who created this contact
        modified_by_user = contact.get_modified_by()  # Fetch the last user who modified this contact
    """
    def get_created_by(self):
        if self.created_by_id:
            # Keep import inside method when doing cross app references.
            from users.models import User
            return User.objects.using("users_db").filter(id=self.created_by_id).first()
        return None

    def get_modified_by(self):
        if self.modified_by_id:
            # Keep import inside method when doing cross app references.
            from users.models import User
            return User.objects.using("users_db").filter(id=self.modified_by_id).first()
        return None    

print("DEBUG: Finished loading models for sites app.")