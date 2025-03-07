from django.test import TestCase
from django.apps import apps
from users.models import User
from users.managers import UserManager
from organizations.models import Organization
from sites.models import Site
from django.utils.timezone import now
from datetime import timedelta
import time
import string
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
        - Currently, this method only prints a status message.
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
            id = "1",
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
            id = "2",
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
            id = "1",
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
            id = "2",
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
            id = "1",
            email="user1@example.com",
            username="userone",
            password="SecurePass123!",
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

        self.user2 = User.objects.using("users_db").create(
            id = "2",
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

        self.user3 = User.objects.using("users_db").create(
            id = "3",
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

        self.user4 = User.objects.using("users_db").create(
            id = "4",
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
        has_special = any(c in string.punctuation for c in password)
        self.assertTrue(has_special, "Password missing a special character.")

    # Test 9d: Ensure generated passwords are unique
    def test_users_test_managers_UserManager_generate_secure_password_uniqueness(self):
        password_set = {self.user_manager.generate_secure_password() for _ in range(10)}
        self.assertGreater(len(password_set), 1, "Generated passwords should not be identical.")

    # Test 9e: Ensure attempting to generate a password below 16 characters raises ValueError
    def test_users_test_managers_UserManager_generate_secure_password_min_length_violation(self):

        with self.assertRaises(ValueError, msg="Password length below 16 should raise a ValueError."):
            self.user_manager.generate_secure_password(length=12)

    """
    Tests the create_user() method in UserManager to ensure correct user creation and error handling.

    Purpose:
        - Ensures that users are created successfully with all required fields.
        - Validates that passwords are securely generated and hashed.
        - Confirms that email normalization occurs before saving.
        - Enforces constraints on required fields.
        - Ensures duplicate emails cannot be registered.

    Expected Behavior:
        - The user is created with a unique email, username, and assigned organization/site.
        - The email is properly normalized (lowercased & trimmed).
        - A password is auto-generated, securely hashed, and never stored in plain text.
        - Attempting to create a user without an email should raise a `ValueError`.
        - Attempting to create a user without a login identifier (username, badge) should raise a `ValueError`.
        - Attempting to create a user with a duplicate email should raise a `ValueError`.

    Test Cases:
        1. **Create a User with Valid Data**  
            - Generates a unique email and ensures proper normalization.
            - Confirms a password is automatically generated and securely hashed.
        2. **Negative Test Case: Missing Email**  
            - Attempting to create a user without an email should raise a `ValueError`.
        3. **Negative Test Case: Missing Login Identifier**  
            - Attempting to create a user without a username, badge barcode, or badge RFID should raise a `ValueError`.
        4. **Negative Test Case: Duplicate Email**  
            - Attempting to create a second user with the same email should raise a `ValueError`.

    Guarantees that create_user() correctly handles required fields, email formatting, password security, and error handling.
    """

    # Test 10a: Ensure a user can be created successfully
    def test_users_test_managers_UserManager_create_user_success(self):
        user = self.user_manager.create_user(
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

        user = self.user_manager.create_user(
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

        user = self.user_manager.create_user(
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
    
    # Test 10d: Ensure missing email raises ValueError
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

    # Test 10e: Ensure missing login identifier raises ValueError
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

    # Test 10f: Ensure duplicate email raises ValueError
    def test_users_test_managers_UserManager_create_user_duplicate_email_fails(self):
        unique_timestamp = int(time.time())
        raw_email = f"  NEWUSER_{unique_timestamp}@EXAMPLE.COM  "
        expected_email = raw_email.strip().lower()

        self.user_manager.create_user(
            email=raw_email,
            username=f"testuser_{unique_timestamp}",
            password=None,
            first_name="Jane",
            last_name="Doe",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            created_by_id=None,
        )

        with self.assertRaises(ValueError, msg="Expected ValueError when creating a user with a duplicate email."):
            self.user_manager.create_user(
                email=expected_email,  # Duplicate email
                username="duplicateuser",
                password=None,
                first_name="John",
                last_name="Doe",
                organization_id=self.organization1.id,
                site_id=self.site1.id,
            )

    """
    Tests the v method in UserManager to ensure correct user updates.

    Purpose:
        - Verifies that user attributes can be updated successfully.
        - Ensures that email normalization is applied correctly.
        - Confirms that foreign key fields update properly.
        - Enforces login identifier constraints.
        - Tests error handling for invalid user updates.

    Verification Steps:
        1. **Update Username**:
            - Modifies the username and confirms persistence in the database.
        2. **Normalize Email on Update**:
            - Provides an untrimmed and uppercase email, then checks if it is normalized.
        3. **Update Foreign Key Fields**:
            - Changes `organization_id` and `site_id`, then verifies updates.
        4. **Ensure Login Identifiers Remain Valid**:
            - Attempts to remove all login identifiers (username, badge), which should raise a `ValueError`.
        5. **Handle Non-Existent User Update**:
            - Tries to update a user that does not exist and confirms that a `ValueError` is raised.

    Guarantees that `update_user()` correctly enforces constraints and persists data accurately.
    """

    # Test 11a: Ensure username updates successfully
    def test_users_test_managers_UserManager_update_user_username_success(self):
        updated_username = "updateduser"
        self.user_manager.update_user(self.user1.id, username=updated_username)

        updated_user = User.objects.using("users_db").get(id=self.user1.id)
        self.assertEqual(updated_user.username, updated_username, "Username did not update correctly.")

    # """
    # Tests the delete_user() method in UserManager to ensure correct user deletion.

    # Purpose:
    #     - Confirms that a user can be deleted successfully.
    #     - Ensures that the delete_user() method explicitly prevents deletion of superusers.
    #     - Ensures proper error handling when deleting non-existent users.

    # Verification Steps:
    #     1. **Delete a Regular User**:
    #         - Calls `delete_user()` and confirms the user is removed.
    #     2. **Confirm Superuser Deletion is Blocked**:
    #         - Attempts to delete a superuser, which is hardcoded in `delete_user()` to raise a `ValueError`.
    #         - This restriction ensures that superusers can only be deleted using `delete_superuser()`.
    #     3. **Handle Non-Existent User Deletion**:
    #         - Tries to delete a user that does not exist and verifies that a `ValueError` is raised.

    # Guarantees that `delete_user()` enforces proper constraints and handles errors correctly.
    # """

    # def test_user_manager_delete_user(self):
    #     print("\n--- DEBUG: Running test_user_manager_delete_user ---")

    #     # Case 1: Successfully delete a regular user
    #     user = User.objects.db_manager("users_db").get(id=self.user1.id)
    #     print(f"🔹 Before Deletion: User Found - ID: {user.id}, Email: {user.email}")

    #     User.objects.db_manager("users_db").delete_user(self.user1.id)

    #     # Confirm user is deleted
    #     print("⏳ Checking if user still exists after deletion...")
    #     with self.assertRaises(User.DoesNotExist):
    #         deleted_user = User.objects.db_manager("users_db").get(id=self.user1.id)
    #         print(f"❌ User still exists: {deleted_user.id}")  # Should NOT execute

    #     print("✅ User successfully deleted (DoesNotExist Exception raised).")

    #     # Case 2: Attempt to delete a superuser (should raise ValueError)
    #     superuser = User.objects.db_manager("users_db").create_user(
    #         email="superuser@example.com",
    #         username="superadmin",
    #         password="SecurePass123!",
    #         is_superuser=True
    #     )

    #     print(f"🔹 Created Superuser: ID {superuser.id}, Email: {superuser.email}")

    #     with self.assertRaises(ValueError):
    #         print("🔴 Attempting to delete a superuser (should raise an error)")
    #         User.objects.db_manager("users_db").delete_user(superuser.id)

    #     # Case 3: Attempt to delete a non-existent user (should raise ValueError)
    #     with self.assertRaises(ValueError):
    #         print("🔴 Attempting to delete a non-existent user (should raise an error)")
    #         User.objects.db_manager("users_db").delete_user(user_id=999999)

    #     print("--- END DEBUG ---\n")

    # """
    # Tests the create_superuser() method in UserManager to ensure proper superuser creation.

    # Expected Behavior:
    #     - Superusers should always have `is_staff=True` and `is_superuser=True`.
    #     - If `is_staff` or `is_superuser` are set to False, an error should be raised.
    #     - Calls `create_user()` and ensures superuser constraints are applied.

    # Test Cases:
    #     1. Successfully create a superuser and verify attributes.
    #     2. Attempt to create a superuser with `is_superuser=False` (should raise `ValueError`).
    #     3. Attempt to create a superuser with `is_staff=False` (should raise `ValueError`).
    # """
    # def test_user_manager_create_superuser(self):
    

    #     print("\n--- DEBUG: Running test_user_manager_create_superuser ---")

    #     # Case 1: Successfully create a superuser
    #     superuser = User.objects.db_manager("users_db").create_superuser(
    #         email="admin@example.com",
    #         username="adminuser",
    #         password="SecurePass123!"
    #     )

    #     print(f"✅ Created Superuser ID: {superuser.id}")
    #     print(f"User Email: {superuser.email} (Expected: admin@example.com)")
    #     print(f"User Username: {superuser.username} (Expected: adminuser)")
    #     print(f"User is_staff: {superuser.is_staff} (Expected: True)")
    #     print(f"User is_superuser: {superuser.is_superuser} (Expected: True)")

    #     # Assertions
    #     self.assertEqual(superuser.email, "admin@example.com", "❌ Email does not match expected value.")
    #     self.assertEqual(superuser.username, "adminuser", "❌ Username does not match expected value.")
    #     self.assertTrue(superuser.is_staff, "❌ Superuser should have is_staff=True.")
    #     self.assertTrue(superuser.is_superuser, "❌ Superuser should have is_superuser=True.")

    #     # Case 2: Attempt to create a superuser with is_superuser=False (should raise ValueError)
    #     with self.assertRaises(ValueError):
    #         print("🔴 Attempting to create a superuser with is_superuser=False (should raise an error)")
    #         User.objects.db_manager("users_db").create_superuser(
    #             email="invalid_admin@example.com",
    #             username="invalidadmin",
    #             password="SecurePass123!",
    #             is_superuser=False
    #         )

    #     # Case 3: Attempt to create a superuser with is_staff=False (should raise ValueError)
    #     with self.assertRaises(ValueError):
    #         print("🔴 Attempting to create a superuser with is_staff=False (should raise an error)")
    #         User.objects.db_manager("users_db").create_superuser(
    #             email="invalid_staff@example.com",
    #             username="invalidstaff",
    #             password="SecurePass123!",
    #             is_staff=False
    #         )

    #     print("--- END DEBUG ---\n")

    # """
    # Tests the update_superuser() method in UserManager to ensure superuser updates function correctly.

    # Expected Behavior:
    #     - Allows updating superuser attributes while enforcing required constraints.
    #     - Ensures `is_staff` and `is_superuser` remain `True`.
    #     - Normalizes email before saving.
    #     - Ensures at least one login identifier remains set.
    #     - Raises errors for invalid update attempts.

    # Test Cases:
    #     1. Successfully update a superuser's attributes.
    #     2. Ensure email normalization when updating email.
    #     3. Update foreign key fields (`organization_id`, `site_id`, `modified_by_id`) and confirm persistence.
    #     4. Attempt to remove all login identifiers (should raise `ValueError`).
    #     5. Attempt to update a non-superuser (should raise `ValueError`).
    #     6. Attempt to update a non-existent superuser (should raise `ValueError`).
    # """
    # def test_user_manager_update_superuser(self):
    
    #     print("\n--- DEBUG: Running test_user_manager_update_superuser ---")

    #     # Case 1: Successfully update superuser attributes
    #     superuser = User.objects.db_manager("users_db").create_superuser(
    #         email="superadmin@example.com",
    #         username="superadmin",
    #         password="SecurePass123!"
    #     )

    #     print(f"🔹 Before Update: Username: {superuser.username}")

    #     updated_superuser = User.objects.db_manager("users_db").update_superuser(
    #         superuser.id, username="updatedsuperadmin"
    #     )

    #     print(f"✅ After Update: Username: {updated_superuser.username} (Expected: updatedsuperadmin)")
    #     self.assertEqual(updated_superuser.username, "updatedsuperadmin", "❌ Username did not update correctly.")

    #     # Case 2: Ensure email normalization when updating email
    #     raw_email = "  UPDATEDSUPER@EXAMPLE.COM  "
    #     expected_email = raw_email.strip().lower()

    #     updated_superuser = User.objects.db_manager("users_db").update_superuser(
    #         superuser.id, email=raw_email
    #     )

    #     print(f"✅ After Email Update: {updated_superuser.email} (Expected: {expected_email})")
    #     self.assertEqual(updated_superuser.email, expected_email, "❌ Email was not normalized correctly.")

    #     # Case 3: Update foreign key fields and verify
    #     new_organization = Organization.objects.using("organizations_db").create(
    #         name="New Super Organization",
    #         type_id=2,
    #         active=True,
    #         created_by_id=None
    #     )

    #     new_site = Site.objects.using("sites_db").create(
    #         name="New Super Site",
    #         organization_id=new_organization.id,
    #         site_type="Datacenter",
    #         address="789 Super St",
    #         active=True,
    #         created_by_id=None
    #     )

    #     updated_superuser = User.objects.db_manager("users_db").update_superuser(
    #         superuser.id,
    #         organization_id=new_organization.id,
    #         site_id=new_site.id,
    #         modified_by_id=superuser.id
    #     )

    #     print(f"✅ After FK Update: Org ID: {updated_superuser.organization_id}, Site ID: {updated_superuser.site_id}")

    #     self.assertEqual(updated_superuser.organization_id, new_organization.id, "❌ Organization ID did not update correctly.")
    #     self.assertEqual(updated_superuser.site_id, new_site.id, "❌ Site ID did not update correctly.")

    #     # Case 4: Attempt to remove all login identifiers (should raise ValueError)
    #     with self.assertRaises(ValueError):
    #         print("🔴 Attempting to remove all login identifiers (should raise an error)")
    #         User.objects.db_manager("users_db").update_superuser(
    #             superuser.id,
    #             username=None,
    #             badge_barcode=None,
    #             badge_rfid=None
    #         )

    #     # Case 5: Attempt to update a non-superuser (should raise ValueError)
    #     regular_user = User.objects.db_manager("users_db").create_user(
    #         email="regular@example.com",
    #         username="regularuser",
    #         password="SecurePass123!"
    #     )

    #     with self.assertRaises(ValueError):
    #         print("🔴 Attempting to update a non-superuser (should raise an error)")
    #         User.objects.db_manager("users_db").update_superuser(regular_user.id, username="shouldfail")

    #     # Case 6: Attempt to update a non-existent superuser (should raise ValueError)
    #     with self.assertRaises(ValueError):
    #         print("🔴 Attempting to update a non-existent superuser (should raise an error)")
    #         User.objects.db_manager("users_db").update_superuser(user_id=999999, username="ghostsuper")

    #     print("--- END DEBUG ---\n")

    # """
    # Tests the delete_superuser() method in UserManager to ensure proper superuser deletion.

    # Expected Behavior:
    #     - Successfully deletes a superuser when multiple superusers exist.
    #     - Prevents deletion of the last remaining superuser.
    #     - Raises an error if attempting to delete a non-existent superuser.

    # Test Cases:
    #     1. Successfully delete a superuser when more than one exists.
    #     2. Attempt to delete the last remaining superuser (should raise `ValueError`).
    #     3. Attempt to delete a non-existent superuser (should raise `ValueError`).
    # """

    # def test_user_manager_delete_superuser(self):
    

    #     print("\n--- DEBUG: Running test_user_manager_delete_superuser ---")

    #     # Case 1: Successfully delete a superuser when multiple exist
    #     superuser1 = User.objects.db_manager("users_db").create_superuser(
    #         email="admin1@example.com",
    #         username="admin1",
    #         password="SecurePass123!"
    #     )

    #     superuser2 = User.objects.db_manager("users_db").create_superuser(
    #         email="admin2@example.com",
    #         username="admin2",
    #         password="SecurePass123!"
    #     )

    #     print(f"🔹 Created Superusers: {superuser1.id} (admin1), {superuser2.id} (admin2)")

    #     # Delete one superuser
    #     User.objects.db_manager("users_db").delete_superuser(superuser1.id)

    #     # Verify deletion
    #     with self.assertRaises(User.DoesNotExist):
    #         print("⏳ Checking if superuser1 still exists after deletion...")
    #         User.objects.db_manager("users_db").get(id=superuser1.id)

    #     print("✅ Superuser1 successfully deleted.")

    #     # Case 2: Attempt to delete the last remaining superuser (should raise ValueError)
    #     with self.assertRaises(ValueError):
    #         print("🔴 Attempting to delete the last remaining superuser (should raise an error)")
    #         User.objects.db_manager("users_db").delete_superuser(superuser2.id)

    #     # Case 3: Attempt to delete a non-existent superuser (should raise ValueError)
    #     with self.assertRaises(ValueError):
    #         print("🔴 Attempting to delete a non-existent superuser (should raise an error)")
    #         User.objects.db_manager("users_db").delete_superuser(user_id=999999)

    #     print("--- END DEBUG ---\n")

    # """
    # Tests the get_by_natural_key() method in UserManager to ensure correct user retrieval.

    # Expected Behavior:
    #     - Successfully retrieves an active user by email, username, badge barcode, or badge RFID.
    #     - Ensures that only active users are retrieved.
    #     - Raises a `User.DoesNotExist` error if no matching active user is found.

    # Test Cases:
    #     1. Retrieve a user by email.
    #     2. Retrieve a user by username.
    #     3. Retrieve a user by badge barcode.
    #     4. Retrieve a user by badge RFID.
    #     5. Attempt to retrieve an inactive user (should raise `User.DoesNotExist`).
    #     6. Attempt to retrieve a non-existent user (should raise `User.DoesNotExist`).
    # """

    # def test_user_manager_get_by_natural_key(self):
    

    #     print("\n--- DEBUG: Running test_user_manager_get_by_natural_key ---")

    #     # Create a user with multiple identifiers
    #     user = User.objects.db_manager("users_db").create_user(
    #         email="searchuser@example.com",
    #         username="searchuser",
    #         password="SecurePass123!",
    #         badge_barcode="123456",
    #         badge_rfid="ABCDEF",
    #         is_active=True
    #     )

    #     print(f"🔹 Created User ID: {user.id}, Email: {user.email}, Username: {user.username}")

    #     # Case 1: Retrieve user by email
    #     retrieved_user = User.objects.db_manager("users_db").get_by_natural_key("searchuser@example.com")
    #     print(f"✅ Retrieved by Email: {retrieved_user.email} (Expected: {user.email})")
    #     self.assertEqual(retrieved_user.id, user.id, "❌ Failed to retrieve user by email.")

    #     # Case 2: Retrieve user by username
    #     retrieved_user = User.objects.db_manager("users_db").get_by_natural_key("searchuser")
    #     print(f"✅ Retrieved by Username: {retrieved_user.username} (Expected: {user.username})")
    #     self.assertEqual(retrieved_user.id, user.id, "❌ Failed to retrieve user by username.")

    #     # Case 3: Retrieve user by badge barcode
    #     retrieved_user = User.objects.db_manager("users_db").get_by_natural_key("123456")
    #     print(f"✅ Retrieved by Badge Barcode: {retrieved_user.badge_barcode} (Expected: {user.badge_barcode})")
    #     self.assertEqual(retrieved_user.id, user.id, "❌ Failed to retrieve user by badge barcode.")

    #     # Case 4: Retrieve user by badge RFID
    #     retrieved_user = User.objects.db_manager("users_db").get_by_natural_key("ABCDEF")
    #     print(f"✅ Retrieved by Badge RFID: {retrieved_user.badge_rfid} (Expected: {user.badge_rfid})")
    #     self.assertEqual(retrieved_user.id, user.id, "❌ Failed to retrieve user by badge RFID.")

    #     # Case 5: Attempt to retrieve an inactive user (should raise User.DoesNotExist)
    #     inactive_user = User.objects.db_manager("users_db").create_user(
    #         email="inactiveuser@example.com",
    #         username="inactiveuser",
    #         password="SecurePass123!",
    #         is_active=False
    #     )

    #     with self.assertRaises(User.DoesNotExist):
    #         print("🔴 Attempting to retrieve an inactive user (should raise an error)")
    #         User.objects.db_manager("users_db").get_by_natural_key("inactiveuser@example.com")

    #     # Case 6: Attempt to retrieve a non-existent user (should raise User.DoesNotExist)
    #     with self.assertRaises(User.DoesNotExist):
    #         print("🔴 Attempting to retrieve a non-existent user (should raise an error)")
    #         User.objects.db_manager("users_db").get_by_natural_key("doesnotexist@example.com")

    #     print("--- END DEBUG ---\n")

    # """
    # Tests UserManager query methods that filter users by specific fields.

    # Purpose:
    #     - Ensures that users can be retrieved based on unique and searchable attributes.
    #     - Confirms that queries return the correct users while excluding incorrect ones.
    #     - Verifies that case-insensitive searches work where applicable.
    #     - Ensures that queries return an empty result when no matching users exist.

    # Verification Steps:
    #     1. **Retrieve a User by Email**:
    #         - Ensures `by_email()` returns the correct user.
    #         - Ensures `by_email()` returns no results when no match exists.
    #     2. **Retrieve a User by Username**:
    #         - Ensures `by_username()` returns the correct user.
    #         - Ensures `by_username()` returns no results when no match exists.
    #     3. **Retrieve a User by Badge Barcode**:
    #         - Ensures `by_badge_barcode()` returns the correct user.
    #         - Ensures `by_badge_barcode()` returns no results when no match exists.
    #     4. **Retrieve a User by Badge RFID**:
    #         - Ensures `by_badge_rfid()` returns the correct user.
    #         - Ensures `by_badge_rfid()` returns no results when no match exists.
    #     5. **Retrieve a User by First Name**:
    #         - Ensures `by_first_name()` returns users with a matching first name (case-insensitive).
    #         - Ensures `by_first_name()` returns no results when no match exists.
    #     6. **Retrieve a User by Last Name**:
    #         - Ensures `by_last_name()` returns users with a matching last name (case-insensitive).
    #         - Ensures `by_last_name()` returns no results when no match exists.
    #     7. **Retrieve a User by Full Name**:
    #         - Ensures `by_full_name()` returns users with a matching first and last name (case-insensitive).
    #         - Ensures `by_full_name()` returns no results when no match exists.

    # Guarantees that filtering by specific fields works as expected and excludes non-matching users.
    # """

    # def test_user_manager_filter_by_specific_fields(self):

    #     print("\n--- DEBUG: Running test_user_manager_filter_by_specific_fields ---")

    #     # ✅ Case 1: Retrieve user by email (Success)
    #     user = User.objects.db_manager("users_db").by_email("user1@example.com").first()
    #     print(f"✅ Retrieved by Email: {user.email} (Expected: user1@example.com)")
    #     self.assertEqual(user, self.user1, "❌ Failed to retrieve user by email.")

    #     # ❌ Case 1b: Retrieve user by email (Failure)
    #     user = User.objects.db_manager("users_db").by_email("nonexistent@example.com").first()
    #     print(f"❌ No User Retrieved by Email (Expected: None)")
    #     self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent email.")

    #     # ✅ Case 2: Retrieve user by username (Success)
    #     user = User.objects.db_manager("users_db").by_username("userone").first()
    #     print(f"✅ Retrieved by Username: {user.username} (Expected: userone)")
    #     self.assertEqual(user, self.user1, "❌ Failed to retrieve user by username.")

    #     # ❌ Case 2b: Retrieve user by username (Failure)
    #     user = User.objects.db_manager("users_db").by_username("fakeuser").first()
    #     print(f"❌ No User Retrieved by Username (Expected: None)")
    #     self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent username.")

    #     # ✅ Case 3: Retrieve user by badge barcode (Success)
    #     self.user3.badge_barcode = "123456"
    #     self.user3.save(using="users_db")
    #     user = User.objects.db_manager("users_db").by_badge_barcode("123456").first()
    #     print(f"✅ Retrieved by Badge Barcode: {user.badge_barcode} (Expected: 123456)")
    #     self.assertEqual(user, self.user3, "❌ Failed to retrieve user by badge barcode.")

    #     # ❌ Case 3b: Retrieve user by badge barcode (Failure)
    #     user = User.objects.db_manager("users_db").by_badge_barcode("999999").first()
    #     print(f"❌ No User Retrieved by Badge Barcode (Expected: None)")
    #     self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent barcode.")

    #     # ✅ Case 4: Retrieve user by badge RFID (Success)
    #     self.user4.badge_rfid = "ABCDEF"
    #     self.user4.save(using="users_db")
    #     user = User.objects.db_manager("users_db").by_badge_rfid("ABCDEF").first()
    #     print(f"✅ Retrieved by Badge RFID: {user.badge_rfid} (Expected: ABCDEF)")
    #     self.assertEqual(user, self.user4, "❌ Failed to retrieve user by badge RFID.")

    #     # ❌ Case 4b: Retrieve user by badge RFID (Failure)
    #     user = User.objects.db_manager("users_db").by_badge_rfid("ZZZZZZ").first()
    #     print(f"❌ No User Retrieved by Badge RFID (Expected: None)")
    #     self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent RFID.")

    #     # ✅ Case 5: Retrieve user by first name (Success)
    #     user = User.objects.db_manager("users_db").by_first_name("alice").first()
    #     print(f"✅ Retrieved by First Name: {user.first_name} (Expected: Alice)")
    #     self.assertEqual(user, self.user1, "❌ Failed to retrieve user by first name.")

    #     # ❌ Case 5b: Retrieve user by first name (Failure)
    #     user = User.objects.db_manager("users_db").by_first_name("noname").first()
    #     print(f"❌ No User Retrieved by First Name (Expected: None)")
    #     self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent first name.")

    #     # ✅ Case 6: Retrieve user by last name (Success)
    #     user = User.objects.db_manager("users_db").by_last_name("smith").first()
    #     print(f"✅ Retrieved by Last Name: {user.last_name} (Expected: Smith)")
    #     self.assertEqual(user, self.user1, "❌ Failed to retrieve user by last name.")

    #     # ❌ Case 6b: Retrieve user by last name (Failure)
    #     user = User.objects.db_manager("users_db").by_last_name("nomatch").first()
    #     print(f"❌ No User Retrieved by Last Name (Expected: None)")
    #     self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent last name.")

    #     # ✅ Case 7: Retrieve user by full name (Success)
    #     user = User.objects.db_manager("users_db").by_full_name("alice", "smith").first()
    #     print(f"✅ Retrieved by Full Name: {user.first_name} {user.last_name} (Expected: Alice Smith)")
    #     self.assertEqual(user, self.user1, "❌ Failed to retrieve user by full name.")

    #     # ❌ Case 7b: Retrieve user by full name (Failure)
    #     user = User.objects.db_manager("users_db").by_full_name("John", "Doe").first()
    #     print(f"❌ No User Retrieved by Full Name (Expected: None)")
    #     self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent full name.")

    #     print("--- END DEBUG ---\n")

    # """
    # Tests UserManager query methods that filter users by status.

    # Purpose:
    #     - Ensures that users can be retrieved based on their active/inactive status.
    #     - Confirms that staff users can be correctly identified.
    #     - Ensures queries exclude non-matching users.
    #     - Verifies that queries return the correct number of users, not just an empty result.

    # Verification Steps:
    #     1. **Retrieve Active Users**:
    #         - Ensures `active()` returns only users marked as active.
    #         - Ensures `active()` returns the correct count of active users.
    #         - Ensures `active()` excludes inactive users.
    #     2. **Retrieve Inactive Users**:
    #         - Ensures `inactive()` returns only users marked as inactive.
    #         - Ensures `inactive()` returns the correct count of inactive users.
    #         - Ensures `inactive()` excludes active users.
    #     3. **Retrieve Staff Users**:
    #         - Ensures `staff()` returns only users marked as staff.
    #         - Ensures `staff()` returns the correct count of staff users.
    #         - Ensures `staff()` excludes non-staff users.

    # Guarantees that filtering by status correctly identifies users based on their active and staff attributes.
    # """

    # def test_user_manager_filter_by_status(self):

    #     print("\n--- DEBUG: Running test_user_manager_filter_by_status ---")

    #     # ✅ Case 1: Retrieve active users (Success)
    #     active_users = User.objects.db_manager("users_db").active()
    #     print(f"✅ Active Users Count: {active_users.count()} (Expected: 3)")
    #     self.assertIn(self.user1, active_users, "❌ Active users query should include user1.")
    #     self.assertIn(self.user3, active_users, "❌ Active users query should include user3.")
    #     self.assertIn(self.user4, active_users, "❌ Active users query should include user4.")

    #     # ✅ Case 1b: Retrieve active users (Failure - some users still active)
    #     self.user1.is_active = False  # Make inactive
    #     self.user2.is_active = True  # Keep active
    #     self.user3.is_active = False  # Make inactive
    #     self.user4.is_active = False  # Make inactive

    #     self.user1.save(using="users_db")
    #     self.user2.save(using="users_db")
    #     self.user3.save(using="users_db")
    #     self.user4.save(using="users_db")

    #     active_users = User.objects.db_manager("users_db").active()
    #     print(f"✅ Active Users Count: {active_users.count()} (Expected: 1)")
    #     self.assertEqual(active_users.count(), 1, "❌ Active query should return only user2 as active.")
    #     self.assertIn(self.user2, active_users, "❌ Active users query should include user2.")

    #     # ✅ Case 2: Retrieve inactive users (Success)
    #     self.user1.is_active = True  # Make active
    #     self.user2.is_active = False  # Ensure user2 is inactive
    #     self.user3.is_active = True  # Make active
    #     self.user4.is_active = True  # Make active

    #     self.user1.save(using="users_db")
    #     self.user2.save(using="users_db")
    #     self.user3.save(using="users_db")
    #     self.user4.save(using="users_db")

    #     inactive_users = User.objects.db_manager("users_db").inactive()
    #     print(f"✅ Inactive Users Count: {inactive_users.count()} (Expected: 1)")
    #     self.assertEqual(inactive_users.count(), 1, "❌ Inactive query should return only user2 as inactive.")
    #     self.assertIn(self.user2, inactive_users, "❌ Inactive users query should include user2.")

    #     # ✅ Case 2b: Retrieve inactive users (Failure - some users still inactive)
    #     self.user1.is_active = True  # Make active
    #     self.user2.is_active = True  # Make active (was inactive)
    #     self.user3.is_active = False  # Ensure at least one inactive user remains
    #     self.user4.is_active = True  # Make active

    #     self.user1.save(using="users_db")
    #     self.user2.save(using="users_db")
    #     self.user3.save(using="users_db")
    #     self.user4.save(using="users_db")

    #     inactive_users = User.objects.db_manager("users_db").inactive()
    #     print(f"✅ Inactive Users Count: {inactive_users.count()} (Expected: 1)")
    #     self.assertEqual(inactive_users.count(), 1, "❌ Inactive query should return only user3 as inactive.")
    #     self.assertIn(self.user3, inactive_users, "❌ Inactive users query should include user3.")

    #     # ✅ Case 3: Retrieve staff users (Success)
    #     staff_users = User.objects.db_manager("users_db").staff()
    #     print(f"✅ Staff Users Count: {staff_users.count()} (Expected: 1)")
    #     self.assertIn(self.user3, staff_users, "❌ Staff query should include user3.")

    #     # ✅ Case 3b: Retrieve staff users (Failure - some users still staff)
    #     self.user1.is_staff = True  # Make staff
    #     self.user3.is_staff = False  # Remove staff status

    #     self.user1.save(using="users_db")
    #     self.user3.save(using="users_db")

    #     staff_users = User.objects.db_manager("users_db").staff()
    #     print(f"✅ Staff Users Count: {staff_users.count()} (Expected: 1)")
    #     self.assertEqual(staff_users.count(), 1, "❌ Staff query should return only user1 as staff.")
    #     self.assertIn(self.user1, staff_users, "❌ Staff users query should include user1.")


    #     print("--- END DEBUG ---\n")

    # """
    # Tests UserManager query methods that filter users based on relationships (foreign keys).

    # Purpose:
    #     - Ensures that users can be retrieved based on their assigned site or organization.
    #     - Confirms that filtering works correctly for active, inactive, and staff users at specific sites and organizations.
    #     - Verifies that queries return the correct count of users, not just an empty result.

    # Verification Steps:
    #     1. **Retrieve Users by Site**:
    #         - Ensures `from_site()` returns only users assigned to a specific site.
    #         - Ensures `from_site()` excludes users from other sites.
    #     2. **Retrieve Users by Organization**:
    #         - Ensures `from_organization()` returns only users assigned to a specific organization.
    #         - Ensures `from_organization()` excludes users from other organizations.
    #     3. **Retrieve Active Users by Site**:
    #         - Ensures `active_from_site()` returns only active users assigned to a site.
    #         - Ensures `active_from_site()` excludes inactive users.
    #         - Ensures `active_from_site()` returns the correct number of active users.
    #     4. **Retrieve Inactive Users by Site**:
    #         - Ensures `inactive_from_site()` returns only inactive users assigned to a site.
    #         - Ensures `inactive_from_site()` excludes active users.
    #     5. **Retrieve Active Users by Organization**:
    #         - Ensures `active_from_organization()` returns only active users assigned to an organization.
    #         - Ensures `active_from_organization()` excludes inactive users.
    #     6. **Retrieve Inactive Users by Organization**:
    #         - Ensures `inactive_from_organization()` returns only inactive users assigned to an organization.
    #         - Ensures `inactive_from_organization()` excludes active users.
    #     7. **Retrieve Staff Users by Site**:
    #         - Ensures `staff_from_site()` returns only staff users assigned to a site.
    #         - Ensures `staff_from_site()` excludes non-staff users.
    #     8. **Retrieve Staff Users by Organization**:
    #         - Ensures `staff_from_organization()` returns only staff users assigned to an organization.
    #         - Ensures `staff_from_organization()` excludes non-staff users.

    # Guarantees that relationship-based filtering correctly identifies users based on their assigned site and organization.
    # """

    # def test_user_manager_filter_by_relationships(self):

    #     print("\n--- DEBUG: Running test_user_manager_filter_by_relationships ---")

    #     # ✅ Case 1: Retrieve users from a specific site (Success)
    #     users_from_site1 = User.objects.db_manager("users_db").from_site(self.site1.id)
    #     print(f"✅ Users from Site 1 Count: {users_from_site1.count()} (Expected: 2)")
    #     self.assertEqual(users_from_site1.count(), 2, "❌ Users from site query should return exactly 2 users.")
    #     self.assertIn(self.user1, users_from_site1, "❌ Users from site query should include user1.")
    #     self.assertIn(self.user2, users_from_site1, "❌ Users from site query should include user2.")

    #     # ✅ Case 2: Retrieve users from a specific organization (Success)
    #     users_from_org1 = User.objects.db_manager("users_db").from_organization(self.organization1.id)
    #     print(f"✅ Users from Organization 1 Count: {users_from_org1.count()} (Expected: 2)")
    #     self.assertEqual(users_from_org1.count(), 2, "❌ Users from organization query should return exactly 2 users.")
    #     self.assertIn(self.user1, users_from_org1, "❌ Users from organization query should include user1.")
    #     self.assertIn(self.user2, users_from_org1, "❌ Users from organization query should include user2.")

    #     # ✅ Case 3: Retrieve active users from a specific site
    #     active_users_from_site1 = User.objects.db_manager("users_db").active_from_site(self.site1.id)
    #     print(f"✅ Active Users from Site 1 Count: {active_users_from_site1.count()} (Expected: 1)")
    #     self.assertEqual(active_users_from_site1.count(), 1, "❌ Active users from site query should return exactly 1 user.")
    #     self.assertIn(self.user1, active_users_from_site1, "❌ Active users from site query should include user1.")

    #     # ✅ Case 4: Retrieve inactive users from a specific organization
    #     inactive_users_from_org1 = User.objects.db_manager("users_db").inactive_from_organization(self.organization1.id)
    #     print(f"✅ Inactive Users from Organization 1 Count: {inactive_users_from_org1.count()} (Expected: 1)")
    #     self.assertEqual(inactive_users_from_org1.count(), 1, "❌ Inactive users from organization query should return exactly 1 user.")
    #     self.assertIn(self.user2, inactive_users_from_org1, "❌ Inactive users from organization query should include user2.")

    #     # ✅ Case 5: Retrieve staff users from a specific site
    #     staff_users_from_site2 = User.objects.db_manager("users_db").staff_from_site(self.site2.id)
    #     print(f"✅ Staff Users from Site 2 Count: {staff_users_from_site2.count()} (Expected: 1)")
    #     self.assertEqual(staff_users_from_site2.count(), 1, "❌ Staff users from site query should return exactly 1 user.")
    #     self.assertIn(self.user3, staff_users_from_site2, "❌ Staff users from site query should include user3.")

    #     # ✅ Case 6: Retrieve staff users from a specific organization
    #     staff_users_from_org2 = User.objects.db_manager("users_db").staff_from_organization(self.organization2.id)
    #     print(f"✅ Staff Users from Organization 2 Count: {staff_users_from_org2.count()} (Expected: 1)")
    #     self.assertEqual(staff_users_from_org2.count(), 1, "❌ Staff users from organization query should return exactly 1 user.")
    #     self.assertIn(self.user3, staff_users_from_org2, "❌ Staff users from organization query should include user3.")

    #     print("--- END DEBUG ---\n")

    # """
    # Tests UserManager query methods that filter users based on their MFA preferences.

    # Purpose:
    #     - Ensures that users can be retrieved based on their selected MFA preference.
    #     - Matches expected results to predefined test data from `setUp()`.
    #     - Verifies that queries return the correct count of users, not just an empty result.

    # Verification Steps:
    #     1. **Retrieve Users Without MFA**:
    #         - Ensures `without_mfa()` returns only users with MFA set to 'none'.
    #         - Ensures `without_mfa()` excludes users with any MFA enabled.
    #     2. **Retrieve Users Using Google Authenticator MFA**:
    #         - Ensures `with_google_authenticator()` returns only users with Google Authenticator enabled.
    #         - Ensures `with_google_authenticator()` excludes users with other MFA methods.
    #     3. **Retrieve Users Using SMS MFA**:
    #         - Ensures `with_sms()` returns only users with SMS MFA enabled.
    #         - Ensures `with_sms()` excludes users with other MFA methods.
    #     4. **Retrieve Users Using Email MFA**:
    #         - Ensures `with_email_mfa()` returns only users with Email MFA enabled.
    #         - Ensures `with_email_mfa()` excludes users with other MFA methods.
    #     5. **Ensure Non-Existent MFA Types Return No Results**:
    #         - Confirms that searching for an MFA type not present in `setUp()` returns an empty QuerySet.

    # Guarantees that MFA-based filtering correctly identifies users based on their selected MFA preference.
    # """


    # def test_user_manager_filter_by_mfa_preferences(self):

    #     print("\n--- DEBUG: Running test_user_manager_filter_by_mfa_preferences ---")

    #     # ✅ Case 1: Retrieve users without MFA (Success)
    #     users_without_mfa = User.objects.db_manager("users_db").without_mfa()
    #     print(f"✅ Users Without MFA Count: {users_without_mfa.count()} (Expected: 1)")
    #     self.assertEqual(users_without_mfa.count(), 1, "❌ Users without MFA query should return exactly 1 user.")
    #     self.assertIn(self.user1, users_without_mfa, "❌ Users without MFA query should include user1.")

    #     # ✅ Case 2: Retrieve users using Google Authenticator MFA (Success)
    #     users_with_google_authenticator = User.objects.db_manager("users_db").with_google_authenticator()
    #     print(f"✅ Users with Google Authenticator Count: {users_with_google_authenticator.count()} (Expected: 1)")
    #     self.assertEqual(users_with_google_authenticator.count(), 1, "❌ Users with Google Authenticator query should return exactly 1 user.")
    #     self.assertIn(self.user2, users_with_google_authenticator, "❌ Users with Google Authenticator query should include user2.")

    #     # ✅ Case 3: Retrieve users using SMS MFA (Success)
    #     users_with_sms = User.objects.db_manager("users_db").with_sms()
    #     print(f"✅ Users with SMS MFA Count: {users_with_sms.count()} (Expected: 1)")
    #     self.assertEqual(users_with_sms.count(), 1, "❌ Users with SMS MFA query should return exactly 1 user.")
    #     self.assertIn(self.user3, users_with_sms, "❌ Users with SMS MFA query should include user3.")

    #     # ✅ Case 4: Retrieve users using Email MFA (Success)
    #     users_with_email_mfa = User.objects.db_manager("users_db").with_email_mfa()
    #     print(f"✅ Users with Email MFA Count: {users_with_email_mfa.count()} (Expected: 1)")
    #     self.assertEqual(users_with_email_mfa.count(), 1, "❌ Users with Email MFA query should return exactly 1 user.")
    #     self.assertIn(self.user4, users_with_email_mfa, "❌ Users with Email MFA query should include user4.")

    #     # ❌ Case 5: Ensure no users are returned for an MFA type that doesn't exist in setUp()
    #     users_with_facial_recognition = User.objects.db_manager("users_db").filter(mfa_preference="facial_recognition")
    #     print(f"❌ No Users with Facial Recognition MFA Found (Expected: 0)")
    #     self.assertEqual(users_with_facial_recognition.count(), 0, "❌ Users with Facial Recognition query should return no results.")

    #     print("--- END DEBUG ---\n")

    # """
    # Tests UserManager query methods that filter users based on creation and modification data.

    # Purpose:
    #     - Ensures that users can be retrieved based on who created or modified them.
    #     - Confirms that filtering works correctly for users created within a specific time frame.
    #     - Verifies that queries return the correct count of users, not just an empty result.

    # Verification Steps:
    #     1. **Retrieve Users Created by a Specific User**:
    #         - Ensures `created_by()` returns only users created by the given user.
    #         - Ensures `created_by()` excludes users created by others.
    #     2. **Retrieve Users Modified by a Specific User**:
    #         - Ensures `modified_by()` returns only users modified by the given user.
    #         - Ensures `modified_by()` excludes users modified by others.
    #     3. **Retrieve Users Recently Joined**:
    #         - Ensures `recently_joined()` returns only users created within the last X days.
    #         - Ensures `recently_joined()` excludes users older than X days.
    #     4. **Retrieve Users Recently Joined from a Specific Site**:
    #         - Ensures `recently_joined_from_site()` returns only users from a given site within the last X days.
    #         - Ensures `recently_joined_from_site()` excludes users outside of X days or the wrong site.
    #     5. **Retrieve Users Recently Joined from a Specific Organization**:
    #         - Ensures `recently_joined_from_organization()` returns only users from a given organization within the last X days.
    #         - Ensures `recently_joined_from_organization()` excludes users outside of X days or the wrong organization.

    # Guarantees that filtering by creation and modification data correctly identifies users based on relationships and timestamps.
    # """

    # def test_user_manager_filter_by_creation_and_modification(self):

    #     print("\n--- DEBUG: Running test_user_manager_filter_by_creation_and_modification ---")

    #     # ✅ Case 1: Retrieve users created by a specific user (Success)
    #     users_created_by_user1 = User.objects.db_manager("users_db").created_by(self.user1.id)
    #     print(f"✅ Users Created by User1 Count: {users_created_by_user1.count()} (Expected: 1)")
    #     self.assertEqual(users_created_by_user1.count(), 1, "❌ Created by query should return exactly 1 user.")
    #     self.assertIn(self.user4, users_created_by_user1, "❌ Created by query should include user4.")

    #     # ❌ Case 1b: Retrieve users created by a user with no created users (Failure)
    #     users_created_by_user3 = User.objects.db_manager("users_db").created_by(self.user3.id)
    #     print(f"❌ No Users Created by User3 Found (Expected: 0)")
    #     self.assertEqual(users_created_by_user3.count(), 0, "❌ Created by query should return no results when the user has not created any users.")

    #     # ✅ Case 2: Retrieve users modified by a specific user (Success)
    #     users_modified_by_user1 = User.objects.db_manager("users_db").modified_by(self.user1.id)
    #     print(f"✅ Users Modified by User1 Count: {users_modified_by_user1.count()} (Expected: 2)")
    #     self.assertEqual(users_modified_by_user1.count(), 2, "❌ Modified by query should return exactly 2 users.")
    #     self.assertIn(self.user2, users_modified_by_user1, "❌ Modified by query should include user2.")
    #     self.assertIn(self.user3, users_modified_by_user1, "❌ Modified by query should include user3.")

    #     # ✅ Case 3: Retrieve recently joined users (Success)
    #     recently_joined_users = User.objects.db_manager("users_db").recently_joined(days=30)
    #     print(f"✅ Recently Joined Users Count: {recently_joined_users.count()} (Expected: 3)")
    #     self.assertEqual(recently_joined_users.count(), 3, "❌ Recently joined query should return exactly 3 users.")
    #     self.assertIn(self.user1, recently_joined_users, "❌ Recently joined query should include user1.")
    #     self.assertIn(self.user3, recently_joined_users, "❌ Recently joined query should include user3.")
    #     self.assertIn(self.user4, recently_joined_users, "❌ Recently joined query should include user4.")

    #     # ❌ Case 3b: Retrieve recently joined users with a short time frame (Failure)
    #     short_term_recently_joined = User.objects.db_manager("users_db").recently_joined(days=2)
    #     print(f"✅ Recently Joined Users in Last 2 Days Count: {short_term_recently_joined.count()} (Expected: 1)")
    #     self.assertEqual(short_term_recently_joined.count(), 1, "❌ Recently joined query should return exactly 1 user.")
    #     self.assertIn(self.user4, short_term_recently_joined, "❌ Recently joined query should include user4.")

    #     # ✅ Case 4: Retrieve recently joined users from a specific site (Success)
    #     recently_joined_from_site1 = User.objects.db_manager("users_db").recently_joined_from_site(self.site1.id, days=30)
    #     print(f"✅ Recently Joined from Site 1 Count: {recently_joined_from_site1.count()} (Expected: 1)")
    #     self.assertEqual(recently_joined_from_site1.count(), 1, "❌ Recently joined from site query should return exactly 1 user.")
    #     self.assertIn(self.user1, recently_joined_from_site1, "❌ Recently joined from site query should include user1.")

    #     # ✅ Case 5: Retrieve recently joined users from a specific organization (Success)
    #     recently_joined_from_org2 = User.objects.db_manager("users_db").recently_joined_from_organization(self.organization2.id, days=30)
    #     print(f"✅ Recently Joined from Organization 2 Count: {recently_joined_from_org2.count()} (Expected: 2)")
    #     self.assertEqual(recently_joined_from_org2.count(), 2, "❌ Recently joined from organization query should return exactly 2 users.")
    #     self.assertIn(self.user3, recently_joined_from_org2, "❌ Recently joined from organization query should include user3.")
    #     self.assertIn(self.user4, recently_joined_from_org2, "❌ Recently joined from organization query should include user4.")


    #     print("--- END DEBUG ---\n")








