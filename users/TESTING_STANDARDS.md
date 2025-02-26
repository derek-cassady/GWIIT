# Testing Standards

## Overview
This document outlines the standardized approach for writing and maintaining tests in this project. These standards ensure consistency, readability, and reliability across all test cases.

---
## Print Statements for Test Start/End Announcements

Each test must clearly announce its start and end using print(), but should not include debugging output.

Example:
```python
print("\n⏳ Starting test_user_manager_create_user...")
print("✅ Finished test_user_manager_create_user...")
```
Debugging print statements inside test cases should be avoided unless temporarily used for troubleshooting.

Print statements are primarily for marking test start/end, and assertions should handle validation.

Emojis should not be used in comments or in anywhere else in the code.  These are meant as a simple visual check during development and/or testing.

---


## AAA (Arrange, Act, Assert) Methodology
All test cases should follow **Arrange, Act, Assert (AAA)** to maintain clarity and separation of concerns:

- **Arrange:** Set up necessary objects and test conditions.
- **Act:** Execute the specific function or method being tested.
- **Assert:** Verify that the output matches expectations.

```python
def test_example(self):
    # Arrange
    user = User.objects.create(email="test@example.com")

    # Act
    retrieved_user = User.objects.get(email="test@example.com")

    # Assert
    self.assertEqual(user.id, retrieved_user.id, "Retrieved user ID does not match expected value.")
```
---

## Test Structure & Organization

### **Organizing Test Files**
Each test file should correspond to the Django file it tests.

| File Being Tested | Test File             |
| ------------------|-----------------------|
| `models.py`       | `test_models.py`      |
| `managers.py`     | `test_managers.py`    |
| `views.py`        | `test_views.py`       |
| `serializers.py`  | `test_serializers.py` |
| `forms.py`        | `test_forms.py`       |

Each file should **only** test the related functionality. Avoid mixing concerns.

### **One Test Method Per Behavior**
Each test method should test **only one aspect** of behavior.

**Example Good Tests**
```python
def test_user_manager_create_user_success(self):
    user = User.objects.create_user(email="valid@example.com", password="TestPass123!")
    self.assertIsNotNone(user, "User should be created successfully.")

def test_user_manager_create_user_failure(self):
    with self.assertRaises(ValueError, msg="Creating a user without an email should raise ValueError."):
        User.objects.create_user(email=None)
```

**Example Bad Tests**
```Python
def test_user_manager_create_user(self):
    user = User.objects.create_user(email="valid@example.com", password="TestPass123!")
    self.assertIsNotNone(user, "User should be created successfully.")

    with self.assertRaises(ValueError, msg="Creating a user without an email should raise ValueError."):
        User.objects.create_user(email=None)
```
The **bad example** includes **multiple test cases** in a single **Test Method**, which makes debugging harder.

---

### **One Assertion Per Expected Behavior**
Each test method should have **one assertion** per expected behavior.

Multiple assertions can exist per **Test Method**, as long as each assertion checks a distinct expected behavior.

**Example Good**
```Python
def test_user_email_is_normalized(self):
    user = User.objects.create(email="TEST@Example.COM")
    self.assertEqual(user.email, "test@example.com", "Email should be normalized to lowercase.")

```
---

**Example Bad**
```Python
def test_user_email_normalization(self):
    user = User.objects.create(email="TEST@Example.COM")
    self.assertEqual(user.email, "test@example.com", "Email should be normalized.")
    self.assertTrue(user.email.islower(), "Email should be lowercase.")
```
The **bad example** adds **multiple redundant assertions**, which is unnecessary.

---
## Testing Both Success & Failure Cases

Each test must include:

- A successful case (verifying expected functionality).

- A failure case (ensuring proper error handling).

This ensures that tests do not only confirm success, but also check robust error handling.

---

## Consistent Test Naming Convention
To maintain clarity and debugging efficiency, test method names follow a structured format. Since test files are already separated by component (e.g., `test_managers.py`, `test_models.py`), we simplify the naming convention while ensuring consistency.

**Example:** Standard Format
```Python
test_<ClassName>_<MethodName>_<ExpectedBehavior>()
```
**Example:** for `test_managers.py` (`UserManager` tests)
```Python
def test_UserManager_normalize_email_uppercase(self):
def test_UserManager_normalize_email_leading_trailing_spaces(self):
def test_UserManager_normalize_email_invalid_format(self):
```
**Example:** for `test_models.py` (`User` model tests)
```Python
def test_User_get_organization_valid(self):
def test_User_get_organization_no_association(self):
```
---

## Test Terminology

### TestCase

**Definition:** In Django, a **TestCase** refers to a <```class```> that inherits from ```django.test.TestCase``` or another test <```class```>. 

- This <```class```> groups related **TestMethod**s that test specific functionalities of the application.

### TestMethod

**Definition:** A **TestMethod** is an individual method within a **TestCase** <```class```>. 

- Each **TestMethod** checks a particular aspect of the functionality being tested. **TestMethod**s must start with the word "test" to be recognized by Django's test runner.

## Test Case Selection
Test case structure is critical to maintaining efficient and effective tests. The table below outlines when to use different types of test cases.

### Selecting the Right Test Case Type

|Test Case Type|Purpose|When to Use|
|--------------|-------|:----:|
***Unit Test*** (TestCase) | Isolated test of a single function or method | Use for model managers, utility functions, and standalone logic |
***Integration Test*** (TransactionTestCase) | Ensures multiple components work together | Use when testing models that interact with multiple databases or require transactions |
***API Test*** (APITestCase) | Tests API endpoints with Django Rest Framework | Use when testing views, authentication, or request/response validation |
***Form Test*** (SimpleTestCase) | Validates form behavior without database interaction | Use for testing form validation, cleaning, and processing logic |
***Database Query Test*** (TestCase with assertNumQueries) | Ensures a query executes efficiently | Use when testing optimized database interactions |

---

#### Deciding Test Scope
- If testing model methods or managers - Use TestCase

- If testing data consistency across multiple databases - Use TransactionTestCase

- If testing HTTP views or API responses - Use APITestCase

- If testing form validation without touching the database - Use SimpleTestCase

## Assertions in Django Testing

### What Are Assertions?

Assertions are conditions used in **TestMethod**s to validate expected behavior. If an assertion fails, Django marks the test as a failure.

### Why Are Assertions Needed?

- **Validate Expected Behavior –** Ensures that a function, query, or API returns the expected result.

- **Prevent Bugs –** Identifies unexpected behavior early in development.

- **Improve Debugging –** Failed assertions provide clear feedback about what went wrong.

### Common Assertion Methods (With Examples)
---

#### **self.assertEqual(a, b)**
Ensures that `a` and `b` are equal.

**Example:**
```python
user = User.objects.create(email="test@example.com")
retrieved_user = User.objects.get(email="test@example.com")
self.assertEqual(user.id, retrieved_user.id, "Retrieved user ID does not match expected value.")
```
---

#### **self.assertNotEqual(a, b)**
Ensures that `a` and `b` are <u>**NOT**</u> equal.

**Example:**
```python
self.assertNotEqual("abc", "xyz", "Values should not be equal.")
```
---

#### **self.assertFalse(condition)**
Ensures that `condition` evaluates to `False`.

**Example:**
```python
user = User.objects.create(email="test@example.com", is_active=False)
self.assertFalse(user.is_active, "User should be inactive.")
```
---

#### **self.assertRaises(ExpectedException)**
Ensures that a specific exception is raised.

**Example:**
```python
with self.assertRaises(ValueError, msg="Creating a user without an email should raise an error."):
    User.objects.create(email=None)
```
---

#### **self.assertContains(response, text)**
Checks if a response includes a specific text.

**Example:**
```python
response = self.client.get('/home/')
self.assertContains(response, "Welcome to the homepage")
```
---

#### **self.assertRedirects(response, expected_url)**
Ensures a response redirects to the correct URL

**Example:**
```python
response = self.client.post('/logout/')
self.assertRedirects(response, '/login/')
```
---

### Additional Assertions in Django
In addition to the commonly used assertions, Django provides specialized assertions for testing templates, forms, HTTP responses, and database interactions. 

This list can be further expanded as sections of the application are developed to add examples for each specific type of assertion.

#### Assertions for HTTP Responses
|Assertion|Purpose|Example|
|---------|-------|:----:|
|self.assertContains(response, text, count=None, status_code=200, msg_prefix='', html=False)|Ensures a response contains a given text|self.assertContains(response, "Welcome to the site")|
|self.assertNotContains(response, text, status_code=200, msg_prefix='', html=False)|Ensures a response does not contain a given text|self.assertNotContains(response, "Error")|
|self.assertRedirects(response, expected_url, status_code=302, target_status_code=200, fetch_redirect_response=True)|	Ensures the response redirects to a specific URL|self.assertRedirects(response, '/dashboard/')|
|self.assertTemplateUsed(response, template_name, msg_prefix='')|Ensures a specific template was used in rendering the response|self.assertTemplateUsed(response, "home.html")|
---

#### Assertions for Forms and Fields
|Assertion|Purpose|Example|
|---------|-------|:----:|
|self.assertFormError(response, form, field, errors, msg_prefix='')|Ensures a form field contains specific errors	self.|assertFormError(response, "login_form", "username", "This field is required.")|
|self.assertFieldOutput(fieldclass, valid, invalid, field_args=None, field_kwargs=None, empty_value='')|Validates form field behavior with valid and invalid inputs|self.assertFieldOutput(CharField, {"valid_input": "Valid"}, {"invalid_input": ["Error message"]})|
---

#### Assertions for Database Behavior
|Assertion|Purpose|Example|
|---------|-------|:----:|
|self.assertQuerysetEqual(qs, values, transform=repr, ordered=True, msg=None)|Ensures a queryset matches expected values|self.assertQuerysetEqual(User.objects.filter(is_active=True), ['<User: user1>', '<User: user2>'])|
|self.assertNumQueries(num, func, *args, **kwargs)|	Ensures a specific number of database queries are executed|self.assertNumQueries(1, lambda: User.objects.get(id=1))|
---

## Test Setup Method Comments

Test Setup Methods are responsible for setting up the test environment for a **TestCase** before execution. Since they do not test functionality, they follow a different comment structure.

### Comment Structure

Prepares <**TestCase** environment> before each **TestMethod** runs.

**Purpose:**

- Describes why the test setup method is necessary.
- Defines what relationships and test data are being set up.
- Explains how this benefits test reliability.

**Expected Behavior:**

- Defines what a successful setup looks like.
- Lists key properties of the test data (e.g., correct relationships, valid attributes).
- Outlines constraints such as expected variations in data.

**Data Setup:**

- **[Data Category]** (Stored in ```[database]```): What entities are created.
- **[Data Category]** (Stored in ```[database]```): How entities are linked.
- **[Data Category]** (Stored in ```[database]```): Any attributes important for testing.

Example:
```Python
"""
Prepares test data before each test method runs.

Purpose:
    - Ensures each test starts with a fresh and structured dataset.
    - Establishes consistent relationships between organizations, sites, and users.
    - Provides diverse user attributes to test query methods.

Expected Behavior:
    - Organizations, sites, and users are correctly created and linked.
    - Users have varying statuses (`active`, `inactive`), roles (`staff`, `non-staff`), and MFA preferences.

Data Setup:
    1. **Organizations** (Stored in `organizations_db`)
            - Two organizations with different types.
    2. **Sites** (Stored in `sites_db`)
            - Two sites linked to different organizations.
    3. **Users** (Stored in `users_db`)
            - Four users with different roles, MFA settings, and status.

Guarantees that all test cases start with a structured dataset.
"""
```
---

## TestMethod Comments

**Testmethod** comments clearly document what is being tested.

### Comment Structure

Tests <method_name> to ensure <primary function>.

Comment Structure
Tests <method_name> to ensure <primary function>.

**Purpose:**

Describes what functionality the test verifies.
Explains why this test is necessary.
Highlights any constraints or assumptions.

**Expected Behavior:**

Defines success conditions.
Outlines failure conditions.
Lists key attributes or outputs that should be verified.

**Test Cases:**

```[Test Case Name]``` - What it verifies.
```[Test Case Name]``` - An edge case scenario.
```[Test Case Name]``` - Failure handling conditions.

Example:
``` Python
"""
Tests the create_user() method to ensure correct user creation.

Purpose:
    - Ensures that users are created successfully with all required fields.
    - Validates password security and email normalization.
    - Enforces constraints on required fields.

Expected Behavior:
    - Users should be created with a hashed password.
    - Email should be normalized (lowercased, trimmed).
    - Missing required fields should raise a ValueError.

Test Cases:
    1. **Valid User Creation** - Ensures a user is created correctly.
    2. **Missing Email** - Should raise ValueError.
    3. **Missing Login Identifier** - Should raise ValueError.
"""
```
---

## Running Tests

To run all tests:
```Python
python manage.py test
```
---

To run a specific test:
```Python
python manage.py test <app_name>.tests.<TestClassName>
```
---

To run a test with verbosity:
```Python
python manage.py test --verbosity 2
```
---