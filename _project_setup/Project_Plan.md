# GWIIT Capstone Project Plan

## GWIIT: General Workplace Inventory and Inspection Tool

**GWIIT** (*General Workplace Inventory and Inspection Tool*) is a **multi-tenant platform** designed to help organizations with Health, Safety, and Environmental (**HSE**) management needs to **manage HSE inventory, perform HSE inspections, and maintain compliance** with **HSE regulations and policies**. The system will provide **centralized record-keeping**, **structured data storage**, and **scalable backend functionality** to support future development.

---

## Long-Term Vision

The **fully implemented version** of GWIIT will:

- Support **customizable inspection checklists** for compliance with **OSHA, NFPA, and other regulatory standards**.
- Provide **task scheduling, automated notifications, and QR code tracking** for seamless inventory management.
- Feature a **ticketing system** for maintenance tracking and compliance resolution.
- Offer **advanced analytics and reporting** for data-driven decision-making.
- Include **offline capabilities** to allow inspections to be conducted without an internet connection.
- Integrate with **external authentication providers** (OAuth, LDAP) for enterprise security needs.
- Support **fully developed role-based access control (RBAC)** to grant granular permissions.

---

## Short-Term Capstone Implementation

For this **first version**, GWIIT will focus on building the **foundational backend architecture** needed for future development along side basic frontend architecture and functionality. The **Capstone iteration** will include:

### Basic User Authentication & Session Management
- Standard **Django authentication** with **session handling via Redis**.
- **Multi-tenancy foundation** (not fully developed, but supports future scaling).

### Organizational Structure & Data Models
- **User, Organization, and Site models** with proper **associations**.
- **Cross-database communication** between different Django apps (ensuring database routing/signals work).
- **SQLite3 databases** used for **development purposes**—not production-ready.

### Basic Inventory & Site Management
- Ability to **create, modify, and delete** organizations, sites, and users.
- **General user-organization-site association management** (no preferences/settings yet).
- **Focus on backend structure** rather than front-end functionality.

### Early-Stage Role-Based Access Control (RBAC)
- **Limited, basic roles** (e.g., Admin vs. User).
- No **granular permission settings**, but **foundation built** for future enhancement.

### Custom Django API for Organization & Site Management
- The **Django backend serves as an internal API**, providing:
  - **User authentication & session management**
  - **Multi-tenant organization/site/user management**
  - **Data retrieval & association queries**
- The frontend can request data from the backend via **Django’s built-in views or Django REST Framework (DRF) endpoints**.

---

### Key Limitations for Capstone Submission
**No external Multi-Factor Authentication (MFA) integration**—only basic session management.  
**No advanced RBAC features**—only basic admin/user distinction.   
**No preference settings or user-specific customizations**—only essential model relationships.  
**No inspection, reporting, task management, ticketing, or auditing features in this phase.**  

---
## Feature #1: Use Arrays, Objects, Sets, or Maps to Store and Retrieve Information

### Capstone Definition
Use arrays, objects, sets or maps to store and retrieve information that is displayed in your app.

---

### How GWIIT Implements This

#### Django ORM Stores Users, Organizations, and Sites as Structured Objects for the Front-End
The backend stores structured data in **Django ORM models**, allowing the front-end to retrieve and display it dynamically.

#### How This Affects the Front-End
- The front-end requests stored data (e.g., users, sites, and organizations) to **populate dropdown menus, tables, and user profiles**.
- Data is fetched via **API endpoints** that return JSON responses.

---

#### QuerySets Allow the Front-End to Filter & Retrieve Data

QuerySets in Django allow **structured** data retrieval and filtering, making them functionally similar to arrays, objects, and maps.

How This Affects the Front-End
The front-end requests filtered data to dynamically update UI components like search results, dropdowns, and reports.
Query parameters are passed in API calls to fetch only the necessary data.

#### Example: Retrieving Active User Data via API
The front end calls the API using the **Fetch API**, passing query parameters (`?active=true`).

**Example API Call:**
```javascript
fetch("/api/users/?active=true")
  .then(response => response.json())
  .then(data => {
    console.log(data); // Returns only active users
  });
```
The front-end does not interact with the database directly but instead sends requests to the **Django API** to retrieve and display this data.  

In the backend, The Request is Handled by a Django View (`views.py`) for the app being called. 

- The Django view receives the request, checks for **query parameters** (`?active=true`), and decides what data to retrieve.

    - This determines whether to return all users or only active users before querying the database.

**Example view method:**
```Python
def get_users(request):
    active = request.GET.get("active")  # Check if "active=true" was passed
    users = User.objects.filter(is_active=True) if active else User.objects.all()

    users_data = list(users.values("id", "email", "first_name", "last_name", "organization_id", "site_id"))
    return JsonResponse({"users": users_data})
```

- The view calls the **ModelManager** class in `models.py` to retrieve the relevant QuerySet from the methods in the manager.

**Example ModelManager:**
```Python
class UserManager(models.Manager):
    def active_users(self):
        return self.filter(is_active=True)
```
The **Django ORM** translates the QuerySet into an SQL query and fetches the requested data.

- The **User Model** in `models.py` defines the structure of user data in the database.

#### Example User Model
``` Python
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    organization = models.ForeignKey("organizations.Organization", null=True, on_delete=models.SET_NULL)
    site = models.ForeignKey("sites.Site", null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    def __str__(self):
        return self.email
```
The SQL query for this example would look like this:

**Example SQL quesry:**
``` SQL
SELECT "users_user"."id",
       "users_user"."email",
       "users_user"."first_name",
       "users_user"."last_name",
       "users_user"."organization_id",
       "users_user"."site_id"
FROM "users_user"
WHERE "users_user"."is_active" = TRUE;
```
The SQL response from the query is returned in Python as tuples.

**Example SQL response to Python:**
``` Python
[
    (1, "john.doe@example.com", "John", "Doe", 2, 5),
    (2, "jane.smith@example.com", "Jane", "Smith", 3, 7)
]
```
**Django** ORM converts the SQL response into Python dictionaries using `values()`

- This can also be a serializer, but our example of **view** above is using `values()`.

```Python
users_data = list(users.values("id", "email", "first_name", "last_name", "organization_id", "site_id"))
```

The response is then made as a `JSONResponse` since our example **view** from above is returning in that format.

```Python
return JsonResponse({"users": list(users)})
```

This will send the frontend the response in the JSON format for it to use.

**Example JSON format:**
```JSON
{
  "users": [
    {
      "id": 1,
      "email": "john.doe@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "organization_id": 2,
      "site_id": 5
    },
    {
      "id": 2,
      "email": "jane.smith@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "organization_id": 3,
      "site_id": 7
    }
  ]
}
```

## Feature #2: Analyze Data Stored in Arrays, Objects, Sets, or Maps and Display Insights

### Capstone Definition
Extract meaningful information from stored data (e.g., filter, count, summarize).

---

### How GWIIT Implements This

### Django Admin Panel Provides Data Filtering, Counting, and Summarizing

Django’s **Admin Panel** provides for **managing, filtering, and analyzing data dynamically**. Instead of requiring custom queries for every analysis, Django’s admin interface allows for **efficient data management through QuerySets, model managers, and direct database queries.**

#### How This Affects the Front-End
- **Admin users can dynamically filter and search records** without needing additional API calls.
- **User counts and summaries are displayed directly in the admin panel** to help administrators make decisions.
- **Sorting and ordering allow admins to quickly structure large datasets**.
- **Batch actions allow efficient bulk processing** of records.

---

## How Django Admin Panel Works with data in the Database

### Filtering and Searching Data in the Admin Panel

The **Admin Panel dynamically generates QuerySets** based on filtering and searching configurations in `admin.py`.

#### Example Querying Active Users via the Admin Panel:

```Python
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "organization", "is_active")
    list_filter = ("organization", "is_active")
    search_fields = ("email", "first_name", "last_name")
```
Django automatically generates SQL queries based on filter selections.
- **`list_filter`**: Allows filtering by organization and active status.
- **`search_fields`**: Enables quick lookups by name or email.

#### Example SQL Query from Admin Panel for filter `is_active`:
```Python
SELECT * FROM "users_user"
WHERE "users_user"."is_active" = TRUE;
```
- This query is dynamically executed when a filter is selected in the Admin Panel.

The admin panel through `admin.py` can be configured for custom filters and advanced querying.

- Based on the custom filter or query, DJango will dynamically convert it into an SQL query.

#### Example Custom Filter for "Users by Last Login":
```Python
class LastLoginFilter(admin.SimpleListFilter):
    title = "Last Login"
    parameter_name = "last_login"

    def lookups(self, request, model_admin):
        return [
            ("last_7_days", "Last 7 Days"),
            ("last_30_days", "Last 30 Days"),
            ("never_logged_in", "Never Logged In")
        ]

    def queryset(self, request, queryset):
        if self.value() == "last_7_days":
            return queryset.filter(last_login__gte=now() - timedelta(days=7))
        if self.value() == "last_30_days":
            return queryset.filter(last_login__gte=now() - timedelta(days=30))
        if self.value() == "never_logged_in":
            return queryset.filter(last_login__isnull=True)
        return queryset

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ["organization", "is_active", LastLoginFilter]
```
Based on the custom filter created, the **Admin** user will be able to select from a drop down `Last 7 Days` and DJango will create the SQL query based on the selection.

#### Example SQL Query for `Last 7 Days` filter:
```Python
SELECT * FROM "users_user"
WHERE "users_user"."last_login" >= NOW() - INTERVAL '7 days';
```
---
### Counting and Summarizing Data in the Admin Panel

The **Admin Panel** can display custom counts by adding a custom method inside `admin.py`.

#### Example of Custom Count for Users Per Organization

```Python
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "num_users")  # Displays name and user count

    def num_users(self, obj):
        return obj.user_set.count()  # Counts related users
    num_users.short_description = "User Count"  # Column name in the Admin Panel
```
From this, Django will automatically execute an SQL query and render results to the **Admin Panel**

#### Example SQL query for Count for Users Per Organization

```SQL
SELECT "organizations_organization"."id",
       "organizations_organization"."name",
       COUNT("users_user"."id") AS "num_users"
FROM "organizations_organization"
LEFT JOIN "users_user"
ON "organizations_organization"."id" = "users_user"."organization_id"
GROUP BY "organizations_organization"."id";
```
---

### Sorting and Ordering Data in the Admin Panel
By default, Django does not allow sorting by custom methods in the **Admin Panel**.  However, it can be enabled through methods in the `admin.py` file.

```Python
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "num_users")
    ordering = ("-num_users",)  # Sorts organizations by user count (descending)

    def num_users(self, obj):
        return obj.user_set.count()
    num_users.short_description = "User Count"
    num_users.admin_order_field = "user__count"  # Enables sorting
```

From this, DJango will create the query for a custom sort.

#### Example SQL query for Sorting by User Count
```SQL
SELECT "organizations_organization"."id",
       "organizations_organization"."name",
       COUNT("users_user"."id") AS "num_users"
FROM "organizations_organization"
LEFT JOIN "users_user"
ON "organizations_organization"."id" = "users_user"."organization_id"
GROUP BY "organizations_organization"."id"
ORDER BY "num_users" DESC;
```
---

## Feature #3: Use a Regular Expression (Regex) to Validate User Input

### Capstone Definition
Prevent invalid input by validating data (e.g., email validation, password rules).

---

## How GWIIT Implements This

### Regex Validation for Passwords in Authentication System
GWIIT uses **regular expressions (regex) for password validation**, ensuring that user-provided data meets security and formatting standards.

This is done through a custom validator created in the `validators.py` file.

```Python
class CustomPasswordValidator:
    """
    Enforces password rules:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one special character (@, #, $, etc.)
    - At least one digit
    """
    
    def validate(self, password, user=None):
        """Checks if the password meets the complexity requirements."""
        if not re.search(r'[A-Z]', password):
            raise ValidationError(_("Password must contain at least one uppercase letter."), code='password_no_upper')
        if not re.search(r'[a-z]', password):
            raise ValidationError(_("Password must contain at least one lowercase letter."), code='password_no_lower')
        if not re.search(r'\d', password):
            raise ValidationError(_("Password must contain at least one digit."), code='password_no_digit')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\'\\|,.<>?/]', password):
            raise ValidationError(_("Password must contain at least one special character."), code='password_no_special')

    def get_help_text(self):
        """Returns a description of the password rules."""
        return _(
            "Your password must contain at least one uppercase letter, one lowercase letter, "
            "one special character (@, #, $, etc.), and one digit."
        )
```

The validator being placed on the backend will ensure that injection into the backend, while bypassing the frontend requires the same level of password security.

The frontend will validate passwords through the same level of validation logic via JavaScript.  

This will:
- Prevent unnecessary backend requests for invalid passwords.
- Give instant feedback to users instead of waiting for a backend response.
- Ensure passwords meet security standards before they are submitted.

```javascript
function validatePassword(password) {
    const errors = [];

    if (!/[A-Z]/.test(password)) {
        errors.push("Password must contain at least one uppercase letter.");
    }
    if (!/[a-z]/.test(password)) {
        errors.push("Password must contain at least one lowercase letter.");
    }
    if (!/\d/.test(password)) {
        errors.push("Password must contain at least one digit.");
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};:"'\\|,.<>?/]/.test(password)) {
        errors.push("Password must contain at least one special character.");
    }

    return errors;
}

// Example usage:
const password = "weakPassword";
const validationErrors = validatePassword(password);

if (validationErrors.length > 0) {
    console.log("Password does not meet security requirements:");
    console.log(validationErrors.join("\n"));
} else {
    console.log("Password is valid.");
}

```
---
### Regex Validation for emails in Authentication System
GWIIT uses **regular expressions (regex) for email normalization**, ensuring that user-provided data meets security and formatting standards.

This is done through a method in the "UserManager" of the `models.py` file.  The `UserManger` is what allows for the creation and modification of users.  So this method will ensure emails are normalized before a user is created or modified.

```Python
def normalize_email(self, email):
        if not email:
            # Allow None values ("None handled module creat_user)
            return None
    
        email = email.lower().strip()

        r""" Regex for basic email validation
            Ensures email format follows standard structure:
            - Starts with alphanumeric characters, underscores, dots, plus, or hyphens.
                - ^[a-zA-Z0-9_.+-]+
            - Contains exactly one "@" symbol separating the local part and domain, but allows for subdomains (e.g., "user@mail.example.com").
                - @
            - Domain must contain at least one dot (".") to indicate a valid TLD.
                - \.
            - Ends with valid TLD (e.g., .com, .co.uk)
                - [a-zA-Z0-9-.]+$
            - Prevents spaces, special characters like "!", "#", "$", etc., outside of allowed ones.
        """
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, email):
            raise ValueError(f"Invalid email format: {email}")

        return email
```
The normalizer being placed on the backend will ensure that injection into the backend, while bypassing the frontend requires the same level of normalization for the email.

The frontend will normalize emails through the same level of logic via JavaScript.

This will:
- Prevent unnecessary backend requests for invalid emails.
- Give instant feedback to users instead of waiting for a backend response.
- Ensure emails meet standards before they are submitted.

```javascript
function normalizeEmail(email) {
    if (!email) {
        return null; // Allow null/undefined values (like the backend)
    }

    email = email.toLowerCase().trim();

    // Regex for basic email validation (mirrors Python regex)
    const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;

    if (!emailRegex.test(email)) {
        throw new Error(`Invalid email format: ${email}`);
    }

    return email;
}

// Example usage:
try {
    console.log(normalizeEmail("  USER@example.COM  "));  // "user@example.com"
    console.log(normalizeEmail("invalid-email@com"));     // Throws error
} catch (error) {
    console.error(error.message);
}
```
### DJango built-in Authentication System
Django provides **built-in validators** for common fields like **Passwords** and **emails**.

#### **Example Email Validation using Django Built-in
```python
from django.core.validators import EmailValidator
from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True, validators=[EmailValidator()])
```

#### Example SQL Constraint Automatically Applied
``` SQL
ALTER TABLE users_user ADD CONSTRAINT users_user_email_check 
CHECK (email ~* '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$');
```
- The database enforces valid email formats at the SQL level.
---

## Feature #4: Create a Function That Accepts Two or More Input Parameters and Returns a Calculated Result

### Capstone Definition
Must be more complex than basic math functions.

---

## How GWIIT Implements This

Retrieving Active Users from a Specific Site Within an Organization

GWIIT allows filtering **users by both organization and site**, ensuring that only **relevant active users** are retrieved.


### How This Affects the Front-End
- **The API allows front-end users to filter active users by organization and site.**
- **Reduces unnecessary data fetching**, improving front-end efficiency.
- **Ensures only authorized users appear in dropdowns, tables, or reports.**

---

## How Django Uses Functions with Multiple Parameters

### Custom QuerySet Method to Retrieve Users by Organization and Site

Django’s ORM supports **multi-parameter filtering** through model managers.

Example: Retrieving Active User for a Specific Site and Organization via API

The front end calls the API using the Fetch API, passing query parameters.

- `"organizations/2/"`
- `"sites/5/"`
- `"active-users/"`

#### Example API call for Active Users from a Specific Site and Organization
```javascript
fetch("/api/organizations/2/sites/5/active-users/")
  .then(response => response.json())
  .then(data => {
    console.log(data); // Returns active users for Site ID 5 in Organization ID 2
  });
```

#### Example View That Retrieves Active Users by Organization and Site
```Python
def get_active_users_by_site(request, org_id, site_id):
    users = User.objects.active_users_by_site(org_id, site_id)
    users_data = list(users.values("id", "email", "first_name", "last_name"))
    return JsonResponse({"users": users_data})
```

- The function is executed dynamically based on `"org_id"` and s`"ite_id"` provided in the request.
- The API returns only active users from the given organization and site.

- The view calls the **ModelManager** class in `models.py` to retrieve the relevant QuerySet from the methods in the manager.

#### Example Filtering for Active Users by Organization and Site in the ModelManager (`models.py`)

```python
class UserManager(models.Manager):
    def active_users_by_site(self, org_id, site_id):
        return self.filter(organization_id=org_id, site_id=site_id, is_active=True)
```
- This function requires both org_id and site_id, ensuring precise filtering.
- The function is reusable across different views and API calls.

The **Django ORM** translates the QuerySet into an SQL query and fetches the requested data.

- The **User Model** in `models.py` defines the structure of user data in the database.

#### Example User Model
``` Python
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    organization = models.ForeignKey("organizations.Organization", null=True, on_delete=models.SET_NULL)
    site = models.ForeignKey("sites.Site", null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    def __str__(self):
        return self.email
```

#### Example SQL Query Generated
```SQL
SELECT * FROM "users_user"
WHERE "users_user"."organization_id" = %s
AND "users_user"."site_id" = %s
AND "users_user"."is_active" = TRUE;
```
- `"%s"` is replaced dynamically with `"org_id"` and `"site_id"` from the request.

**Django** ORM converts the SQL response into Python dictionaries using `values()`

- This can also be a serializer, but our example of **view** above is using `values()`.

```Python
users_data = list(users.values("id", "email", "first_name", "last_name", "organization_id", "site_id"))
```

The response is then made as a `JSONResponse` since our example **view** from above is returning in that format.

```Python
return JsonResponse({"users": list(users)})
```

This will send the frontend the response in the JSON format for it to use.
The API dynamically retrieves active users for a specific site within an organization.
Example JSON Response Sent to the Front-End

```json
{
  "users": [
    {
      "id": 1,
      "email": "john.doe@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    {
      "id": 3,
      "email": "jane.smith@example.com",
      "first_name": "Jane",
      "last_name": "Smith"
    }
  ]
}
```
---

## Feature #5: Create 3 or More Unit Tests and Document How to Run Them

### Capstone Definition
Basic automated testing of core functionality.

---

## How GWIIT Implements This

### Unit Tests for User, Organization, and Site Models
GWIIT uses **Django’s built-in `unittest` framework** to test **core functionality**, ensuring that models, authentication, and permissions work as expected.  

Each **app (`users`, `organizations`, `sites`) has its own `tests.py` file**, containing tests specific to that app.

### How This Affects the Development Process
- **Prevents regressions** by automatically checking critical functionality.  
- **Ensures authentication, permissions, and multi-database configurations work correctly.**  
- **Reduces manual testing**, making the development process more efficient.  

---

## How GWIIT Uses Unit Testing in Django

### **Test Coverage for Core Models and Relationships**
Each app contains a `tests.py` file, ensuring that all models, model managers, and features are tested.

#### **Example: Testing User Creation (`users/tests.py`)**
```python
def test_user_manager_create_user(self):
        print("\n--- DEBUG: Running test_user_manager_create_user ---")

        unique_timestamp = int(time.time())  # Generates a unique number each time
        raw_email = f"  NEWUSER_{unique_timestamp}@EXAMPLE.COM  "  # Untrimmed & uppercase
        expected_email = raw_email.strip().lower()  # Normalized email

        # Create user
        user = User.objects.db_manager("users_db").create_user(
            email=raw_email,
            username=f"testuser_{unique_timestamp}",  
            password=None,  # Should be auto-generated
            first_name="Jane",
            last_name="Doe",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
        )

        # Debugging Output
        print(f"✅ Created User ID: {user.id}")
        print(f"User Email: {user.email} (Expected: {expected_email})")
        print(f"User Username: {user.username}")
        print(f"User Organization ID: {user.organization_id}")
        print(f"User Site ID: {user.site_id}")

        # Assertions - Email should be normalized
        self.assertEqual(user.email, expected_email, "❌ Email was not normalized before saving.")

        # Assertions - Password should be set and hashed
        self.assertIsNotNone(user.password, "❌ Password should not be None.")
        self.assertNotEqual(user.password, "SecurePass123!", "❌ Password should not be stored as plain text.")
        self.assertTrue(user.password.startswith("pbkdf2_"), "❌ Password should be hashed.")

        # Test Case 1: Attempt to create a user without an email (should raise ValueError)
        with self.assertRaises(ValueError):
            print("🔴 Attempting to create a user without an email (should raise an error)")
            User.objects.db_manager("users_db").create_user(
                email=None,
                username="testuser_no_email",
                password=None,
                first_name="John",
                last_name="Doe",
                organization_id=self.organization1.id,
                site_id=self.site1.id,
            )

        # Test Case 2: Attempt to create a user without any login identifier (should raise ValueError)
        with self.assertRaises(ValueError):
            print("🔴 Attempting to create a user without a login identifier (should raise an error)")
            User.objects.db_manager("users_db").create_user(
                email="identifier_missing@example.com",
                username=None,
                badge_barcode=None,
                badge_rfid=None,
                password=None,
                first_name="John",
                last_name="Doe",
                organization_id=self.organization1.id,
                site_id=self.site1.id,
            )
```
---

## Feature #6: Calculate and Display Data Based on an External Factor

### Capstone Definition
Example: Countdown to an event based on the current date.

---

## How GWIIT Implements This

### Timestamp-Based Calculations for User Sessions & Account Creation
GWIIT uses **timestamp-based filtering** to dynamically **retrieve users who have recently joined**.  
This allows for **time-sensitive queries**, such as listing **new users in the last 30 days**.

### How This Affects the Front-End
- **The API dynamically filters users by their join date**, displaying **only recent accounts**.
- **Admins can track new users per site or organization** in real-time.
- **Enhances reporting dashboards and analytics**.

---

## How Django Uses Timedelta-Based Calculations

### **Custom QuerySet Methods for Date-Based Filtering**
Django’s ORM allows filtering **based on time calculations** using the `timedelta` function.

#### **Example Methods Using `timedelta` (`models.py`)**
```python
# Returns all users created in the last X days (default: 30)
    def recently_joined(self, days=30):
        return self.filter(date_joined__gte=now() - timedelta(days=days))

    # Returns all users created in the last X days from a specific site
    def recently_joined_from_site(self, site_id, days=30):
        return self.filter(date_joined__gte=now() - timedelta(days=days), site_id=site_id)

    # Returns all users created in the last X days from a specific organization
    def recently_joined_from_organization(self, organization_id, days=30):
        return self.filter(date_joined__gte=now() - timedelta(days=days), organization_id=organization_id)
```
---
## Feature #7: Persist Data to an External API and Make It Accessible After Refresh

### Capstone Definition
Example: Save and retrieve data using an external database.

---

## How GWIIT Implements This

**This feature is already covered in our existing implementation of Features #1 and #4.**

---

## Feature #8: Interact with a Database to Store and Retrieve Information

### Capstone Definition
Example: Using MySQL, MongoDB, etc.

## How GWIIT Implements This

**This feature is already covered in our existing implementation of Features #1 and #6.**
---

## Technical Insight

### Python Libraries
The current python library requirements for this project are as follows:

---
- #### **asgiref**==3.8.1
    - ASGI (Asynchronous Server Gateway Interface) support for Django, enabling async capabilities.
---
- #### **Django**==5.1.1
    - The core web framework for building GWIIT, providing ORM, authentication, admin panel, and routing.
---
- #### **django-axes**==6.5.2
    - Security tool that prevents brute-force login attacks by tracking failed login attempts.
---
- #### **django-otp**==1.5.4
    - Adds multi-factor authentication (MFA) support using one-time passwords (OTP).
---
- #### **django-redis**==5.4.0
    - Integrates Redis caching into Django for session storage and performance optimization.
---
- #### **django-tenants**==3.7.0
    - Multi-tenancy support, allowing database schema separation per organization.
---
- #### **phonenumbers**==8.13.46
    - Library for phone number validation and formatting.
---
- #### **psycopg2-binary**==2.9.9
    - PostgreSQL database adapter for Django, enabling database interactions with PostgreSQL.
---
- #### **redis**==5.0.8
    - High-performance in-memory data store used for caching, session management, and rate-limiting.
---
- #### **sqlparse**==0.5.1
    - Library for parsing and formatting SQL queries, used internally by Django ORM.
---
- #### **tzdata**==2024.1
    - Provides timezone support for Django applications to ensure accurate time handling.
---
- #### **passlib**==1.7.4
    - Secure password hashing library used for storing and verifying user passwords.
---
- #### **setuptools**>=65.0.0
    - Python package management tool that helps install and manage dependencies.
---
- #### **celery**==5.3.4
    - Task queue system for handling background jobs in Django, using Redis as a broker.
---
- #### **django-celery-beat**==2.5.0
    - Enables scheduled periodic tasks for Celery, storing task schedules in Django's database.
---
- #### **django-celery-results**==2.5.1
    - Stores Celery task states and results in the Django database for tracking task progress.
---
- #### **channels**==4.0.0
    - Adds WebSocket support to Django, enabling real-time communication between the backend and frontend.
---
- #### **python-socketio**==5.8.0
    - WebSockets framework that allows Django to send real-time updates to the frontend using Socket.IO.
---

The project leverages the following technologies and tools:

- **Backend**: [Django](https://www.djangoproject.com/) with [django-tenants](https://django-tenants.readthedocs.io/en/latest/) for multi-tenant support.
- **Frontend**: Initially planned with [React](https://reactjs.org/); however, due to time constraints, the implementation will proceed with vanilla JavaScript, HTML, and CSS.
- **Database**: PostgreSQL, chosen for its robustness and compatibility with `django-tenants`(for production). SQLite3 for early development and initial testing

## Front End Design

### Overview
The front-end design of GWIIT follows a **clean, corporate-friendly aesthetic** inspired by Windows Vista-era applications.  
The primary goal is to create a **functional, easy-to-navigate form-based UI** that allows users to **input and review data efficiently**.

### Design Principles
- **Minimalist and Functional UI**
  - The interface is primarily **form-based**, with users **filling out, viewing, and reporting data**.
  - No **excessive animations** or interactive elements that do not serve a functional purpose.
  - **Clear spacing, structure, and intuitive form layouts** for ease of use.

- **Windows Vista-Era Aesthetic**
  - The UI follows a **clean, slightly modernized version of Windows Vista-style apps**.
  - Uses **flat design with slight gradients**, avoiding ultra-modern trends.
  - **Simple, well-aligned elements** to provide a professional feel.

- **Mobile-First Responsive Layout**
  - The app will be designed to **scale across multiple devices**:
    - **Phones**
    - **Tablets**
    - **Laptops**
    - **Desktops**
    - **Larger displays (TVs for reporting & monitoring)**
  - CSS **media queries** will ensure proper rendering and usability across screen sizes.

- **Standard Iconography**
  - UI elements will utilize **Google’s Material Icons** for:
    - **Navigation menus** (hamburger menu)
    - **Action buttons** (✔, ✖, ⏳)
    - **Form validation indicators** (✅ ❌)
  - **Icons will be kept simple** to maintain a **clean, uncluttered UI**.

- **Typography**
  - **Primary Font:** **Segoe UI** (default Windows Vista font).
  - **Fallback Fonts:** Arial, sans-serif.
  - **Emphasis on readability** with clear contrast and spacing.

- **Color Scheme**
  - **Neutral corporate colors** (white, grays, soft blues).
  - **Minimal bold colors** (used only for alerts and required fields).
  - **Backgrounds will be light** to maintain a professional and clean appearance.

- **CSS for Layout and Structure**
  - CSS will be used for **form layout, spacing, and alignment**.
  - **No unnecessary JavaScript-based animations**—functionality takes priority over visual effects.
  - **Forms, tables, and buttons will be designed for usability first**.

### Summary
The front-end of GWIIT prioritizes **functionality, usability, and clarity** while maintaining a **corporate-friendly design**.  
It follows **mobile-first principles** and ensures that the interface **remains accessible, structured, and easy to use across all devices**.

## Project Plan Format

The project plan is documented in this Markdown file to maintain simplicity and clarity. This format allows for easy updates and sharing.

## Submission Details

The completed project, along with this project plan, will be submitted through the designated Google Form by **11:59 AM (Noon) EST on the last Friday of Module 4**.

---