from django.test import TestCase
from django.apps import apps
from users.models import User
from users.managers import UserManager
from organizations.models import Organization
from sites.models import Site
from django.utils.timezone import now
from datetime import timedelta
from django.core import mail
from django.core.mail import send_mail
from unittest.mock import patch
import smtplib
import time
import string
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
# https://docs.djangoproject.com/en/5.1/topics/testing/tools/

class UserModelTests(TestCase):
    """
    TransactionTestCase.databases explained:
        
    Purpose:
    - Ensures test databases are properly managed and isolated between test runs.
    - Optimizes database flushing to improve test performance.
    - Prevents unintended state leaks between tests when using multiple databases.

    Key Points:
    1. **Default Behavior**:
        - Django sets up test databases for each defined database in `DATABASES`.
        - By default, only the **default database** is flushed before each test.
        - This reduces unnecessary database resets, improving test speed.

    2. **Flushing Non-Default Databases**:
        - If a test needs a **clean state** across multiple databases, it must specify the required databases.
        - Use the `databases` attribute on the test class or method to request additional databases to be flushed.
        - `databases = '__all__'` ensures all test databases are flushed before a test runs.

    3. **Preventing State Leaks**:
        - Queries to databases **not listed** in `databases` will raise assertion errors.
        - This prevents unintentional data persistence between test cases.

    4. **Transaction Wrapping in `TestCase`**:
        - By default, only the **default database** is wrapped in a transaction during `TestCase` execution.
        - To enable transaction wrapping for **non-default databases**, explicitly declare them using `databases`.

    Guarantees proper database isolation, optimizes test execution time, and ensures consistency when testing across multiple databases.
    """
    
    databases = {"default", "users_db", "organizations_db", "sites_db"}

    """
    Performs class-wide setup before any test in this class executes.

    Purpose:
        - Ensures that any necessary setup for the test class is performed.
        - Provides a consistent environment across all test cases.
        - Runs only once before all test methods in the class.

    Expected Behavior:
        - Executes any required setup that applies to all test cases.
        - Can be expanded later to initialize class-wide configurations.

    Notes:
        - Future modifications may include logging, database preparation, or resource allocation.
    """

    @classmethod
    def setUpClass(cls):
        # Runs once before any test in this class executes.
        super().setUpClass()

    """
    Prepares test data before each test method runs to ensure consistency across multiple databases.

    Purpose:
        - Ensures each test starts with a fresh and structured dataset.
        - Establishes consistent relationships between organizations, sites, and users.
        - Provides diverse user attributes to thoroughly test query methods.
        - Simulates real-world scenarios, including active/inactive users, staff roles, and multi-database queries.

    Expected Behavior:
        - Organizations, sites, and users are correctly created and linked.
        - Users have varying statuses (`active`, `inactive`), roles (`staff`, `non-staff`), and MFA preferences.
        - User relationships (e.g., `created_by_id`, `modified_by_id`) are properly assigned.

    Data Setup:
        1. **Organizations** (Stored in `organizations_db`)
            - Two organizations with different types and active statuses.
        2. **Sites** (Stored in `sites_db`)
            - Two sites linked to different organizations with varied attributes.
        3. **Users** (Stored in `users_db`)
            - Four users with diverse attributes:
                - Different login methods (`email`, `username`).
                - Different MFA settings (`none`, `Google Authenticator`, `SMS`, `email`).
                - A mix of `active` and `inactive` statuses.
                - Staff and non-staff users.
                - Users assigned to different organizations and sites.
                - Users created and modified by other users.

    Guarantees that all test cases begin with a structured and representative dataset for validation.
    """

    def setUp(self):

        # Iinitializes UserManager instance.
        self.user_manager = UserManager()

        # Use apps.get_model() to ensure cross-app consistency
        Organization = apps.get_model("organizations", "Organization")
        Site = apps.get_model("sites", "Site")
        User = apps.get_model("users", "User")
        
        # Create test organizations
        self.organization1 = Organization.objects.using("organizations_db").create(
            #id = "1",
            name="Test Organization 1",
            type_id=1,
            active=True,
            contact_id=None,  # Ensuring this field is handled
            login_options={},  # Matches model default
            mfa_required=False,  # Matches model default
            created_by_id=None,
            date_created=now(),
            last_modified=now(),
            modified_by_id=None
        )

        self.organization2 = Organization.objects.using("organizations_db").create(
            #id = "2",
            name="Test Organization 2",
            type_id=2,
            active=True,
            contact_id=None,  # Ensuring this field is handled
            login_options={},  # Matches model default
            mfa_required=False,  # Matches model default
            created_by_id=None,
            date_created=now(),
            last_modified=now(),
            modified_by_id=None
        )

        # Create test sites
        self.site1 = Site.objects.using("sites_db").create(
            #id = "1",
            name="Test Site 1",
            organization_id=self.organization1.id,
            site_type="Office",
            address="123 Test St",
            active=True,
            created_by_id=None,
            date_created=now(),
            last_modified=now(),
            modified_by_id=None
        )

        self.site2 = Site.objects.using("sites_db").create(
            #id = "2",
            name="Test Site 2",
            organization_id=self.organization2.id,
            site_type="Warehouse",
            address="456 Another St",
            active=True,
            created_by_id=None,
            date_created=now(),
            last_modified=now(),
            modified_by_id=None
        )

        # Create multiple test users with different attributes
        self.user1 = User.objects.using("users_db").create(
            #id = "1",
            email="user1@example.com",
            username="userone",
            first_name="Alice",
            last_name="Smith",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            badge_barcode="BARCODE12345",
            badge_rfid="RFID98765",
            is_active=True,
            is_staff=False,
            mfa_preference="none",
            created_by_id=None,
            modified_by_id=None,
            date_joined=now() - timedelta(days=5)
        )

        self.user1.set_password("SecurePass123!")
        self.user1.save(using="users_db")

        self.user2 = User.objects.using("users_db").create(
            #id = "2",
            email="user2@example.com",
            username="usertwo",
            password="SecurePass123!",
            first_name="Bob",
            last_name="Johnson",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            badge_barcode="BARCODE23456",
            badge_rfid="RFID87654",
            is_active=False,  # Inactive user
            is_staff=False,
            mfa_preference="google_authenticator",
            created_by_id=None,
            modified_by_id=self.user1.id,
            date_joined=now() - timedelta(days=40)
        )

        self.user2.set_password("SecurePass123!")
        self.user2.save(using="users_db")

        self.user3 = User.objects.using("users_db").create(
            #id = "3",
            email="user3@example.com",
            username="userthree",
            password="SecurePass123!",
            first_name="Charlie",
            last_name="Brown",
            organization_id= None,
            site_id= None,
            badge_barcode="BARCODE34567",
            badge_rfid="RFID76543",
            is_active=True,
            is_staff=True,  # Staff user
            mfa_preference="sms",
            created_by_id=None,
            modified_by_id=self.user1.id,
            date_joined=now() - timedelta(days=15)
        )

        self.user3.set_password("SecurePass123!")
        self.user3.save(using="users_db")

        self.user4 = User.objects.using("users_db").create(
            #id = "4",
            email="user4@example.com",
            username="userfour",
            password="SecurePass123!",
            first_name="Dana",
            last_name="White",
            organization_id=None,
            site_id=None,
            badge_barcode="BARCODE45678",
            badge_rfid="RFID65432",
            is_active=True,
            is_staff=False,
            mfa_preference="email",
            created_by_id=self.user1.id,
            modified_by_id=self.user2.id,
            date_joined=now()
        )

        self.user4.set_password("SecurePass123!")
        self.user4.save(using="users_db")

    """
    Verifies that the test organization exists after setup.

    Purpose:
        - Ensures that `setUp()` correctly creates and stores the organization in `organizations_db`.

    Expected Behavior:
        - Organization with `self.organization1.id` should be present in the test database.

    Test Steps:
        1. Retrieve `organization1` using `apps.get_model()` and `filter()`.
        2. Assert that the retrieved organization is **not None**.

    Guarantees that the test database correctly initializes the organization data before running tests.
    """

    # Test 1a: Ensure test organization 1 exists
    def test_users_test_managers_UserModelTests_setUp_OrganizationExists_org2(self):
        Organization = apps.get_model("organizations", "Organization")
        organization = Organization.objects.using("organizations_db").filter(id=self.organization1.id).first()
        self.assertIsNotNone(organization, "Organization1 should exist in the test database.")

    # Test 1b: Ensure test organization 2 exists
    def test_users_test_managers_UserModelTests_setUp_OrganizationExists_org2(self):
        Organization = apps.get_model("organizations", "Organization")
        organization = Organization.objects.using("organizations_db").filter(id=self.organization2.id).first()
        self.assertIsNotNone(organization, "Organization2 should exist in the test database.")

    """
    Verifies that the test site exists after setup.

    Purpose:
        - Ensures that `setUp()` correctly creates and stores the site in `sites_db`.

    Expected Behavior:
        - Site with `self.site1.id` should be present in the test database.

    Test Steps:
        1. Retrieve `site1` using `apps.get_model()` and `filter()`.
        2. Assert that the retrieved site is **not None**.

    Guarantees that the test database correctly initializes the site data before running tests.
    """

    # Test 2a: Ensure test site exists
    def test_users_test_managers_UserModelTests_setUp_SiteExists_site1(self):
        Site = apps.get_model("sites", "Site")
        site = Site.objects.using("sites_db").filter(id=self.site1.id).first()
        self.assertIsNotNone(site, "Site1 should exist in the test database.")

    # Test 2b: Ensure test site exists
    def test_users_test_managers_UserModelTests_setUp_SiteExists_site2(self):
        Site = apps.get_model("sites", "Site")
        site = Site.objects.using("sites_db").filter(id=self.site2.id).first()
        self.assertIsNotNone(site, "Site2 should exist in the test database.")

    """
    Verifies that the test user exists after setup.

    Purpose:
        - Ensures that `setUp()` correctly creates and stores the user in `users_db`.

    Expected Behavior:
        - User with `self.user1.id` should be present in the test database.

    Test Steps:
        1. Retrieve `user1` using `apps.get_model()` and `filter()`.
        2. Assert that the retrieved user is **not None**.

    Guarantees that the test database correctly initializes user data before running tests.
    """
    
    # Test 3a: Ensure test user 1 exists
    def test_users_test_managers_UserModelTests_setUp_UserExists_user1(self):
        User = apps.get_model("users", "User")
        user = User.objects.using("users_db").filter(id=self.user1.id).first()
        self.assertIsNotNone(user, "User1 should exist in the test database.")

    # Test 3b: Ensure test user 2 exists
    def test_users_test_managers_UserModelTests_setUp_UserExists_user2(self):
        User = apps.get_model("users", "User")
        user = User.objects.using("users_db").filter(id=self.user2.id).first()
        self.assertIsNotNone(user, "User2 should exist in the test database.")

    # Test 3c: Ensure test user 3 exists
    def test_users_test_managers_UserModelTests_setUp_UserExists_user3(self):
        User = apps.get_model("users", "User")
        user = User.objects.using("users_db").filter(id=self.user3.id).first()
        self.assertIsNotNone(user, "User3 should exist in the test database.")

    # Test 3d: Ensure test user 4 exists
    def test_users_test_managers_UserModelTests_setUp_UserExists_user4(self):
        User = apps.get_model("users", "User")
        user = User.objects.using("users_db").filter(id=self.user4.id).first()
        self.assertIsNotNone(user, "User4 should exist in the test database.")        
    
    """
    Verifies that the test user's email is correctly set.

    Purpose:
        - Ensures that `setUp()` assigns the correct email to `user1`.

    Expected Behavior:
        - `self.user1.email` should match the expected value `"user1@example.com"`.

    Test Steps:
        1. Retrieve `self.user1.email`.
        2. Assert that it matches the expected value.

    Guarantees that user email is properly assigned during setup.
    """
   
    # Test 4a: Ensure test user 1 email is correctly set
    def test_users_test_managers_UserModelTests_setUp_UserEmailCorrect_user1(self):
        self.assertEqual(self.user1.email, "user1@example.com", "User email does not match expected value.")

    # Test 4b: Ensure test user 2 email is correctly set
    def test_users_test_managers_UserModelTests_setUp_UserEmailCorrect_user2(self):
        self.assertEqual(self.user2.email, "user2@example.com", "User email does not match expected value.")
    
    # Test 4c: Ensure test user 3 email is correctly set
    def test_users_test_managers_UserModelTests_setUp_UserEmailCorrect_user3(self):
        self.assertEqual(self.user3.email, "user3@example.com", "User email does not match expected value.")

    # Test 4d: Ensure test user 4 email is correctly set
    def test_users_test_managers_UserModelTests_setUp_UserEmailCorrect_user4(self):
        self.assertEqual(self.user4.email, "user4@example.com", "User email does not match expected value.")
    
    """
    Verifies that the test user's username is correctly set.

    Purpose:
        - Ensures that `setUp()` assigns the correct username to `user1`.

    Expected Behavior:
        - `self.user1.username` should match the expected value `"userone"`.

    Test Steps:
        1. Retrieve `self.user1.username`.
        2. Assert that it matches the expected value.

    Guarantees that user username is properly assigned during setup.
    """

    # Test 5a: Ensure test user 1 username is correctly set
    def test_users_test_managers_UserModelTests_setUp_UserUsernameCorrect_user1(self):
        self.assertEqual(self.user1.username, "userone", "User username does not match expected value.")

    # Test 5b: Ensure test user 2 username is correctly set
    def test_users_test_managers_UserModelTests_setUp_UserUsernameCorrect_user2(self):
        self.assertEqual(self.user2.username, "usertwo", "User username does not match expected value.")

    # Test 5c: Ensure test user 3 username is correctly set
    def test_users_test_managers_UserModelTests_setUp_UserUsernameCorrect_user3(self):
        self.assertEqual(self.user3.username, "userthree", "User username does not match expected value.")

    # Test 5d: Ensure test user 4 username is correctly set
    def test_users_test_managers_UserModelTests_setUp_UserUsernameCorrect_user4(self):
        self.assertEqual(self.user4.username, "userfour", "User username does not match expected value.")
    
    """
    Verifies that the test user's `organization_id` is correctly set.

    Purpose:
        - Ensures that `setUp()` assigns the correct organization ID to `user1`.

    Expected Behavior:
        - `self.user1.organization_id` should match `self.organization1.id`.

    Test Steps:
        1. Retrieve `self.user1.organization_id`.
        2. Assert that it matches the expected value.

    Guarantees that the user is associated with the correct organization.
    """

    # Test 6a: Ensure test user 1 organization_id is correctly set
    def test_users_test_managers_UserModelTests_setUp_UserOrganizationCorrect_user1(self):
        self.assertEqual(self.user1.organization_id, self.organization1.id, "User 1 organization_id does not match expected value.")

    # Test 6b: Ensure test user 2 organization_id is correctly set
    def test_users_test_managers_UserModelTests_setUp_UserOrganizationCorrect_user2(self):
        self.assertEqual(self.user2.organization_id, self.organization1.id, "User 2 organization_id does not match expected value.")

    # Test 6c: Ensure test user 3 organization_id is correctly set (None)
    def test_users_test_managers_UserModelTests_setUp_UserOrganizationCorrect_user3(self):
        self.assertIsNone(self.user3.organization_id, "User 3 organization_id should be None.")

    # Test 6d: Ensure test user 4 organization_id is correctly set (None)
    def test_users_test_managers_UserModelTests_setUp_UserOrganizationCorrect_user4(self):
        self.assertIsNone(self.user4.organization_id, "User 4 organization_id should be None.")
    
    """
    Verifies that the test user's `site_id` is correctly set.

    Purpose:
        - Ensures that `setUp()` assigns the correct site ID to `user1`.

    Expected Behavior:
        - `self.user1.site_id` should match `self.site1.id`.

    Test Steps:
        1. Retrieve `self.user1.site_id`.
        2. Assert that it matches the expected value.

    Guarantees that the user is associated with the correct site.
    """

    # Test 7a: Ensure test user 1 site_id is correctly set
    def test_users_test_managers_UserModelTests_setUp_UserSiteCorrect_user1(self):
        self.assertEqual(self.user1.site_id, self.site1.id, "User 1 site_id does not match expected value.")

    # Test 7b: Ensure test user 2 site_id is correctly set
    def test_users_test_managers_UserModelTests_setUp_UserSiteCorrect_user2(self):
        self.assertEqual(self.user2.site_id, self.site1.id, "User 2 site_id does not match expected value.")

    # Test 7c: Ensure test user 3 site_id is correctly set (None)
    def test_users_test_managers_UserModelTests_setUp_UserSiteCorrect_user3(self):
        self.assertIsNone(self.user3.site_id, "User 3 site_id should be None.")

    # Test 7d: Ensure test user 4 site_id is correctly set ("")
    def test_users_test_managers_UserModelTests_setUp_UserSiteCorrect_user4(self):
        self.assertIsNone(self.user4.site_id, "User 4 site_id should be None.")

    """
    Tests normalize_email() in UserManager to ensure proper email formatting and error handling.

    Purpose:
        - Ensures email addresses are correctly formatted before being saved.
        - Confirms normalization handles case sensitivity and whitespace.
        - Validates that invalid email formats raise a `ValueError`.

    Expected Behavior:
        - Converts uppercase letters to lowercase.
        - Strips leading and trailing whitespace.
        - Returns `None` when given `None` as input.
        - Raises a `ValueError` when given an invalid email format.

    Test Cases (Grouped under Test 8):
        8a. **Uppercase Letters** → Converts "USER@Example.COM" to "user@example.com".
        8b. **Leading & Trailing Spaces** → Strips spaces from "  user@example.com  ".
        8c. **Mixed-Case Email** → Normalizes "MiXEDcAsE@DOMAIN.CoM" to "mixedcase@domain.com".
        8d. **None Input** → Returns `None` without raising an error.
        8e. **Invalid Email Format** → Raises `ValueError` for malformed emails (e.g., "INVALID EMAIL@EXAMPLE.COM").

    Guarantees that email normalization works correctly before storing user data.
    """

    #Test 8a: Ensure uppercase emails are converted to lowercase.
    def test_users_test_managers_UserManager_normalize_email_uppercase(self):
        raw_email = "  USER@Example.COM  "
        expected_email = "user@example.com"
        normalized_email = self.user_manager.normalize_email(raw_email)
        self.assertEqual(normalized_email, expected_email, "Uppercase email normalization failed.")

    # Test 8b:Ensure leading and trailing spaces are removed.
    def test_users_test_managers_UserManager_normalize_email_leading_trailing_spaces(self):
        raw_email = "  user@example.com  "
        expected_email = "user@example.com"
        normalized_email = self.user_manager.normalize_email(raw_email)
        self.assertEqual(normalized_email, expected_email, "Email normalization failed to strip spaces.")
    
    # Test 8c:Ensure mixed-case emails normalize correctly.
    def test_users_test_managers_UserManager_normalize_email_mixed_case(self):
        raw_email = "MiXEDcAsE@DOMAIN.CoM"
        expected_email = "mixedcase@domain.com"
        normalized_email = self.user_manager.normalize_email(raw_email)
        self.assertEqual(normalized_email, expected_email, "Mixed-case email normalization failed.")

    # Test 8d:Ensure None input returns None.
    def test_users_test_managers_UserManager_normalize_email_none_input(self):
        raw_email = None
        normalized_email = self.user_manager.normalize_email(raw_email)
        self.assertIsNone(normalized_email, "None email input should return None.")

    # Test 8e:Ensure invalid email formats raise a ValueError.
    def test_users_test_managers_UserManager_normalize_email_invalid_format(self):
        raw_email = "INVALID EMAIL@EXAMPLE.COM"
        with self.assertRaises(ValueError, msg="normalize_email() should raise ValueError for an invalid email format."):
            self.user_manager.normalize_email(raw_email)

    """
    Tests generate_secure_password() to ensure strong password generation.

    Purpose:
        - Confirms that generated passwords meet security and complexity requirements.
        - Ensures that passwords contain all required character types.
        - Validates that passwords are unique across multiple generations.
        - Ensures the function raises an error when attempting to generate a password below the minimum length.

    Expected Behavior:
        - Generates passwords with a minimum length of 16 characters.
        - Each password contains at least one uppercase letter, one lowercase letter, one digit, and one special character.
        - Passwords are randomly generated and unique.
        - Raises a `ValueError` if a password shorter than 16 characters is requested.

    Test Cases:
        9a. **Default Password Length (16)** → Confirms generated password meets minimum length.
        9b. **Custom Password Length (20)** → Ensures requested length is respected.
        9c. **Password Character Validation**:
            1. Must contain at least one uppercase letter.
            2. Must contain at least one lowercase letter.
            3. Must contain at least one digit.
            4. Must contain at least one special character.
        9d. **Password Uniqueness** → Multiple generated passwords should not be identical.
        9e. **Password Below Minimum Length** → Attempting to generate a password <16 should raise a `ValueError`.

    Guarantees that password generation adheres to security best practices and prevents weak or predictable passwords.
    """

    
    # Test 9a: Ensure default password length is 16 characters
    def test_users_test_managers_UserManager_generate_secure_password_default_length(self):
        password = self.user_manager.generate_secure_password()
        self.assertEqual(len(password), 16, "Default password length should be 16.")

    # Test 9b: Ensure custom password length works (20 characters)
    def test_users_test_managers_UserManager_generate_secure_password_custom_length(self):
        password = self.user_manager.generate_secure_password(length=20)
        self.assertEqual(len(password), 20, "Custom password length should be 20.")

    # Test 9c-1: Ensure password contains at least one uppercase letter
    def test_users_test_managers_UserManager_generate_secure_password_contains_uppercase(self):
        password = self.user_manager.generate_secure_password()
        has_upper = any(c.isupper() for c in password)
        self.assertTrue(has_upper, "Password missing an uppercase letter.")

    # Test 9c-2: Ensure password contains at least one lowercase letter
    def test_users_test_managers_UserManager_generate_secure_password_contains_lowercase(self):
        password = self.user_manager.generate_secure_password()
        has_lower = any(c.islower() for c in password)
        self.assertTrue(has_lower, "Password missing a lowercase letter.")

    # Test 9c-3: Ensure password contains at least one digit
    def test_users_test_managers_UserManager_generate_secure_password_contains_digit(self):
        password = self.user_manager.generate_secure_password()
        has_digit = any(c.isdigit() for c in password)
        self.assertTrue(has_digit, "Password missing a digit.")

    # Test 9c-4: Ensure password contains at least one special character
    def test_users_test_managers_UserManager_generate_secure_password_contains_special_character(self):
        password = self.user_manager.generate_secure_password()
        has_special = any(c in self.user_manager.SPECIAL_CHARACTERS for c in password)
        self.assertTrue(has_special, "Password missing a special character from the approved set.")

    # Test 9d: Ensure generated passwords are unique
    def test_users_test_managers_UserManager_generate_secure_password_uniqueness(self):
        password_set = {self.user_manager.generate_secure_password() for _ in range(10)}
        self.assertGreater(len(password_set), 1, "Generated passwords should not be identical.")

    # Test 9e: Ensure attempting to generate a password below 16 characters raises ValueError
    def test_users_test_managers_UserManager_generate_secure_password_min_length_violation(self):

        with self.assertRaises(ValueError, msg="Password length below 16 should raise a ValueError."):
            self.user_manager.generate_secure_password(length=12)

    # Test 9f: Raises ValueError if required character sets are empty
    def test_users_test_managers_UserManager_generate_secure_password_raises_if_charset_missing(self):
        manager = self.user_manager

        # Patch 'SPECIAL_CHARACTERS' to an empty list to force IndexError
        with patch("users.managers.secrets.choice", side_effect=IndexError("Empty sequence")):
            with self.assertRaises(ValueError) as context:
                manager.generate_secure_password()
            self.assertIn("Character set missing required characters", str(context.exception))
    
    # Test 9g: Raises ValueError if final password fails complexity check
    def test_users_test_managers_UserManager_generate_secure_password_complexity_check_fails(self):
        manager = self.user_manager

        # Patch secrets.choice and random_chars to force bad password output
        with patch("users.managers.secrets.choice", return_value="a"):  # Force lowercase
            with self.assertRaises(ValueError) as context:
                manager.generate_secure_password()
            self.assertIn("Generated password does not meet complexity requirements", str(context.exception))

    """
    Comprehensive test coverage for the UserManager create_user() method and its supporting logic.

    Purpose:
        - Validate correct user creation and error handling under various conditions.
        - Ensure password generation, normalization, validation, and secure storage function as expected.
        - Verify duplicate protection, email delivery, and failure handling.

    Test Coverage Includes:

    Standalone Tests (Direct create_user Behavior & Constraints)
        - Successful user creation with all required fields populated.
        - Automatic email normalization (trimming whitespace and lowercasing).
        - Ensuring password is properly hashed and secure.
        - Validation that users are active by default unless explicitly set inactive.
        - Proper handling of is_active=False when provided.
        - Raises ValueError if email is missing or blank.
        - Raises ValueError if login identifiers (username, badge_barcode, badge_rfid) are missing.
        - Prevents active duplicate creation of:
            - Email
            - Username
            - Badge Barcode
            - Badge RFID
        - Validates support for creating users with **all unique identifiers** present.
        - Raises ValueError when a blank password is passed (security enforcement).

    Grouped Functional Test Blocks
        1. Password Complexity & Generation Tests
            - Validates all complexity requirements (uppercase, lowercase, digits, special characters).
            - Ensures minimum length.
    
        2. Inactive User Duplicate Handling
            - Confirms inactive users can reuse unique identifiers of other inactive users without conflict.

        3. Email Delivery Tests
            - Verifies email is sent correctly, with the correct recipient, subject, and content (login credentials).

        4. Email Failure Handling Tests
            - Ensures that email delivery failures do not break user creation.
            - Confirms email failure properly sets `email_sent = False`.

    Expectations:
        - The create_user() method strictly enforces all required fields, uniqueness, and password security.
        - The system allows duplicate inactive records where expected but blocks duplicates on active users.
        - Emails are reliably sent upon success and safely handled when failures occur.
        - Passwords are securely generated, validated, and hashed before storage.
    """

    # Test 10a: Ensure a user can be created successfully
    def test_users_test_managers_UserManager_create_user_success(self):
        user, _ = self.user_manager.create_user(
            email="user5@example.com",
            username="userfive",
            password=None,  # Auto-generated
            first_name="Jane",
            last_name="Doe",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
        )

        self.assertIsInstance(user, User, "User creation failed, did not return a User instance.")

    # Test 10b: Ensure the email is normalized correctly
    def test_users_test_managers_UserManager_create_user_email_normalization(self):
        unique_timestamp = int(time.time())
        raw_email = f"  NEWUSER_{unique_timestamp}@EXAMPLE.COM  "
        expected_email = raw_email.strip().lower()

        user, _ = self.user_manager.create_user(
            email=raw_email,
            username=f"testuser_{unique_timestamp}",
            password=None,
            first_name="Jane",
            last_name="Doe",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
        )

        self.assertEqual(user.email, expected_email, "Email was not normalized before saving.")
    
    # Test 10c: Ensure the password is set and hashed correctly
    def test_users_test_managers_UserManager_create_user_password_is_hashed(self):
        unique_timestamp = int(time.time())
        raw_email = f"  NEWUSER_{unique_timestamp}@EXAMPLE.COM  "

        user, _ = self.user_manager.create_user(
            email=raw_email,
            username=f"testuser_{unique_timestamp}",
            password=None,
            first_name="Jane",
            last_name="Doe",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
        )

        self.assertTrue(user.password.startswith("pbkdf2_"), "Password should be hashed.")
    
    """
    Tests the password complexity requirements enforced during create_user() 
        by validating the behavior of the generate_secure_password() method.

    Purpose:
        - Ensures generated passwords meet all defined security complexity standards.
        - Verifies inclusion of all required character types.
        - Confirms the password length complies with the minimum requirement.

    Expected Behavior:
        - Each generated password contains at least one uppercase letter (A-Z).
        - Each generated password contains at least one lowercase letter (a-z).
        - Each generated password contains at least one numeric digit (0-9).
        - Each generated password includes at least one special character from the allowed set.
        - Generated passwords are a minimum of 16 characters in length.

    Test Cases:
        1. **Uppercase Requirement**  
            - Validates that the password includes at least one uppercase letter.
        2. **Lowercase Requirement**  
            - Validates that the password includes at least one lowercase letter.
        3. **Digit Requirement**  
            - Validates that the password includes at least one numeric digit.
        4. **Special Character Requirement**  
            - Validates that the password includes at least one special character from the approved list.
        5. **Minimum Length Requirement**  
            - Validates that the password is at least 16 characters long.

    Guarantees that passwords generated for user accounts meet all complexity
        requirements, supporting system security and compliance.
    """
    
    # Test 10d_1: Ensure generated password contains at least one uppercase letter
    def test_UserManager_generate_secure_password_contains_uppercase(self):
        password = self.user_manager.generate_secure_password()
        self.assertTrue(any(c.isupper() for c in password), "Password must contain at least one uppercase letter.")

    # Test 10d_2: Ensure generated password contains at least one lowercase letter
    def test_UserManager_generate_secure_password_contains_lowercase(self):
        password = self.user_manager.generate_secure_password()
        self.assertTrue(any(c.islower() for c in password), "Password must contain at least one lowercase letter.")

    # Test 10d_3: Ensure generated password contains at least one digit
    def test_UserManager_generate_secure_password_contains_digit(self):
        password = self.user_manager.generate_secure_password()
        self.assertTrue(any(c.isdigit() for c in password), "Password must contain at least one digit.")

    # Test 10d_4: Ensure generated password contains at least one special character
    def test_UserManager_generate_secure_password_contains_special_character(self):
        special_characters = self.user_manager.SPECIAL_CHARACTERS
        password = self.user_manager.generate_secure_password()
        self.assertTrue(any(c in special_characters for c in password), "Password must contain at least one special character.")

    # Test 10d_5: Ensure generated password meets minimum length requirement
    def test_UserManager_generate_secure_password_meets_length_requirement(self):
        password = self.user_manager.generate_secure_password()
        self.assertGreaterEqual(len(password), 16, "Password must be at least 16 characters long.")

    # Test 10e: Ensure newly created users are active by default
    def test_UserManager_create_user_defaults_is_active_to_true(self):
        user, _  = self.user_manager.create_user(
            email="defaultactive@example.com",
            username="defaultactiveuser",
            password=None,
            first_name="Jane",
            last_name="Doe",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
        )

        self.assertTrue(user.is_active, "New users should be active by default.")

    # Test 10f: Ensure is_active=False when explicitly set
    def test_UserManager_create_user_explicitly_sets_is_active_false(self):
        user, _  = self.user_manager.create_user(
            email="inactiveuser@example.com",
            username="inactiveuser",
            password=None,
            first_name="John",
            last_name="Doe",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            is_active=False,  # Explicitly setting is_active=False
        )

        self.assertFalse(user.is_active, "User should remain inactive when explicitly set to False.")
    
    # Test 10g: Ensure missing email raises ValueError
    def test_users_test_managers_UserManager_create_user_missing_email_fails(self):
        with self.assertRaises(ValueError, msg="Expected ValueError when creating a user without an email."):
            self.user_manager.create_user(
                email=None,
                username="testuser_no_email",
                password=None,
                first_name="John",
                last_name="Doe",
                organization_id=self.organization1.id,
                site_id=self.site1.id,
            )
    
    # Test 10h: Ensure missing login identifier raises ValueError
    def test_users_test_managers_UserManager_create_user_missing_login_identifier_fails(self):
        with self.assertRaises(ValueError, msg="Expected ValueError when creating a user without a login identifier."):
            self.user_manager.create_user(
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
            
    # Test 10i: Ensure duplicate username raises ValueError
    def test_users_test_managers_UserManager_create_user_duplicate_username_fails(self):
        with self.assertRaises(ValueError, msg="Expected ValueError when creating a user with a duplicate username."):
            self.user_manager.create_user(
                email="uniqueuser@example.com",
                username=self.user1.username,  # Duplicate username from setUp()
                password=None,
                first_name="John",
                last_name="Doe",
                organization_id=self.organization1.id,
                site_id=self.site1.id,
            )

    # Test 10j: Ensure duplicate badge_barcode raises ValueError
    def test_users_test_managers_UserManager_create_user_duplicate_badge_barcode_fails(self):
        with self.assertRaises(ValueError, msg="Expected ValueError when creating a user with a duplicate badge barcode."):
            self.user_manager.create_user(
                email="barcodeuser@example.com",
                username="barcodeuser",
                badge_barcode=self.user1.badge_barcode,  # Duplicate barcode from setUp()
                password=None,
                first_name="John",
                last_name="Doe",
                organization_id=self.organization1.id,
                site_id=self.site1.id,
            )

    # Test 10k: Ensure duplicate badge_rfid raises ValueError
    def test_users_test_managers_UserManager_create_user_duplicate_badge_rfid_fails(self):
        with self.assertRaises(ValueError, msg="Expected ValueError when creating a user with a duplicate badge RFID."):
            self.user_manager.create_user(
                email="rfiduser@example.com",
                username="rfiduser",
                badge_rfid=self.user1.badge_rfid,  # Duplicate RFID from setUp()
                password=None,
                first_name="John",
                last_name="Doe",
                organization_id=self.organization1.id,
                site_id=self.site1.id,
            )

    # Test 10l: Ensure duplicate email raises ValueError
    # This test checks duplicate emails *only* against active users
    def test_users_test_managers_UserManager_create_user_duplicate_email_fails(self):
        with self.assertRaises(ValueError, msg="Expected ValueError when creating a user with a duplicate email."):
            self.user_manager.create_user(
                email=self.user1.email,  # Duplicate email from setUp()
                username="duplicateuser",
                password=None,
                first_name="John",
                last_name="Doe",
                organization_id=self.organization1.id,
                site_id=self.site1.id,
            )

    # Test 10m: Ensure a user can be created with all unique identifiers
    def test_UserManager_create_user_with_all_unique_identifiers(self):
        user, _  = self.user_manager.create_user(
            email="multiiduser@example.com",
            username="multiiduser",
            password=None,
            first_name="Alex",
            last_name="Smith",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="BARCODE99999",
            badge_rfid="RFID99999",
        )

        # Refresh from the database to confirm it was saved
        # If user was not saved in db, calling "refresh_from_db()" will raise "User.DoesNotExist" error.
        user.refresh_from_db()

        self.assertIsInstance(user, User, "User creation failed when using all unique identifiers.")

    """
    Tests the create_user() method behavior when creating inactive users 
        with duplicate identifiers.

    Purpose:
        - Verifies that the system allows inactive users to share the same 
          unique identifiers (email, username, badge_barcode, badge_rfid) 
          as other inactive users.
        - Ensures that uniqueness constraints only apply to active users.

    Expected Behavior:
        - The system permits creation of inactive users even if their email,
          username, badge_barcode, or badge_rfid duplicates another inactive user.
        - Duplicate identifiers among inactive users should not raise a ValueError.
        - Each inactive user is properly saved and returned as a valid User instance.

    Test Cases:
        1. **Duplicate Email Allowed for Inactive Users**
            - Ensures inactive users can share the same email address.
        2. **Duplicate Username Allowed for Inactive Users**
            - Ensures inactive users can share the same username.
        3. **Duplicate Badge Barcode Allowed for Inactive Users**
            - Ensures inactive users can share the same badge barcode.
        4. **Duplicate Badge RFID Allowed for Inactive Users**
            - Ensures inactive users can share the same badge RFID.

    Guarantees the create_user() method correctly bypasses active-user uniqueness 
        onstraints when creating inactive users with duplicate identifiers.
    """

    # Test 10n_1: Ensure an inactive user can have a duplicate email
    def test_UserManager_inactive_user_can_have_duplicate_email(self):
        inactive_user, _  = self.user_manager.create_user(
            email=self.user2.email,  # Duplicate email from existing inactive user
            username="newinactiveuser",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="NEWBARCODE",
            badge_rfid="NEWRFID",
            is_active=False,  # New inactive user
        )

        self.assertIsInstance(inactive_user, User, "Inactive user should be allowed to have a duplicate email.")

    # Test 10n_2: Ensure an inactive user can have a duplicate username
    def test_UserManager_inactive_user_can_have_duplicate_username(self):
        inactive_user, _  = self.user_manager.create_user(
            email="newinactive@example.com",
            username=self.user2.username,  # Duplicate username from existing inactive user
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="NEWBARCODE",
            badge_rfid="NEWRFID",
            is_active=False,  # New inactive user
        )

        self.assertIsInstance(inactive_user, User, "Inactive user should be allowed to have a duplicate username.")

    # Test 10n_3: Ensure an inactive user can have a duplicate badge_barcode
    def test_UserManager_inactive_user_can_have_duplicate_badge_barcode(self):
        inactive_user, _  = self.user_manager.create_user(
            email="newinactive@example.com",
            username="newinactiveuser",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode=self.user2.badge_barcode,  # Duplicate badge_barcode from existing inactive user
            badge_rfid="NEWRFID",
            is_active=False,  # New inactive user
        )

        self.assertIsInstance(inactive_user, User, "Inactive user should be allowed to have a duplicate badge_barcode.")

    # Test 10n_4: Ensure an inactive user can have a duplicate badge_rfid
    def test_UserManager_inactive_user_can_have_duplicate_badge_rfid(self):
        inactive_user, _  = self.user_manager.create_user(
            email="newinactive@example.com",
            username="newinactiveuser",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="NEWBARCODE",
            badge_rfid=self.user2.badge_rfid,  # Duplicate badge_rfid from existing inactive user
            is_active=False,  # New inactive user
        )

        self.assertIsInstance(inactive_user, User, "Inactive user should be allowed to have a duplicate badge_rfid.")

    """
    Tests the create_user() method's email delivery functionality and 
        the accuracy of email content.

    Purpose:
        - Ensures that an email is sent after successful user creation.
        - Verifies that the email is sent to the correct recipient.
        - Confirms the email subject is correct.
        - Validates that the email body contains all required user credentials
          and login information.

    Expected Behavior:
        - A single email is sent and captured in Django's test mail outbox.
        - The recipient's email address matches the created user's email.
        - The subject line is "Your Account Credentials".
        - The body contains the user’s email, username, badge barcode, badge RFID,
          and the temporary password generated during creation.
        - The temporary password is properly extracted and present in the email.

    Test Cases:
        1. **Email is Sent**
            - Verifies that exactly one email is sent after user creation.
        2. **Correct Email Recipient**
            - Ensures the email is sent to the user’s registered email address.
        3. **Correct Subject Line**
            - Checks that the email subject is set as expected.
        4. **Email Body Content Verification**
            - Confirms the body contains:
                - The user's email address.
                - The user's username.
                - The user's badge barcode.
                - The user's badge RFID.
                - The temporary password extracted from the email content.

    Guarantees the create_user() method reliably handles email notifications, 
        preserves user credential accuracy, and provides all necessary login information 
        for the user in the email body.
    """

    # Test 10o_1: Ensure an email is sent after user creation
    def test_UserManager_create_user_sends_email(self):
    
        self.user_manager.create_user(
            email="emailtest@example.com",
            username="emailtestuser",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="BARCODEEMAILTEST",
            badge_rfid="RFIDEMAILTEST",
        )

        self.assertEqual(len(mail.outbox), 1, "No email was sent after user creation.")

    # Test 10o_2: Ensure email is sent to the correct recipient
    def test_UserManager_create_user_email_recipient_is_correct(self):
    
        user, _  = self.user_manager.create_user(
            email="emailtest@example.com",
            username="emailtestuser",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="BARCODEEMAILTEST",
            badge_rfid="RFIDEMAILTEST",
        )

        sent_email = mail.outbox[0]

        self.assertEqual(sent_email.to, [user.email], "Email was not sent to the correct recipient.")

    # Test 10o_3: Ensure email subject is correct
    def test_UserManager_create_user_email_subject_is_correct(self):
    
        self.user_manager.create_user(
            email="emailtest@example.com",
            username="emailtestuser",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="BARCODEEMAILTEST",
            badge_rfid="RFIDEMAILTEST",
        )

        sent_email = mail.outbox[0]

        self.assertEqual(sent_email.subject, "Your Account Credentials", "Email subject does not match.")

    # Test 10o_4_1: Ensure email contains the correct email address
    def test_UserManager_create_user_email_contains_email(self):
    
        user, _  = self.user_manager.create_user(
            email="emailtest@example.com",
            username="emailtestuser",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="BARCODEEMAILTEST",
            badge_rfid="RFIDEMAILTEST",
        )

        sent_email = mail.outbox[0]

        self.assertIn(f"Email: {user.email}", sent_email.body, "Email missing in email body.")

    # Test 10o_4_2: Ensure email contains the correct username
    def test_UserManager_create_user_email_contains_username(self):
    
        user, _  = self.user_manager.create_user(
            email="emailtest@example.com",
            username="emailtestuser",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="BARCODEEMAILTEST",
            badge_rfid="RFIDEMAILTEST",
        )

        sent_email = mail.outbox[0]

        self.assertIn(f"Username: {user.username}", sent_email.body, "Username missing in email body.")

    # Test 10o_4_3: Ensure email contains the correct badge barcode
    def test_UserManager_create_user_email_contains_badge_barcode(self):
    
        user, _  = self.user_manager.create_user(
            email="emailtest@example.com",
            username="emailtestuser",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="BARCODEEMAILTEST",
            badge_rfid="RFIDEMAILTEST",
        )

        sent_email = mail.outbox[0]

        self.assertIn(f"Badge Barcode: {user.badge_barcode}", sent_email.body, "Badge Barcode missing in email body.")

    # Test 10o_4_4: Ensure email contains the correct badge RFID
    def test_UserManager_create_user_email_contains_badge_rfid(self):
    
        user, _  = self.user_manager.create_user(
            email="emailtest@example.com",
            username="emailtestuser",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="BARCODEEMAILTEST",
            badge_rfid="RFIDEMAILTEST",
        )

        sent_email = mail.outbox[0]

        self.assertIn(f"Badge RFID: {user.badge_rfid}", sent_email.body, "Badge RFID missing in email body.")

    # Test 10o_4_5: Ensure the email contains the correct temporary password
    def test_UserManager_create_user_email_contains_temporary_password(self):

        user, _  = self.user_manager.create_user(
            email="emailtest@example.com",
            username="emailtestuser",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="BARCODEEMAILTEST",
            badge_rfid="RFIDEMAILTEST",
        )

        sent_email = mail.outbox[0]

        # Extract the actual password from the email body, since we do not want to have a non hashed password outside of the create_user method
        email_lines = sent_email.body.split("\n")
        plaintext_password = None
        for line in email_lines:
            if "Temporary Password:" in line:
                plaintext_password = line.replace("Temporary Password:", "").strip()
                break

        self.assertIn(f"Temporary Password: {plaintext_password}", sent_email.body, "Temporary Password missing in email body.")

    """
    Tests the create_user() method's behavior when email delivery fails.

    Purpose:
        - Ensures that the user creation process is robust and does not fail
          if sending the email fails.
        - Verifies that user records are still created even when email delivery
          is unsuccessful.
        - Confirms that the email_sent flag is correctly set to False when
          email sending fails.

    Expected Behavior:
        - No exceptions are raised if email delivery fails due to an SMTP error.
        - User creation succeeds and returns a valid User instance.
        - The email_sent flag is False, reflecting that email delivery did not succeed.

    Test Cases:
        1. **Graceful Handling of Email Failure**
            - Simulates an SMTP failure and ensures no unhandled exceptions occur.
        2. **User Still Created on Email Failure**
            - Confirms that the user is fully created and persisted even when the email fails.
        3. **Email Sent Flag is False**
            - Validates that the email_sent flag accurately reflects the failure state.

    Guarantees that the create_user() method is resilient against email delivery failures
        and maintains system stability and user data integrity.
    """

    #Test 10p_1: Ensure create_user does not raise an error when email fails
    @patch("django.core.mail.send_mail", side_effect=smtplib.SMTPException("Simulated email failure"))
    def test_UserManager_create_user_handles_email_failure_gracefully(self, mock_send_mail):
    
        try:
            user, email_sent = self.user_manager.create_user(
                email="failedemail@example.com",
                username="emailfailtest",
                password=None,
                first_name="Test",
                last_name="User",
                organization_id=self.organization1.id,
                site_id=self.site1.id,
                created_by_id=None,
                badge_barcode="BARCODEEMAILFAIL",
                badge_rfid="RFIDEMAILFAIL",
            )
        except Exception as e:
            self.fail(f"create_user() raised an exception when email failed: {e}")

    # Test 10p_2: Ensure create_user still creates a user even when email fails
    @patch("django.core.mail.send_mail", side_effect=smtplib.SMTPException("Simulated email failure"))
    def test_UserManager_create_user_creates_user_even_when_email_fails(self, mock_send_mail):
    
        user, email_sent = self.user_manager.create_user(
            email="failedemail@example.com",
            username="emailfailtest",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="BARCODEEMAILFAIL",
            badge_rfid="RFIDEMAILFAIL",
        )


        self.assertIsInstance(user, User, "User was not created when email failed.")
    
    @patch("users.managers.send_mail", side_effect=smtplib.SMTPException("Simulated email failure"))
    # Test 10p_3: Ensure email_sent is False when email fails
    def test_UserManager_create_user_email_sent_flag_is_false_on_failure(self,mock_send_mail):

        user, email_sent = self.user_manager.create_user(
            email="failedemail@example.com",
            username="emailfailtest",
            password=None,
            first_name="Test",
            last_name="User",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
            badge_barcode="BARCODEEMAILFAIL",
            badge_rfid="RFIDEMAILFAIL",
        )

        self.assertFalse(email_sent, "email_sent should be False when email sending fails.")

    # Test 10q: Ensure ValueError is raised if blank password is provided
    def test_UserManager_create_user_raises_error_on_blank_password(self):

        with self.assertRaises(ValueError) as context:
            self.user_manager.create_user(
                email="blankpassword@example.com",
                username="blankpassuser",
                password="",  # Explicitly passing blank
                first_name="Test",
                last_name="User",
                organization_id=self.organization1.id,
                site_id=self.site1.id,
                created_by_id=None,
                badge_barcode="BARCODEBLANK",
                badge_rfid="RFIDBLANK",
            )

        self.assertEqual(str(context.exception), "A valid password must be set and cannot be blank.")