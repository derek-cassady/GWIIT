print("DEBUG: Starting to load models for organizations app...")
from django.db import models
from django.conf import settings
from django.utils.timezone import now, timedelta
from django.utils.translation import gettext_lazy as _
from django.db import models

"""
Custom Manager for OrganizationType Model

This manager provides methods to create, update, and delete organization types
    while ensuring data integrity across multi-database constraints.

**Create, Update & Deletion Methods:**
    - `create_organization_type(...)`: Creates a new organization type and saves it in the database.
    - `update_organization_type(type_id, **updated_fields)`: Updates an existing organization type
        with the provided field values.
    - `delete_organization_type(type_id)`: Deletes an organization type if no organizations depend on it.
        
    **Default Behavior:**
    - Overrides `get_queryset()` to ensure all queries are ordered by name.

**Query Methods:**
    - `by_name(name)`: Fetches an organization type by name (case insensitive).
    - `by_id(type_id)`: Fetches an organization type by ID (useful for FK lookups).
    - `with_description()`: Retrieves organization types that include a description.
    - `without_description()`: Retrieves organization types that lack a description.
    - `recently_created(days=30)`: Retrieves organization types created within the last X days.
    - `recently_modified(days=30)`: Retrieves organization types modified within the last X days.

**Why This Approach?**
    - Supports efficient lookups in a multi-database setup.
    - Ensures consistent data retrieval for related models like `Organization`.
    - Provides commonly needed queries without requiring custom filters.

**Example Usage:**
    - `organization_type = OrganizationType.objects.by_name("Non-Profit")`
    - `recent_types = OrganizationType.objects.recently_created(15)`  # Last 15 days
"""


class OrganizationTypeManager(models.Manager):

    """
    Creates a new OrganizationType instance.

    Args:
        - `name` (str): Name of the organization type (required).
        - `description` (str, optional): Description of the organization type.
        - `created_by_id` (int, optional): ID of the user who created this type.

    Returns:
        OrganizationType: A new OrganizationType instance.
    """
    
    def create_organization_type(self, name, description=None, created_by_id=None):
        
        organization_type = self.model(
            name=name,
            description=description,
            created_by_id=created_by_id
        )
        organization_type.save(using=self._db)
        return organization_type

    """
        Updates an existing organization type with provided fields.

        Args:
            - `type_id` (int): The ID of the organization type to update.
            - `updated_fields` (dict): Fields to update.

        Returns:
            OrganizationType: The updated OrganizationType instance or None if not found.
        """
    
    def update_organization_type(self, type_id, **updated_fields):
        
        organization_type = self.filter(id=type_id).first()
        if organization_type:
            for field, value in updated_fields.items():
                setattr(organization_type, field, value)
            organization_type.save(using=self._db)
        return organization_type

    """
        Deletes an organization type from the `organizations_db`.

        **Usage Example:**
            - `OrganizationType.objects.delete_organization_type(type_id=5)`

        **Handles:**
            - Ensuring the organization type exists before deletion.
            - Preventing deletion if related organizations exist.
            - Removing the organization type only from `organizations_db`.

        Raises:
            - `ValueError` if the organization type does not exist.
            - `IntegrityError` if related organizations exist.
    """
    def delete_organization_type(self, type_id):
        try:
            # Retrieve the organization type instance
            organization_type = self.using("organizations_db").get(id=type_id)

            # Check if any organizations use this type
            from organizations.models import Organization
            has_organizations = Organization.objects.using("organizations_db").filter(type_id=type_id).exists()

            if has_organizations:
                raise ValueError(
                    f"Cannot delete organization type '{organization_type.name}'. "
                    "Organizations are still associated with it."
                )

            # Delete the organization type
            organization_type.delete(using="organizations_db")
            return f"Organization Type '{organization_type.name}' (ID {type_id}) deleted successfully."

        except self.model.DoesNotExist:
            raise ValueError(f"Organization Type with ID {type_id} does not exist.")

    """
    Query Methods for OrganizationType Retrieval

    These methods allow efficient filtering and retrieval of organization types.

    - **Name-Based Queries (`by_name`, `by_id`)**
        - Retrieve organization types by their exact name or unique ID.

    - **Description-Based Queries (`with_description`, `without_description`)**
        - Filter organization types based on whether they include a description.

    - **Time-Based Queries (`recently_created`, `recently_modified`)**
        - Retrieve organization types based on their creation or last modification date.
        - Default range: last 30 days (adjustable with the `days` parameter).

    **Why These Methods?**
        - Ensures structured access to organization type data.
        - Supports **manual foreign key relationships** by allowing lookup via `by_id()`.
        - Provides consistent data retrieval for related models, such as `Organization`.
    """

    # Fetch an organization type by name (case insensitive).
    def by_name(self, name):
        return self.filter(name__iexact=name).first()
    
    # Fetch an organization type by its ID.
    def by_id(self, type_id):
        return self.filter(id=type_id).first()

    # Fetch organization types that have a description.
    def with_description(self):
        return self.exclude(description__isnull=True).exclude(description="")

    # Fetch organization types that do not have a description.
    def without_description(self):
        return self.filter(models.Q(description__isnull=True) | models.Q(description=""))

    # Fetch organization types created within the last X days (default: 30 days).
    def recently_created(self, days=30):
        return self.filter(date_created__gte=now() - timedelta(days=days))

    # Fetch organization types modified within the last X days (default: 30 days).
    def recently_modified(self, days=30):
        return self.filter(last_modified__gte=now() - timedelta(days=days))


"""
Represents a classification type for organizations.
    
    - Example Types: "Non-Profit", "Government", "Corporate", "Educational".
    - Used to categorize organizations and determine possible configurations.
    
**Manual Foreign Key Handling**:
    - `created_by_id` and `modified_by_id` reference users from `users_db`.
    - These IDs allow tracking of who created/modified the organization type.

**Tracking Fields**:
    - `date_created`: Timestamp for initial record creation.
    - `last_modified`: Auto-updated on changes.
"""

class OrganizationType(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Type Name"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Type Description"))

    # Tracking fields
    date_created = models.DateTimeField(default=now, verbose_name=_('Date Created'))
    created_by_id = models.IntegerField(null=True, blank=True, verbose_name=_("Created By ID"))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last Modified'))
    modified_by_id = models.IntegerField(null=True, blank=True, verbose_name=_("Modified By ID"))

    objects = OrganizationTypeManager()

    """
    Metadata options for the model:
        - app_label: Explicitly associates the model with its Django app.
        - verbose_name: Human-readable singular name for the model.
        - verbose_name_plural: Human-readable plural name for the model.
        - ordering: Defines the default ordering of query results. If not present, consider adding an appropriate default.

    Notes:
        - app_label is required for multi-database setups to ensure correct app referencing.
        - ordering improves query efficiency by specifying a default sort order.
        - verbose_name settings enhance readability in admin and UI interfaces.
    """

    class Meta:
        
        app_label = "organizations"
        verbose_name = _("Organization Type")
        verbose_name_plural = _("Organization Types")
        ordering = ["name"]

    """
    String Representation for OrganizationType

    - `__str__()`: Returns a formatted string representing the organization type.
        - If a description is provided, it includes a truncated version (first 50 characters).
        - Ensures clarity when displaying organization types in logs, admin, and UI.

    Why This Approach?
        - Provides meaningful representation without excessive details.
        - Helps distinguish similar organization types by displaying partial descriptions.
        - Avoids overly long outputs in dropdowns, tables, and logs.

    Example Outputs:
        - `"Non-Profit"`
        - `"Government Agency (Supports public services)"`
        - `"Educational Institution (Focuses on higher learning)"`
    """

    def __str__(self):
        truncated_description = f" ({_(self.description[:50])}...)" if self.description else ""
        return _(f"{self.name}{truncated_description}")

    """
    Manual Foreign Key Lookup Methods

    These methods manually retrieve related objects from their respective databases
        since Django does not support cross-database ForeignKey relationships.

    **Why These Methods Are Inside the `OrganizationType` Model:**
        - They allow retrieving associated users (who created or modified the type) dynamically.
        - Unlike `OrganizationTypeManager`, which handles QuerySet-level operations,
          these methods return a single related object or `None`.

    **Usage Example:**
        org_type = OrganizationType.objects.using("organizations_db").get(id=1)
        created_by_user = org_type.get_created_by()  # Fetch user who created this type
        modified_by_user = org_type.get_modified_by()  # Fetch last user who modified this type
    """

    # Fetch the creator (User) from users_db.
    def get_created_by(self):
        if self.created_by_id:
            # Import inside method to prevent circular dependencies
            from users.models import User
            return User.objects.using("users_db").filter(id=self.created_by_id).first()
        return None

    # Fetch the last modifier (User) from users_db.
    def get_modified_by(self):
        if self.modified_by_id:
            # Import inside method to prevent circular dependencies
            from users.models import User
            return User.objects.using("users_db").filter(id=self.modified_by_id).first()
        return None

"""
Custom Manager for the Organization Model

Provides optimized queries for filtering, creating, updating, and deleting organizations,
    while supporting manual foreign key handling due to multi-database constraints.

**Create, Update & Deletion Methods:**
    - `create_organization(...)`: Creates a new organization and saves it in the database.
    - `update_organization(organization_id, **updated_fields)`: Updates an existing organization
          with the provided field values.
    - `delete_organization(organization_id)`: Deletes an organization with verification.
          
**Query Methods:**
    - `active()`: Retrieves all active organizations.
    - `inactive()`: Retrieves all inactive organizations.
    - `by_name(name)`: Retrieves organizations by exact name.
    - `by_type(type_id)`: Retrieves organizations of a specific type.
    - `by_contact(contact_id)`: Retrieves organizations with a specific primary contact.
    - `requiring_mfa()`: Retrieves organizations that enforce multi-factor authentication.
    - `not_requiring_mfa()`: Retrieves organizations that do not require MFA.
    - `created_by_user(user_id)`: Retrieves organizations created by a specific user.
    - `modified_by_user(user_id)`: Retrieves organizations last modified by a specific user.
    - `recently_created(days=30)`: Retrieves organizations created within the last `X` days.
    - `recently_modified(days=30)`: Retrieves organizations modified within the last `X` days.

**Why Manual Foreign Keys?**
    - Django does not support cross-database foreign key relations.
    - Integer fields (e.g., `type_id`, `contact_id`, `created_by_id`, `modified_by_id`) are used instead of actual ForeignKey fields.
    - Query methods work by filtering based on these integer IDs.

**Usage Example:**
    - `organizations = Organization.objects.active()`
    - `recent_organizations = Organization.objects.recently_created(days=7)`
"""


class OrganizationManager(models.Manager):
    
    """
    Creates and returns an Organization instance with the given details.

    Args:
        - `name` (str): The name of the organization (required).
        - `type_id` (int, optional): The ID of the organization type.
        - `active` (bool, optional): Whether the organization is active.
        - `contact_id` (int, optional): ID of the primary contact.
        - `login_options` (dict, optional): JSON field storing login preferences.
        - `mfa_required` (bool, optional): Whether MFA is required.
        - `created_by_id` (int, optional): The ID of the user who created this organization.

    Returns:
        Organization: A new Organization instance.
    """
    
    def create_organization(self, name, type_id=None, active=True, contact_id=None, login_options=None, mfa_required=False, created_by_id=None):
        
        organization = self.model(
            name=name,
            type_id=type_id,
            active=active,
            contact_id=contact_id,
            login_options=login_options or {},
            mfa_required=mfa_required,
            created_by_id=created_by_id,
        )
        organization.save(using=self._db)
        return organization

    """
    Updates an existing organization with provided fields.

    Args:
        - `organization_id` (int): The ID of the organization to update.
        - `updated_fields` (dict): Fields to update.

    Returns:
        Organization: The updated Organization instance or None if not found.
    """
    
    def update_organization(self, organization_id, **updated_fields):
        
        organization = self.filter(id=organization_id).first()
        if organization:
            for field, value in updated_fields.items():
                setattr(organization, field, value)
            organization.save(using=self._db)
        return organization
    
    """
        Deletes an organization from the organizations_db.

        **Usage Example:**
            - `Organization.objects.delete_organization(organization_id=10)`

        **Handles:**
            - Ensuring the organization exists before deletion.
            - Preventing deletion if related records (users, sites, contacts) exist.
            - Removing the organization only from `organizations_db`.

        Raises:
            - `ValueError` if the organization does not exist.
            - `IntegrityError` if related records exist (e.g., users, sites, contacts).
    """
    def delete_organization(self, organization_id):
        try:
            # Retrieve the organization instance
            organization = self.using("organizations_db").get(id=organization_id)

            # Check for related records before deletion
            from users.models import User
            from sites.models import Site
            from organizations.models import OrganizationContact

            has_users = User.objects.using("users_db").filter(organization_id=organization_id).exists()
            has_sites = Site.objects.using("sites_db").filter(organization_id=organization_id).exists()
            has_contacts = OrganizationContact.objects.using("organizations_db").filter(organization_id=organization_id).exists()

            if has_users or has_sites or has_contacts:
                raise ValueError(
                    f"Cannot delete organization {organization.name}. "
                    "Users, sites, or contacts are still associated with it."
                )

            # Delete the organization
            organization.delete(using="organizations_db")
            return f"Organization '{organization.name}' (ID {organization_id}) deleted successfully."

        except self.model.DoesNotExist:
            raise ValueError(f"Organization with ID {organization_id} does not exist.")
    
    """
    Query Methods for Organization Retrieval

    These methods retrieve organizations based on specific attributes.

    - **Status-Based Queries (`active`, `inactive`)**
        - Retrieve organizations based on whether they are currently active or inactive.

    - **Attribute-Based Queries (`by_name`, `by_type`, `by_contact`)**
        - Allow searching for organizations by name, type, or primary contact.

    - **Security & Compliance Queries (`requiring_mfa`, `not_requiring_mfa`)**
        - Identify organizations based on their Multi-Factor Authentication (MFA) policies.

    - **Tracking Queries (`created_by_user`, `modified_by_user`, `recently_created`, `recently_modified`)**
        - Retrieve organizations based on when they were created or last modified.
        - `recently_created()` and `recently_modified()` allow dynamic time filtering (default: last 30 days).

    **Why These Methods?**
        - Efficient retrieval and filtering of organizations for better UI and reporting.
        - Supports **manual foreign key management** across different databases.
    """

    # Returns all active organizations, prefetching related data for efficiency
    def active(self):
        return self.filter(active=True)

    # Returns all inactive organizations
    def inactive(self):
        return self.filter(active=False)

    # Returns organizations filtered by exact name, ensuring efficient lookup
    def by_name(self, name):
        return self.filter(name=name)

    # Returns all organizations by type, prefetching related organization type
    def by_type(self, type_id):
        return self.filter(type_id=type_id)

    # Returns all organizations that require MFA
    def requiring_mfa(self):
        return self.filter(mfa_required=True)

    # Returns all organizations that do not require MFA
    def not_requiring_mfa(self):
        return self.filter(mfa_required=False)

    # Returns all organizations created by a specific user
    def created_by_user(self, user_id):
        return self.filter(created_by_id=user_id)

    # Returns all organizations modified by a specific user
    def modified_by_user(self, user_id):
        return self.filter(modified_by_id=user_id)

    # Returns all organizations created in the last X days (default: 30)
    def recently_created(self, days=30):
        return self.filter(date_created__gte=now() - timedelta(days=days))

    # Returns all organizations modified in the last X days (default: 30)
    def recently_modified(self, days=30):
        return self.filter(last_modified__gte=now() - timedelta(days=days))

"""
Represents an organization within the system.

This model stores key details about an organization, such as its name, type, 
    primary contact, authentication settings, and activity status. Due to multi-database 
    constraints, foreign key relationships are manually managed.

**Fields:**
    - `name`: Unique identifier for the organization.
    - `type_id`: Manages the relationship to `OrganizationType` manually.
    - `active`: Boolean flag indicating whether the organization is currently active.
    - `contact_id`: References the primary contact for the organization.
    - `login_options`: Stores authentication-related options in JSON format.
    - `mfa_required`: Determines whether multi-factor authentication is enforced.

**Tracking Fields:**
    - `date_created`: Timestamp indicating when the organization was added.
    - `created_by_id`: Tracks the user who created this organization.
    - `last_modified`: Auto-updates when modifications occur.
    - `modified_by_id`: Tracks the user who last modified this record.

**Why Manual Foreign Keys?**
    - Django does not support cross-database foreign key relations.
    - `get_type()`, `get_contact()`, `get_created_by()`, and `get_modified_by()`
        dynamically retrieve related objects from the appropriate database.

**Additional Features:**
    - `is_active_label`: Returns a user-friendly representation of the active status.
    - `__str__()`: Provides a formatted string including organization name, type, and active status.

**Example Usage:**
    organization = Organization.objects.using("organizations_db").get(id=1)
    organization_type = organization.get_type()  # Retrieves associated organization type
    organization_contact = organization.get_contact()  # Retrieves associated primary contact
    created_by_user = organization.get_created_by()  # Retrieves the user who created this organization
    modified_by_user = organization.get_modified_by()  # Retrieves the user who last modified this organization
"""

class Organization(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Organization Name'))
    type_id = models.IntegerField(null=True, blank=True, verbose_name=_("Type ID"))
    active = models.BooleanField(default=True, verbose_name=_('Organization Active'))
    contact_id = models.IntegerField(null=True, blank=True, verbose_name=_("Contact ID"))
    login_options = models.JSONField(default=dict, verbose_name=_("Login Options"))
    mfa_required = models.BooleanField(default=False, verbose_name=_("MFA Required"))

    # Tracking fields
    date_created = models.DateTimeField(default=now, verbose_name=_('Date Created'))
    created_by_id = models.IntegerField(null=True, blank=True, verbose_name=_("Created By ID"))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last Modified'))
    modified_by_id = models.IntegerField(null=True, blank=True, verbose_name=_("Modified By ID"))

    objects = OrganizationManager()

    """
    Metadata options for the model:
        - app_label: Explicitly associates the model with its Django app.
        - verbose_name: Human-readable singular name for the model.
        - verbose_name_plural: Human-readable plural name for the model.
        - ordering: Defines the default ordering of query results. If not present, consider adding an appropriate default.

    Notes:
        - app_label is required for multi-database setups to ensure correct app referencing.
        - ordering improves query efficiency by specifying a default sort order.
        - verbose_name settings enhance readability in admin and UI interfaces.
    """

    class Meta:
        app_label = "organizations"
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        ordering = ["name", "-active", "-date_created"]

    """
    String Representation and Active Status for Organization

    - `is_active_label`: Converts the boolean `active` field into `"Active"` or `"Inactive"`.
    - `__str__()`: Provides a formatted string containing:
        - Organization name
        - Organization type (retrieved via `get_type()`)
        - Active status (`Active` / `Inactive`)

    Why These Methods?
        - Ensures consistency and clarity when displaying organizations in logs, admin, and UI.
        - Allows `__str__()` to provide more meaningful information beyond just the organization name.
        - Uses a manual lookup (`get_type()`) since ForeignKey relationships are not available.
        - Helps differentiate between organizations with similar names by showing additional context.
    """

    @property
    
    # Returns a human-readable label for the active status.
    def is_active_label(self):
        return _("Active") if self.active else _("Inactive")

    # String representation of an Organization, including type and status.
    def __str__(self):
        organization_type = self.get_type()
        type_name = organization_type.name if organization_type else _("Unknown Type")
        return _(f"{self.name} ({type_name} - {self.is_active_label})")
    
    """
    These methods manually retrieve related objects from their respective databases
    due to Django’s lack of native cross-database ForeignKey support.

    **Why These Methods Are Inside the `Organization` Model:**
        - They operate at the instance level, dynamically fetching related records.
        - They allow retrieval of associated organization types, contacts, and users without an actual ForeignKey.
        - Unlike `OrganizationManager`, which handles QuerySet-level operations, these methods
        return a single related object or `None`.

    **Usage Example:**
        organization = Organization.objects.using("organizations_db").get(id=1)
        organization_type = organization.get_type()  # Fetch associated organization type
        organization_contact = organization.get_contact()  # Fetch associated primary contact
        created_by_user = organization.get_created_by()  # Fetch the creator of the organization
        modified_by_user = organization.get_modified_by()  # Fetch the last user who modified the organization
    """

    # Fetch the organization type from organizations_db.
    def get_type(self):
        if self.type_id:
            return OrganizationType.objects.using("organizations_db").filter(id=self.type_id).first()
        return None

    # Fetch the organization contact from organizations_db.
    def get_contact(self):
        if self.contact_id:
            return OrganizationContact.objects.using("organizations_db").filter(id=self.contact_id).first()
        return None

    # Fetch the creator (User) from users_db.
    def get_created_by(self):
        if self.created_by_id:
            # Keep import inside method when doing cross app references.
            from users.models import User
            return User.objects.using("users_db").filter(id=self.created_by_id).first()
        return None

    # Fetch the last modifier (User) from users_db.
    def get_modified_by(self):
        if self.modified_by_id:
            # Keep import inside method when doing cross app references.
            from users.models import User
            return User.objects.using("users_db").filter(id=self.modified_by_id).first()
        return None

"""
Custom Manager for OrganizationContact Model

Provides optimized queries for filtering, creating, updating, and deleting contacts,
    while supporting manual foreign key handling due to multi-database constraints.

**Create, Update & Deletion Methods:**
    - `create_contact(...)`: Creates a new contact and saves it in the database.
    - `update_contact(contact_id, **updated_fields)`: Updates an existing contact
        with the provided field values.
    - `delete_contact(contact_id)`: Deletes a contact with verification.

**Query Methods:**
    - `by_first_name(first_name)`: Retrieve contacts by first name (case-insensitive).
    - `by_last_name(last_name)`: Retrieve contacts by last name (case-insensitive).
    - `by_full_name(first_name, last_name)`: Retrieve contacts by full name.
    - `from_organization(organization_id)`: Retrieve contacts belonging to a specific organization.
    - `with_role(role)`: Retrieve contacts with a specific role in an organization.
    - `created_by_user(user_id)`: Retrieve contacts created by a specific user.
    - `modified_by_user(user_id)`: Retrieve contacts last modified by a specific user.
    - `recently_created(days=30)`: Retrieve contacts created within the last X days (default: 30).
    - `recently_modified(days=30)`: Retrieve contacts modified within the last X days (default: 30).
    - `active_contacts()`: Retrieve contacts linked to active organizations.
    - `inactive_contacts()`: Retrieve contacts linked to inactive organizations.

**Notes:**
    - Methods interacting with organizations require **manual database queries** due to cross-database constraints.
    - Queries involving `organization_id` retrieve organization states **before** filtering contacts.
"""

class ContactManager(models.Manager):
    
    """
    Creates and returns an OrganizationContact instance.

    Args:
        - `organization_id` (int, required): The ID of the associated organization.
        - `first_name` (str, optional): First name of the contact.
        - `last_name` (str, optional): Last name of the contact.
        - `email` (str, optional): Email of the contact.
        - `phone_number` (str, optional): Contact's phone number.
        - `address` (str, optional): Contact's address.
        - `role` (str, optional): Contact's role in the organization.
        - `created_by_id` (int, optional): ID of the user who created this contact.

    Returns:
        OrganizationContact: A new OrganizationContact instance.
    """

    def create_contact(self, organization_id, first_name=None, last_name=None, email=None, phone_number=None, address=None, role=None, created_by_id=None):

        contact = self.model(
            organization_id=organization_id,
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
        OrganizationContact: The updated OrganizationContact instance or None if not found.
    """

    def update_contact(self, contact_id, **updated_fields):
        
        contact = self.filter(id=contact_id).first()
        if contact:
            for field, value in updated_fields.items():
                setattr(contact, field, value)
            contact.save(using=self._db)
        return contact

    """
        Deletes a contact from the organizations_db.

        **Usage Example:**
            - `OrganizationContact.objects.delete_contact(contact_id=5)`

        **Handles:**
            - Ensuring the contact exists before deletion.
            - Removing the contact only from `organizations_db`.
        
        Raises:
            - `ValueError` if the contact does not exist.
    """
    def delete_contact(self, contact_id):
        try:
            # Retrieve the contact instance
            contact = self.using("organizations_db").get(id=contact_id)

            # Delete the contact
            contact.delete(using="organizations_db")
            return f"Contact with ID {contact_id} deleted successfully."

        except self.model.DoesNotExist:
            raise ValueError(f"Contact with ID {contact_id} does not exist.")

    """
    Query Methods for Contact Retrieval

    These methods retrieve contacts based on various filters and constraints.

    - Name-Based Queries (`by_first_name`, `by_last_name`, `by_full_name`):
        - Allow searching for contacts based on partial or full name matches.
        - Case-insensitive queries are used for better usability.

    - Organization & Role Queries (`from_organization`, `with_role`):
        - Fetch contacts belonging to a specific organization or holding a specific role.
    
    - Tracking Queries (`created_by_user`, `modified_by_user`, `recently_created`, `recently_modified`):
        - Retrieve contacts based on when they were created or modified.
        - `recently_created()` and `recently_modified()` allow dynamic time filtering (default: last 30 days).

    - Organization Status Queries (`active_contacts`, `inactive_contacts`):
        - Fetch contacts based on whether their linked organization is active or inactive.

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
    
    # Returns all contacts from a specific organization
    def from_organization(self, organization_id):
        return self.filter(organization_id=organization_id)

    # Returns all contacts with a specific role
    def with_role(self, role):
        return self.filter(role=role)

    # Returns all contacts created by a specific user
    def created_by_user(self, user_id):
        return self.filter(created_by_id=user_id)

    # Returns all contacts modified by a specific user
    def modified_by_user(self, user_id):
        return self.filter(modified_by_id=user_id)
    
    # Returns all contacts created in the last X days (default: 30)
    def recently_created(self, days=30):
        return self.filter(date_created__gte=now() - timedelta(days=days))

    # Returns all contacts modified in the last X days (default: 30)
    def recently_modified(self, days=30):
        return self.filter(last_modified__gte=now() - timedelta(days=days))
    
    # Returns all contacts associated with active organizations
    def active_contacts(self):
        active_org_ids = Organization.objects.using("organizations_db").filter(active=True).values_list('id', flat=True)
        return self.filter(organization_id__in=active_org_ids)
    
    # Returns all contacts associated with inactive organizations
    def inactive_contacts(self):
        inactive_org_ids = Organization.objects.using("organizations_db").filter(active=False).values_list('id', flat=True)
        return self.filter(organization_id__in=inactive_org_ids)

"""
Represents a contact person associated with an organization.

This model stores contact details such as name, email, phone number, and role
    within an organization. Relationships to organizations and users (for tracking)
    are managed manually due to multi-database constraints.

**Fields:**
    - `organization_id`: Manually manages the foreign key to an organization.
    - `first_name`, `last_name`: Contact's full name (either can be optional).
    - `email`, `phone_number`: Preferred communication methods.
    - `address`: Mailing address for reference.
    - `role`: Job title or function within the organization.

**Tracking Fields:**
    - `date_created`: Timestamp when the contact was added.
    - `created_by_id`: Tracks the user who created this contact.
    - `last_modified`: Auto-updates when changes occur.
    - `modified_by_id`: Tracks the user who last modified this record.

**Why Manual Foreign Keys?**
    - Django does not support cross-database foreign key relations.
    - `get_organization()`, `get_created_by()`, and `get_modified_by()` methods
        dynamically retrieve related objects from the appropriate database.

Example Usage:
    contact = OrganizationContact.objects.using("organizations_db").get(id=1)
    organization = contact.get_organization()  # Retrieves associated organization
    creator = contact.get_created_by()  # Retrieves the user who added this contact
"""

class OrganizationContact(models.Model):
    id = models.BigAutoField(primary_key=True)
    organization_id = models.IntegerField(null=True, blank=True, verbose_name=_("Organization ID"))
    first_name = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('Last Name'))
    email = models.EmailField(null=True, blank=True, verbose_name=_('Email Address'))
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('Phone Number'))
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Organization Mailing Address'))
    # Role in the organization (e.g., CEO, Manager)
    role = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Role'))

    # Tracking fields
    date_created = models.DateTimeField(default=now, verbose_name=_('Date Created'))
    created_by_id = models.IntegerField(null=True, blank=True, verbose_name=_("Created By ID"))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last Modified'))
    modified_by_id = models.IntegerField(null=True, blank=True, verbose_name=_("Modified By ID"))

    objects = ContactManager()

    """
    Metadata options for the model:
        - app_label: Explicitly associates the model with its Django app.
        - verbose_name: Human-readable singular name for the model.
        - verbose_name_plural: Human-readable plural name for the model.
        - ordering: Defines the default ordering of query results. If not present, consider adding an appropriate default.

    Notes:
        - app_label is required for multi-database setups to ensure correct app referencing.
        - ordering improves query efficiency by specifying a default sort order.
        - verbose_name settings enhance readability in admin and UI interfaces.
    """

    class Meta:
        app_label = "organizations"
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')
        ordering = ["last_name", "first_name", "organization_id", "role", "-date_created"]


    """
    String Representation and Naming for OrganizationContact
        - `name()`: Computes the full name of the contact, handling cases where first or last name may be missing.
        - `__str__()`: Returns a formatted string representing the contact and their associated organization.

    Why These Methods?
        - Ensures consistent and user-friendly identification of contacts across the application.
        - Handles missing name fields gracefully to avoid returning empty strings.
        - Uses a manual lookup (`get_organization()`) to retrieve the organization name since ForeignKey relationships are not used.
        - Provides meaningful output even when organization data is unavailable.
    """

    @property
    def name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.first_name or self.last_name or _("Unnamed Contact")


    def __str__(self):
        organization = self.get_organization()
        organization_name = organization.name if organization else _('No Organization')
        return _(f"{self.name} ({organization_name})")

    """
    Manual Foreign Key Lookup Methods

    These methods manually retrieve related objects from their respective databases
        due to Django’s lack of native cross-database ForeignKey support.

    Why These Methods Are Inside the `OrganizationContact` Model:
        - They operate at the instance level, dynamically fetching related records.
        - They allow retrieval of associated organizations and users without an actual ForeignKey.
        - Unlike `ContactManager`, which handles QuerySet-level operations, these methods
            return a single related object or `None`.

    Usage Example:
        contact = OrganizationContact.objects.using("organizations_db").get(id=1)
        organization = contact.get_organization()  # Fetch associated organization
        created_by_user = contact.get_created_by()  # Fetch the creator of the contact
    """

    def get_organization(self):
        if self.organization_id:
            org = Organization.objects.using("organizations_db").filter(id=self.organization_id, active=True).first()
            return org if org else _("Deleted Organization")
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



    print("DEBUG: Finished loading models for organizations app.") 