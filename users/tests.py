from django.test import TestCase
from users.models import User
from organizations.models import Organization
from sites.models import Site
from django.utils.timezone import now
from datetime import timedelta
import time
import string
"""
    Standardized use of emojis in test output for quick visual identification in the terminal.

    Purpose:
        - Provides **consistent visual markers** in VSCode and other test runners.
        - Helps **differentiate** between running tests, passing tests, expected failures, and actual failures.
        - Improves **debugging efficiency** by clearly indicating test behavior.

    Emoji Usage:
        1. **⏳ (Hourglass) - Running a Test Step**
            - Used **before executing an important query or operation**.
            - Example:
              print("⏳ Checking active users count...")

        2. **✅ (Green Check) - Test Passed**
            - Used **when a test case successfully meets expectations**.
            - Example:
              print(f"✅ Active Users Count: {active_users.count()} (Expected: 3)")

        3. **❌ (Red X) - Test Failed**
            - Used **when an assertion fails and the test does not return the expected result**.
            - Example:
              self.assertEqual(users.count(), 2, "❌ Active users count does not match expected value.")

        4. **🔴 (Red Dot) - Expected Failure Case**
            - Used **when we intentionally trigger a failure to validate error handling**.
            - Example:
              print("🔴 Attempting to retrieve a non-existent user (should raise an error)")

    Unicode Code for Each Emoji:
        - **⏳ Hourglass (Running a Test Step)** → `\U000023f3`
        - **✅ Green Check (Test Passed)** → `\U00002705`
        - **❌ Red X (Test Failed)** → `\U0000274C`
        - **🔴 Red Dot (Expected Failure Case)** → `\U0001F534`

    Guarantees that test outputs remain structured, readable, and easy to debug.
    """


class UserModelTests(TestCase):

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
        """Runs once before any test in this class executes."""
        super().setUpClass()
        print("\n--- DEBUG: setUpClass() executed ---")

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

        print("\n⏳ Starting setting up test data...")

        # Create test organizations
        self.organization1 = Organization.objects.using("organizations_db").create(
            name="Test Organization 1",
            type_id=1,
            active=True,
            created_by_id=None
        )

        self.organization2 = Organization.objects.using("organizations_db").create(
            name="Test Organization 2",
            type_id=2,
            active=True,
            created_by_id=None
        )

        # Create test sites
        self.site1 = Site.objects.using("sites_db").create(
            name="Test Site 1",
            organization_id=self.organization1.id,
            site_type="Office",
            address="123 Test St",
            active=True,
            created_by_id=None
        )

        self.site2 = Site.objects.using("sites_db").create(
            name="Test Site 2",
            organization_id=self.organization2.id,
            site_type="Warehouse",
            address="456 Another St",
            active=True,
            created_by_id=None
        )

        # Create multiple test users with different attributes
        self.user1 = User.objects.using("users_db").create(
            email="user1@example.com",
            username="userone",
            password="SecurePass123!",
            first_name="Alice",
            last_name="Smith",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            is_active=True,
            is_staff=False,
            mfa_preference="none",
            created_by_id=None,
            modified_by_id=None,
            date_joined=now() - timedelta(days=5)
        )

        self.user2 = User.objects.using("users_db").create(
            email="user2@example.com",
            username="usertwo",
            password="SecurePass123!",
            first_name="Bob",
            last_name="Johnson",
            organization_id=self.organization1.id,
            site_id=self.site1.id,
            is_active=False,  # Inactive user
            is_staff=False,
            mfa_preference="google_authenticator",
            created_by_id=None,
            modified_by_id=self.user1.id,
            date_joined=now() - timedelta(days=40)
        )

        self.user3 = User.objects.using("users_db").create(
            email="user3@example.com",
            username="userthree",
            password="SecurePass123!",
            first_name="Charlie",
            last_name="Brown",
            organization_id=self.organization2.id,
            site_id=self.site2.id,
            is_active=True,
            is_staff=True,  # Staff user
            mfa_preference="sms",
            created_by_id=None,
            modified_by_id=self.user1.id,
            date_joined=now() - timedelta(days=15)
        )

        self.user4 = User.objects.using("users_db").create(
            email="user4@example.com",
            username="userfour",
            password="SecurePass123!",
            first_name="Dana",
            last_name="White",
            organization_id=self.organization2.id,
            site_id=self.site2.id,
            is_active=True,
            is_staff=False,
            mfa_preference="email",
            created_by_id=self.user1.id,
            modified_by_id=self.user2.id,
            date_joined=now()
        )

        print("✅ Test data setup complete.")

    """
    Tests setUp() to ensure test data is correctly created and linked.

    Purpose:
        - Confirms that test data is properly inserted into the correct databases.
        - Ensures that organizations, sites, and users are linked correctly.
        - Validates that user attributes match expected values.
        - Includes a negative test case to confirm that non-existent data returns `None`.

    Expected Behavior:
        - The organization, site, and user should exist in their respective databases.
        - The retrieved organization and site should be correctly linked.
        - The user should have the expected attributes (email, username, organization ID, and site ID).
        - Attempting to retrieve a non-existent organization should return `None`.

    Test Cases:
        1. **Verify Organization Data** - Ensures an organization exists and can be retrieved.
        2. **Verify Site Data** - Confirms a site exists and is linked to an organization.
        3. **Verify User Data** - Ensures a user exists and is linked to both a site and an organization.
        4. **Negative Test Case** - Attempts to retrieve a non-existent organization to confirm failure handling.

    Guarantees that all test cases start with a well-structured and validated test environment.
    """

    def test_setup_data(self):

        print("\n⏳ Starting test_setup_data...")

        # Verify organization
        organization = Organization.objects.using("organizations_db").first()
        if organization:
            print(f"✅ Organization Found: {organization.id} - {organization.name}")
        else:
            print("❌ No Organization Found")

        # Verify site
        site = Site.objects.using("sites_db").first()
        if site:
            print(f"✅ Site Found: {site.id} - {site.name}, Org ID: {site.organization_id}")
        else:
            print("❌ No Site Found")

        # Verify user
        user = User.objects.using("users_db").first()
        if user:
            print(f"✅ User Found: {user.id} - {user.email}, Username: {user.username}, Org ID: {user.organization_id}, Site ID: {user.site_id}")
        else:
            print("❌ No User Found")

        # Assertions to ensure data exists
        self.assertIsNotNone(organization, "❌ Organization should exist in test DB")
        self.assertIsNotNone(site, "❌ Site should exist in test DB")
        self.assertIsNotNone(user, "❌ User should exist in test DB")

        # Failure case: Verify non-existent data does not exist
        non_existent_org = Organization.objects.using("organizations_db").filter(id=999).first()
        self.assertIsNone(non_existent_org, "❌ Organization with ID 999 should not exist.")

        print("\n✅ Verifying User Attributes...")

        print(f"User ID: {self.user1.id}")
        print(f"User Email: {self.user1.email} (Expected: user1@example.com)")
        print(f"User Username: {self.user1.username} (Expected: userone)")
        print(f"User Organization ID: {self.user1.organization_id} (Expected: {self.organization1.id})")
        print(f"User Site ID: {self.user1.site_id} (Expected: {self.site1.id})")

        # Assertions for user attributes
        self.assertEqual(self.user1.email, "user1@example.com", "❌ User email does not match expected value.")
        self.assertEqual(self.user1.username, "userone", "❌ User username does not match expected value.")
        self.assertEqual(self.user1.organization_id, self.organization1.id, "❌ User organization_id does not match expected value.")
        self.assertEqual(self.user1.site_id, self.site1.id, "❌ User site_id does not match expected value.")

        print("✅ Finished test_setup_data...\n")

    """
    Tests normalize_email() to ensure proper email formatting and error handling.

    Purpose:
        - Ensures email addresses are consistently formatted before being saved to the database.
        - Confirms that email normalization handles various cases correctly.
        - Verifies that invalid email formats raise a `ValueError`.

    Expected Behavior:
        - Converts email addresses to lowercase.
        - Strips leading and trailing whitespace.
        - Returns `None` when given a `None` input without raising an error.
        - Raises a `ValueError` when given an invalid email format.

    Test Cases:
        1. **Uppercase Letters** - Should be converted to lowercase.
        2. **Leading & Trailing Spaces** - Should be stripped.
        3. **Mixed-Case Email** - Should normalize correctly.
        4. **None Input** - Should return `None` without error.
        5. **Invalid Email Format** - Should raise a `ValueError`.

    Guarantees that email normalization functions correctly before saving user data.
    """

    def test_normalize_email(self):

        print("\n⏳ Starting test_normalize_email...")

        # Accessing UserManager
        user_manager = User.objects

        # Test normalization of different email formats
        raw_email_1 = "  USER@Example.COM  "
        raw_email_2 = "MiXEDcAsE@DOMAIN.CoM"
        raw_email_3 = " leadingspace@example.com"
        raw_email_4 = "trailingspace@example.com  "
        raw_email_5 = None  # Should return None

        expected_email_1 = "user@example.com"
        expected_email_2 = "mixedcase@domain.com"
        expected_email_3 = "leadingspace@example.com"
        expected_email_4 = "trailingspace@example.com"
        expected_email_5 = None  # Should remain None

        # Perform normalization
        normalized_email_1 = user_manager.normalize_email(raw_email_1)
        normalized_email_2 = user_manager.normalize_email(raw_email_2)
        normalized_email_3 = user_manager.normalize_email(raw_email_3)
        normalized_email_4 = user_manager.normalize_email(raw_email_4)
        normalized_email_5 = user_manager.normalize_email(raw_email_5)

        # Debug Output
        print(f"✅ Input: '{raw_email_1}' | Normalized: '{normalized_email_1}' | Expected: '{expected_email_1}'")
        print(f"✅ Input: '{raw_email_2}' | Normalized: '{normalized_email_2}' | Expected: '{expected_email_2}'")
        print(f"✅ Input: '{raw_email_3}' | Normalized: '{normalized_email_3}' | Expected: '{expected_email_3}'")
        print(f"✅ Input: '{raw_email_4}' | Normalized: '{normalized_email_4}' | Expected: '{expected_email_4}'")
        print(f"✅ Input: {raw_email_5} | Normalized: {normalized_email_5} | Expected: {expected_email_5}")

        # Assertions
        self.assertEqual(normalized_email_1, expected_email_1, "❌ Email normalization failed.")
        self.assertEqual(normalized_email_2, expected_email_2, "❌ Mixed-case email normalization failed.")
        self.assertEqual(normalized_email_3, expected_email_3, "❌ Leading space email normalization failed.")
        self.assertEqual(normalized_email_4, expected_email_4, "❌ Trailing space email normalization failed.")
        self.assertIsNone(normalized_email_5, "❌ None email should return None.")

        # Failure Case: Invalid Email Formatting Should Not Normalize Incorrectly
        raw_email_fail = "INVALID EMAIL@EXAMPLE.COM"

        print(f"🔴 Attempting to normalize an invalid email: '{raw_email_fail}' (should raise ValueError)")
        with self.assertRaises(ValueError, msg="❌ normalize_email() should raise ValueError for an invalid email format."):
            user_manager.normalize_email(raw_email_fail)

        print("✅ Finished test_normalize_email...\n")


    """
    Tests generate_secure_password() to ensure strong password generation.

    Purpose:
        - Confirms that generated passwords meet security and complexity requirements.
        - Ensures that passwords contain required character types.
        - Validates that passwords are unique and not predictable.
        - Ensures the function raises an error when attempting to generate a password below the minimum length.

    Expected Behavior:
        - Generates passwords with a minimum length of 16 characters.
        - Each password contains at least one uppercase letter, one lowercase letter, one digit, and one special character.
        - Passwords are randomly generated and not identical across multiple generations.
        - Raises a `ValueError` if a password shorter than 16 characters is requested.

    Test Cases:
        1. **Default password length (16)** - Ensures a 16-character password is correctly generated with required character types.
        2. **Custom password length (20)** - Confirms that a password of a custom length meets security standards.
        3. **Password character validation** - Ensures that generated passwords contain at least one uppercase, lowercase, digit, and special character.
        4. **Password uniqueness test** - Checks that multiple password generations are not identical.
        5. **Attempting to generate a password with length <16** - Should raise a `ValueError`.

    Guarantees that password generation meets security standards and prevents weak or predictable passwords.
    """
    
    def test_generate_secure_password(self):

        print("\n⏳ Starting test_generate_secure_password...")
        
        # Accessing UserManager
        user_manager = User.objects

        # Test Case 1: Default password length (16)
        password_16 = user_manager.generate_secure_password()
        print(f"✅ Generated Password (16 chars): {password_16}")

        # Validate length and character requirements
        self.assertEqual(len(password_16), 16, "❌ Default password length should be 16.")
        self.assertTrue(any(c.isupper() for c in password_16), "❌ Password must contain at least one uppercase letter.")
        self.assertTrue(any(c.islower() for c in password_16), "❌ Password must contain at least one lowercase letter.")
        self.assertTrue(any(c.isdigit() for c in password_16), "❌ Password must contain at least one digit.")
        self.assertTrue(any(c in string.punctuation for c in password_16), "❌ Password must contain at least one special character.")

        # Test Case 2: Custom password length (20)
        password_20 = user_manager.generate_secure_password(length=20)
        print(f"✅ Generated Password (20 chars): {password_20}")

        self.assertEqual(len(password_20), 20, "❌ Custom password length should be 20.")
        self.assertTrue(any(c.isupper() for c in password_20), "❌ Custom password must contain at least one uppercase letter.")
        self.assertTrue(any(c.islower() for c in password_20), "❌ Custom password must contain at least one lowercase letter.")
        self.assertTrue(any(c.isdigit() for c in password_20), "❌ Custom password must contain at least one digit.")
        self.assertTrue(any(c in string.punctuation for c in password_20), "❌ Custom password must contain at least one special character.")

        # Test Case 3: Ensure generated passwords contain all required character types
        for _ in range(10):  # Run multiple times to check consistency
            password = user_manager.generate_secure_password()
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in string.punctuation for c in password)

            print(f"✅ Generated Password: {password} | Upper: {has_upper}, Lower: {has_lower}, Digit: {has_digit}, Special: {has_special}")

            self.assertTrue(has_upper, "❌ Password missing an uppercase letter.")
            self.assertTrue(has_lower, "❌ Password missing a lowercase letter.")
            self.assertTrue(has_digit, "❌ Password missing a digit.")
            self.assertTrue(has_special, "❌ Password missing a special character.")

        # Test Case 4: Ensure generated passwords are not identical
        password_set = {user_manager.generate_secure_password() for _ in range(10)}
        print(f"✅ Unique Passwords Generated: {len(password_set)} (Expected: >1)")
        self.assertGreater(len(password_set), 1, "❌ Generated passwords should not be identical.")

        # Test Case 5: Attempt to generate a password below 16 characters (should raise ValueError)
        with self.assertRaises(ValueError, msg="❌ Password length below 16 should raise a ValueError."):
            print("🔴 Attempting to generate a password of length 12 (should raise an error)")
            user_manager.generate_secure_password(length=12)

        print("✅ Finished test_generate_secure_password...\n")

    """
    Tests get_organization() and get_site() to ensure correct manual foreign key retrieval.

    Purpose:
        - Validates that a user's organization and site can be correctly retrieved 
          using manual foreign key lookup methods (`get_organization()` and `get_site()`).
        - Confirms that retrieved objects match expected IDs as set in `setUp()`.
        - Ensures that users with an assigned organization/site retrieve the correct objects.

    Expected Behavior:
        - `get_organization()` should return the correct `Organization` instance for the user.
        - `get_site()` should return the correct `Site` instance for the user.
        - Users with an assigned organization/site should retrieve the expected objects.
        - Users without an assigned organization/site (if applicable) should return `None`.

    Test Cases:
        1. **Retrieve Organization for User1** - Should return the expected organization.
        2. **Retrieve Site for User1** - Should return the expected site.
        3. **Retrieve Organization for User2** - Should return the expected organization.
        4. **Retrieve Site for User2** - Should return the expected site.
        5. **User with no assigned organization/site (if applicable)** - Should return `None`.

    Guarantees that manual foreign key lookup methods function correctly in a multi-database environment.
    """

    def test_user_manual_fk_methods(self):  
    
        print("\n⏳ Starting test_user_manual_fk_methods...")

        # Test Case 1: Retrieve organization using manual FK method
        retrieved_org = self.user1.get_organization()
        print(f"✅ User1's Retrieved Organization: {retrieved_org.id if retrieved_org else 'None'} (Expected: {self.organization1.id})")

        # Test Case 2: Retrieve site using manual FK method
        retrieved_site = self.user1.get_site()
        print(f"✅ User1's Retrieved Site: {retrieved_site.id if retrieved_site else 'None'} (Expected: {self.site1.id})")

        # Test Case 3: Assertions to verify correct retrieval
        self.assertIsNotNone(retrieved_org, "❌ Failed: User1's organization should not be None.")
        self.assertEqual(retrieved_org.id, self.organization1.id, "❌ Failed: Retrieved organization ID does not match expected ID.")

        self.assertIsNotNone(retrieved_site, "❌ Failed: User1's site should not be None.")
        self.assertEqual(retrieved_site.id, self.site1.id, "❌ Failed: Retrieved site ID does not match expected ID.")

        # Test Case 4: User without an organization/site should return None
        retrieved_org_none = self.user2.get_organization()
        retrieved_site_none = self.user2.get_site()

        print(f"✅ User2's Retrieved Organization: {retrieved_org_none.id if retrieved_org_none else 'None'} (Expected: {self.organization1.id})")
        print(f"✅ User2's Retrieved Site: {retrieved_site_none.id if retrieved_site_none else 'None'} (Expected: {self.site1.id})")

        # Test Case 5: Fix the assertion to expect an actual object instead of None
        self.assertIsNotNone(retrieved_org_none, "❌ User2 should return an organization.")
        self.assertEqual(retrieved_org_none.id, self.organization1.id, "❌ User2's organization ID does not match expected.")

        self.assertIsNotNone(retrieved_site_none, "❌ User2 should return a site.")
        self.assertEqual(retrieved_site_none.id, self.site1.id, "❌ User2's site ID does not match expected.")

        print("✅ Finished test_user_manual_fk_methods...\n")

    """
    Tests the create_user() method in UserManager to ensure correct user creation.

    Purpose:
        - Ensures that users are created successfully with all required fields.
        - Validates that passwords are securely generated and hashed.
        - Confirms that email normalization occurs before saving.
        - Enforces constraints on required fields.

    Verification Steps:
        1. **Create a User with Valid Data**:
            - Generates a unique email with extra spaces and uppercase letters.
            - Calls `create_user()` through `UserManager`.
        2. **Validate User Attributes**:
            - Ensures that email is properly normalized (lowercased & trimmed).
            - Checks that a secure, hashed password is set.
        3. **Edge Cases**:
            - Creating a user without an email should raise a `ValueError`.
            - Creating a user without any login identifier (username, badge) should raise a `ValueError`.

    Guarantees that `create_user()` correctly handles required fields, email formatting, 
    password security, and error handling.
    """


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

        print("--- END DEBUG ---\n")

    """
    Tests the update_user() method in UserManager to ensure correct user updates.

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

    def test_user_manager_update_user(self):
        print("\n--- DEBUG: Running test_user_manager_update_user ---")

        # Case 1: Successfully update username
        user = User.objects.db_manager("users_db").get(id=self.user1.id)
        print(f"🔹 Before Update: Username: {user.username}")

        user.username = "updateduser"
        user.save(using="users_db")

        # Fetch the updated user
        updated_user = User.objects.db_manager("users_db").get(id=self.user1.id)

        print(f"✅ After Update: Username: {updated_user.username} (Expected: updateduser)")
        self.assertEqual(updated_user.username, "updateduser", "❌ Username did not update correctly.")

        # Case 2: Ensure email normalization
        raw_email = "  UPDATEDUSER@EXAMPLE.COM  "  # Untrimmed & uppercase
        expected_email = raw_email.strip().lower()  # Expected normalized email

        User.objects.db_manager("users_db").update_user(self.user1.id, email=raw_email)

        updated_user = User.objects.db_manager("users_db").get(id=self.user1.id)
        print(f"✅ After Email Update: {updated_user.email} (Expected: {expected_email})")
        self.assertEqual(updated_user.email, expected_email, "❌ Email was not normalized correctly.")

        # Case 3: Update foreign key fields and verify
        new_organization = Organization.objects.using("organizations_db").create(
            name="New Organization",
            type_id=2,
            active=True,
            created_by_id=None
        )

        new_site = Site.objects.using("sites_db").create(
            name="New Site",
            organization_id=new_organization.id,
            site_type="Warehouse",
            address="456 New St",
            active=True,
            created_by_id=None
        )

        User.objects.db_manager("users_db").update_user(
            self.user1.id,
            organization_id=new_organization.id,
            site_id=new_site.id,
            modified_by_id=self.user1.id,
        )

        updated_user = User.objects.db_manager("users_db").get(id=self.user1.id)
        print(f"✅ After FK Update: Org ID: {updated_user.organization_id}, Site ID: {updated_user.site_id}")

        self.assertEqual(updated_user.organization_id, new_organization.id, "❌ Organization ID did not update correctly.")
        self.assertEqual(updated_user.site_id, new_site.id, "❌ Site ID did not update correctly.")

        # Case 4: Attempt to remove all login identifiers (should raise ValueError)
        with self.assertRaises(ValueError):
            print("🔴 Attempting to remove all login identifiers (should raise an error)")
            User.objects.db_manager("users_db").update_user(
                self.user1.id,
                username=None,
                badge_barcode=None,
                badge_rfid=None,
            )

        # Case 5: Attempt to update a non-existent user (should raise ValueError)
        with self.assertRaises(ValueError):
            print("🔴 Attempting to update a non-existent user (should raise an error)")
            User.objects.db_manager("users_db").update_user(user_id=999999, username="ghostuser")

        print("--- END DEBUG ---\n")

    """
    Tests the delete_user() method in UserManager to ensure correct user deletion.

    Purpose:
        - Confirms that a user can be deleted successfully.
        - Ensures that the delete_user() method explicitly prevents deletion of superusers.
        - Ensures proper error handling when deleting non-existent users.

    Verification Steps:
        1. **Delete a Regular User**:
            - Calls `delete_user()` and confirms the user is removed.
        2. **Confirm Superuser Deletion is Blocked**:
            - Attempts to delete a superuser, which is hardcoded in `delete_user()` to raise a `ValueError`.
            - This restriction ensures that superusers can only be deleted using `delete_superuser()`.
        3. **Handle Non-Existent User Deletion**:
            - Tries to delete a user that does not exist and verifies that a `ValueError` is raised.

    Guarantees that `delete_user()` enforces proper constraints and handles errors correctly.
    """

    def test_user_manager_delete_user(self):
        print("\n--- DEBUG: Running test_user_manager_delete_user ---")

        # Case 1: Successfully delete a regular user
        user = User.objects.db_manager("users_db").get(id=self.user1.id)
        print(f"🔹 Before Deletion: User Found - ID: {user.id}, Email: {user.email}")

        User.objects.db_manager("users_db").delete_user(self.user1.id)

        # Confirm user is deleted
        print("⏳ Checking if user still exists after deletion...")
        with self.assertRaises(User.DoesNotExist):
            deleted_user = User.objects.db_manager("users_db").get(id=self.user1.id)
            print(f"❌ User still exists: {deleted_user.id}")  # Should NOT execute

        print("✅ User successfully deleted (DoesNotExist Exception raised).")

        # Case 2: Attempt to delete a superuser (should raise ValueError)
        superuser = User.objects.db_manager("users_db").create_user(
            email="superuser@example.com",
            username="superadmin",
            password="SecurePass123!",
            is_superuser=True
        )

        print(f"🔹 Created Superuser: ID {superuser.id}, Email: {superuser.email}")

        with self.assertRaises(ValueError):
            print("🔴 Attempting to delete a superuser (should raise an error)")
            User.objects.db_manager("users_db").delete_user(superuser.id)

        # Case 3: Attempt to delete a non-existent user (should raise ValueError)
        with self.assertRaises(ValueError):
            print("🔴 Attempting to delete a non-existent user (should raise an error)")
            User.objects.db_manager("users_db").delete_user(user_id=999999)

        print("--- END DEBUG ---\n")

    """
    Tests the create_superuser() method in UserManager to ensure proper superuser creation.

    Expected Behavior:
        - Superusers should always have `is_staff=True` and `is_superuser=True`.
        - If `is_staff` or `is_superuser` are set to False, an error should be raised.
        - Calls `create_user()` and ensures superuser constraints are applied.

    Test Cases:
        1. Successfully create a superuser and verify attributes.
        2. Attempt to create a superuser with `is_superuser=False` (should raise `ValueError`).
        3. Attempt to create a superuser with `is_staff=False` (should raise `ValueError`).
    """
    def test_user_manager_create_superuser(self):
    

        print("\n--- DEBUG: Running test_user_manager_create_superuser ---")

        # Case 1: Successfully create a superuser
        superuser = User.objects.db_manager("users_db").create_superuser(
            email="admin@example.com",
            username="adminuser",
            password="SecurePass123!"
        )

        print(f"✅ Created Superuser ID: {superuser.id}")
        print(f"User Email: {superuser.email} (Expected: admin@example.com)")
        print(f"User Username: {superuser.username} (Expected: adminuser)")
        print(f"User is_staff: {superuser.is_staff} (Expected: True)")
        print(f"User is_superuser: {superuser.is_superuser} (Expected: True)")

        # Assertions
        self.assertEqual(superuser.email, "admin@example.com", "❌ Email does not match expected value.")
        self.assertEqual(superuser.username, "adminuser", "❌ Username does not match expected value.")
        self.assertTrue(superuser.is_staff, "❌ Superuser should have is_staff=True.")
        self.assertTrue(superuser.is_superuser, "❌ Superuser should have is_superuser=True.")

        # Case 2: Attempt to create a superuser with is_superuser=False (should raise ValueError)
        with self.assertRaises(ValueError):
            print("🔴 Attempting to create a superuser with is_superuser=False (should raise an error)")
            User.objects.db_manager("users_db").create_superuser(
                email="invalid_admin@example.com",
                username="invalidadmin",
                password="SecurePass123!",
                is_superuser=False
            )

        # Case 3: Attempt to create a superuser with is_staff=False (should raise ValueError)
        with self.assertRaises(ValueError):
            print("🔴 Attempting to create a superuser with is_staff=False (should raise an error)")
            User.objects.db_manager("users_db").create_superuser(
                email="invalid_staff@example.com",
                username="invalidstaff",
                password="SecurePass123!",
                is_staff=False
            )

        print("--- END DEBUG ---\n")

    """
    Tests the update_superuser() method in UserManager to ensure superuser updates function correctly.

    Expected Behavior:
        - Allows updating superuser attributes while enforcing required constraints.
        - Ensures `is_staff` and `is_superuser` remain `True`.
        - Normalizes email before saving.
        - Ensures at least one login identifier remains set.
        - Raises errors for invalid update attempts.

    Test Cases:
        1. Successfully update a superuser's attributes.
        2. Ensure email normalization when updating email.
        3. Update foreign key fields (`organization_id`, `site_id`, `modified_by_id`) and confirm persistence.
        4. Attempt to remove all login identifiers (should raise `ValueError`).
        5. Attempt to update a non-superuser (should raise `ValueError`).
        6. Attempt to update a non-existent superuser (should raise `ValueError`).
    """
    def test_user_manager_update_superuser(self):
    
        print("\n--- DEBUG: Running test_user_manager_update_superuser ---")

        # Case 1: Successfully update superuser attributes
        superuser = User.objects.db_manager("users_db").create_superuser(
            email="superadmin@example.com",
            username="superadmin",
            password="SecurePass123!"
        )

        print(f"🔹 Before Update: Username: {superuser.username}")

        updated_superuser = User.objects.db_manager("users_db").update_superuser(
            superuser.id, username="updatedsuperadmin"
        )

        print(f"✅ After Update: Username: {updated_superuser.username} (Expected: updatedsuperadmin)")
        self.assertEqual(updated_superuser.username, "updatedsuperadmin", "❌ Username did not update correctly.")

        # Case 2: Ensure email normalization when updating email
        raw_email = "  UPDATEDSUPER@EXAMPLE.COM  "
        expected_email = raw_email.strip().lower()

        updated_superuser = User.objects.db_manager("users_db").update_superuser(
            superuser.id, email=raw_email
        )

        print(f"✅ After Email Update: {updated_superuser.email} (Expected: {expected_email})")
        self.assertEqual(updated_superuser.email, expected_email, "❌ Email was not normalized correctly.")

        # Case 3: Update foreign key fields and verify
        new_organization = Organization.objects.using("organizations_db").create(
            name="New Super Organization",
            type_id=2,
            active=True,
            created_by_id=None
        )

        new_site = Site.objects.using("sites_db").create(
            name="New Super Site",
            organization_id=new_organization.id,
            site_type="Datacenter",
            address="789 Super St",
            active=True,
            created_by_id=None
        )

        updated_superuser = User.objects.db_manager("users_db").update_superuser(
            superuser.id,
            organization_id=new_organization.id,
            site_id=new_site.id,
            modified_by_id=superuser.id
        )

        print(f"✅ After FK Update: Org ID: {updated_superuser.organization_id}, Site ID: {updated_superuser.site_id}")

        self.assertEqual(updated_superuser.organization_id, new_organization.id, "❌ Organization ID did not update correctly.")
        self.assertEqual(updated_superuser.site_id, new_site.id, "❌ Site ID did not update correctly.")

        # Case 4: Attempt to remove all login identifiers (should raise ValueError)
        with self.assertRaises(ValueError):
            print("🔴 Attempting to remove all login identifiers (should raise an error)")
            User.objects.db_manager("users_db").update_superuser(
                superuser.id,
                username=None,
                badge_barcode=None,
                badge_rfid=None
            )

        # Case 5: Attempt to update a non-superuser (should raise ValueError)
        regular_user = User.objects.db_manager("users_db").create_user(
            email="regular@example.com",
            username="regularuser",
            password="SecurePass123!"
        )

        with self.assertRaises(ValueError):
            print("🔴 Attempting to update a non-superuser (should raise an error)")
            User.objects.db_manager("users_db").update_superuser(regular_user.id, username="shouldfail")

        # Case 6: Attempt to update a non-existent superuser (should raise ValueError)
        with self.assertRaises(ValueError):
            print("🔴 Attempting to update a non-existent superuser (should raise an error)")
            User.objects.db_manager("users_db").update_superuser(user_id=999999, username="ghostsuper")

        print("--- END DEBUG ---\n")

    """
    Tests the delete_superuser() method in UserManager to ensure proper superuser deletion.

    Expected Behavior:
        - Successfully deletes a superuser when multiple superusers exist.
        - Prevents deletion of the last remaining superuser.
        - Raises an error if attempting to delete a non-existent superuser.

    Test Cases:
        1. Successfully delete a superuser when more than one exists.
        2. Attempt to delete the last remaining superuser (should raise `ValueError`).
        3. Attempt to delete a non-existent superuser (should raise `ValueError`).
    """

    def test_user_manager_delete_superuser(self):
    

        print("\n--- DEBUG: Running test_user_manager_delete_superuser ---")

        # Case 1: Successfully delete a superuser when multiple exist
        superuser1 = User.objects.db_manager("users_db").create_superuser(
            email="admin1@example.com",
            username="admin1",
            password="SecurePass123!"
        )

        superuser2 = User.objects.db_manager("users_db").create_superuser(
            email="admin2@example.com",
            username="admin2",
            password="SecurePass123!"
        )

        print(f"🔹 Created Superusers: {superuser1.id} (admin1), {superuser2.id} (admin2)")

        # Delete one superuser
        User.objects.db_manager("users_db").delete_superuser(superuser1.id)

        # Verify deletion
        with self.assertRaises(User.DoesNotExist):
            print("⏳ Checking if superuser1 still exists after deletion...")
            User.objects.db_manager("users_db").get(id=superuser1.id)

        print("✅ Superuser1 successfully deleted.")

        # Case 2: Attempt to delete the last remaining superuser (should raise ValueError)
        with self.assertRaises(ValueError):
            print("🔴 Attempting to delete the last remaining superuser (should raise an error)")
            User.objects.db_manager("users_db").delete_superuser(superuser2.id)

        # Case 3: Attempt to delete a non-existent superuser (should raise ValueError)
        with self.assertRaises(ValueError):
            print("🔴 Attempting to delete a non-existent superuser (should raise an error)")
            User.objects.db_manager("users_db").delete_superuser(user_id=999999)

        print("--- END DEBUG ---\n")

    """
    Tests the get_by_natural_key() method in UserManager to ensure correct user retrieval.

    Expected Behavior:
        - Successfully retrieves an active user by email, username, badge barcode, or badge RFID.
        - Ensures that only active users are retrieved.
        - Raises a `User.DoesNotExist` error if no matching active user is found.

    Test Cases:
        1. Retrieve a user by email.
        2. Retrieve a user by username.
        3. Retrieve a user by badge barcode.
        4. Retrieve a user by badge RFID.
        5. Attempt to retrieve an inactive user (should raise `User.DoesNotExist`).
        6. Attempt to retrieve a non-existent user (should raise `User.DoesNotExist`).
    """

    def test_user_manager_get_by_natural_key(self):
    

        print("\n--- DEBUG: Running test_user_manager_get_by_natural_key ---")

        # Create a user with multiple identifiers
        user = User.objects.db_manager("users_db").create_user(
            email="searchuser@example.com",
            username="searchuser",
            password="SecurePass123!",
            badge_barcode="123456",
            badge_rfid="ABCDEF",
            is_active=True
        )

        print(f"🔹 Created User ID: {user.id}, Email: {user.email}, Username: {user.username}")

        # Case 1: Retrieve user by email
        retrieved_user = User.objects.db_manager("users_db").get_by_natural_key("searchuser@example.com")
        print(f"✅ Retrieved by Email: {retrieved_user.email} (Expected: {user.email})")
        self.assertEqual(retrieved_user.id, user.id, "❌ Failed to retrieve user by email.")

        # Case 2: Retrieve user by username
        retrieved_user = User.objects.db_manager("users_db").get_by_natural_key("searchuser")
        print(f"✅ Retrieved by Username: {retrieved_user.username} (Expected: {user.username})")
        self.assertEqual(retrieved_user.id, user.id, "❌ Failed to retrieve user by username.")

        # Case 3: Retrieve user by badge barcode
        retrieved_user = User.objects.db_manager("users_db").get_by_natural_key("123456")
        print(f"✅ Retrieved by Badge Barcode: {retrieved_user.badge_barcode} (Expected: {user.badge_barcode})")
        self.assertEqual(retrieved_user.id, user.id, "❌ Failed to retrieve user by badge barcode.")

        # Case 4: Retrieve user by badge RFID
        retrieved_user = User.objects.db_manager("users_db").get_by_natural_key("ABCDEF")
        print(f"✅ Retrieved by Badge RFID: {retrieved_user.badge_rfid} (Expected: {user.badge_rfid})")
        self.assertEqual(retrieved_user.id, user.id, "❌ Failed to retrieve user by badge RFID.")

        # Case 5: Attempt to retrieve an inactive user (should raise User.DoesNotExist)
        inactive_user = User.objects.db_manager("users_db").create_user(
            email="inactiveuser@example.com",
            username="inactiveuser",
            password="SecurePass123!",
            is_active=False
        )

        with self.assertRaises(User.DoesNotExist):
            print("🔴 Attempting to retrieve an inactive user (should raise an error)")
            User.objects.db_manager("users_db").get_by_natural_key("inactiveuser@example.com")

        # Case 6: Attempt to retrieve a non-existent user (should raise User.DoesNotExist)
        with self.assertRaises(User.DoesNotExist):
            print("🔴 Attempting to retrieve a non-existent user (should raise an error)")
            User.objects.db_manager("users_db").get_by_natural_key("doesnotexist@example.com")

        print("--- END DEBUG ---\n")

    """
    Tests UserManager query methods that filter users by specific fields.

    Purpose:
        - Ensures that users can be retrieved based on unique and searchable attributes.
        - Confirms that queries return the correct users while excluding incorrect ones.
        - Verifies that case-insensitive searches work where applicable.
        - Ensures that queries return an empty result when no matching users exist.

    Verification Steps:
        1. **Retrieve a User by Email**:
            - Ensures `by_email()` returns the correct user.
            - Ensures `by_email()` returns no results when no match exists.
        2. **Retrieve a User by Username**:
            - Ensures `by_username()` returns the correct user.
            - Ensures `by_username()` returns no results when no match exists.
        3. **Retrieve a User by Badge Barcode**:
            - Ensures `by_badge_barcode()` returns the correct user.
            - Ensures `by_badge_barcode()` returns no results when no match exists.
        4. **Retrieve a User by Badge RFID**:
            - Ensures `by_badge_rfid()` returns the correct user.
            - Ensures `by_badge_rfid()` returns no results when no match exists.
        5. **Retrieve a User by First Name**:
            - Ensures `by_first_name()` returns users with a matching first name (case-insensitive).
            - Ensures `by_first_name()` returns no results when no match exists.
        6. **Retrieve a User by Last Name**:
            - Ensures `by_last_name()` returns users with a matching last name (case-insensitive).
            - Ensures `by_last_name()` returns no results when no match exists.
        7. **Retrieve a User by Full Name**:
            - Ensures `by_full_name()` returns users with a matching first and last name (case-insensitive).
            - Ensures `by_full_name()` returns no results when no match exists.

    Guarantees that filtering by specific fields works as expected and excludes non-matching users.
    """

    def test_user_manager_filter_by_specific_fields(self):

        print("\n--- DEBUG: Running test_user_manager_filter_by_specific_fields ---")

        # ✅ Case 1: Retrieve user by email (Success)
        user = User.objects.db_manager("users_db").by_email("user1@example.com").first()
        print(f"✅ Retrieved by Email: {user.email} (Expected: user1@example.com)")
        self.assertEqual(user, self.user1, "❌ Failed to retrieve user by email.")

        # ❌ Case 1b: Retrieve user by email (Failure)
        user = User.objects.db_manager("users_db").by_email("nonexistent@example.com").first()
        print(f"❌ No User Retrieved by Email (Expected: None)")
        self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent email.")

        # ✅ Case 2: Retrieve user by username (Success)
        user = User.objects.db_manager("users_db").by_username("userone").first()
        print(f"✅ Retrieved by Username: {user.username} (Expected: userone)")
        self.assertEqual(user, self.user1, "❌ Failed to retrieve user by username.")

        # ❌ Case 2b: Retrieve user by username (Failure)
        user = User.objects.db_manager("users_db").by_username("fakeuser").first()
        print(f"❌ No User Retrieved by Username (Expected: None)")
        self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent username.")

        # ✅ Case 3: Retrieve user by badge barcode (Success)
        self.user3.badge_barcode = "123456"
        self.user3.save(using="users_db")
        user = User.objects.db_manager("users_db").by_badge_barcode("123456").first()
        print(f"✅ Retrieved by Badge Barcode: {user.badge_barcode} (Expected: 123456)")
        self.assertEqual(user, self.user3, "❌ Failed to retrieve user by badge barcode.")

        # ❌ Case 3b: Retrieve user by badge barcode (Failure)
        user = User.objects.db_manager("users_db").by_badge_barcode("999999").first()
        print(f"❌ No User Retrieved by Badge Barcode (Expected: None)")
        self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent barcode.")

        # ✅ Case 4: Retrieve user by badge RFID (Success)
        self.user4.badge_rfid = "ABCDEF"
        self.user4.save(using="users_db")
        user = User.objects.db_manager("users_db").by_badge_rfid("ABCDEF").first()
        print(f"✅ Retrieved by Badge RFID: {user.badge_rfid} (Expected: ABCDEF)")
        self.assertEqual(user, self.user4, "❌ Failed to retrieve user by badge RFID.")

        # ❌ Case 4b: Retrieve user by badge RFID (Failure)
        user = User.objects.db_manager("users_db").by_badge_rfid("ZZZZZZ").first()
        print(f"❌ No User Retrieved by Badge RFID (Expected: None)")
        self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent RFID.")

        # ✅ Case 5: Retrieve user by first name (Success)
        user = User.objects.db_manager("users_db").by_first_name("alice").first()
        print(f"✅ Retrieved by First Name: {user.first_name} (Expected: Alice)")
        self.assertEqual(user, self.user1, "❌ Failed to retrieve user by first name.")

        # ❌ Case 5b: Retrieve user by first name (Failure)
        user = User.objects.db_manager("users_db").by_first_name("noname").first()
        print(f"❌ No User Retrieved by First Name (Expected: None)")
        self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent first name.")

        # ✅ Case 6: Retrieve user by last name (Success)
        user = User.objects.db_manager("users_db").by_last_name("smith").first()
        print(f"✅ Retrieved by Last Name: {user.last_name} (Expected: Smith)")
        self.assertEqual(user, self.user1, "❌ Failed to retrieve user by last name.")

        # ❌ Case 6b: Retrieve user by last name (Failure)
        user = User.objects.db_manager("users_db").by_last_name("nomatch").first()
        print(f"❌ No User Retrieved by Last Name (Expected: None)")
        self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent last name.")

        # ✅ Case 7: Retrieve user by full name (Success)
        user = User.objects.db_manager("users_db").by_full_name("alice", "smith").first()
        print(f"✅ Retrieved by Full Name: {user.first_name} {user.last_name} (Expected: Alice Smith)")
        self.assertEqual(user, self.user1, "❌ Failed to retrieve user by full name.")

        # ❌ Case 7b: Retrieve user by full name (Failure)
        user = User.objects.db_manager("users_db").by_full_name("John", "Doe").first()
        print(f"❌ No User Retrieved by Full Name (Expected: None)")
        self.assertIsNone(user, "❌ Unexpected user found when searching for nonexistent full name.")

        print("--- END DEBUG ---\n")

    """
    Tests UserManager query methods that filter users by status.

    Purpose:
        - Ensures that users can be retrieved based on their active/inactive status.
        - Confirms that staff users can be correctly identified.
        - Ensures queries exclude non-matching users.
        - Verifies that queries return the correct number of users, not just an empty result.

    Verification Steps:
        1. **Retrieve Active Users**:
            - Ensures `active()` returns only users marked as active.
            - Ensures `active()` returns the correct count of active users.
            - Ensures `active()` excludes inactive users.
        2. **Retrieve Inactive Users**:
            - Ensures `inactive()` returns only users marked as inactive.
            - Ensures `inactive()` returns the correct count of inactive users.
            - Ensures `inactive()` excludes active users.
        3. **Retrieve Staff Users**:
            - Ensures `staff()` returns only users marked as staff.
            - Ensures `staff()` returns the correct count of staff users.
            - Ensures `staff()` excludes non-staff users.

    Guarantees that filtering by status correctly identifies users based on their active and staff attributes.
    """

    def test_user_manager_filter_by_status(self):

        print("\n--- DEBUG: Running test_user_manager_filter_by_status ---")

        # ✅ Case 1: Retrieve active users (Success)
        active_users = User.objects.db_manager("users_db").active()
        print(f"✅ Active Users Count: {active_users.count()} (Expected: 3)")
        self.assertIn(self.user1, active_users, "❌ Active users query should include user1.")
        self.assertIn(self.user3, active_users, "❌ Active users query should include user3.")
        self.assertIn(self.user4, active_users, "❌ Active users query should include user4.")

        # ✅ Case 1b: Retrieve active users (Failure - some users still active)
        self.user1.is_active = False  # Make inactive
        self.user2.is_active = True  # Keep active
        self.user3.is_active = False  # Make inactive
        self.user4.is_active = False  # Make inactive

        self.user1.save(using="users_db")
        self.user2.save(using="users_db")
        self.user3.save(using="users_db")
        self.user4.save(using="users_db")

        active_users = User.objects.db_manager("users_db").active()
        print(f"✅ Active Users Count: {active_users.count()} (Expected: 1)")
        self.assertEqual(active_users.count(), 1, "❌ Active query should return only user2 as active.")
        self.assertIn(self.user2, active_users, "❌ Active users query should include user2.")

        # ✅ Case 2: Retrieve inactive users (Success)
        self.user1.is_active = True  # Make active
        self.user2.is_active = False  # Ensure user2 is inactive
        self.user3.is_active = True  # Make active
        self.user4.is_active = True  # Make active

        self.user1.save(using="users_db")
        self.user2.save(using="users_db")
        self.user3.save(using="users_db")
        self.user4.save(using="users_db")

        inactive_users = User.objects.db_manager("users_db").inactive()
        print(f"✅ Inactive Users Count: {inactive_users.count()} (Expected: 1)")
        self.assertEqual(inactive_users.count(), 1, "❌ Inactive query should return only user2 as inactive.")
        self.assertIn(self.user2, inactive_users, "❌ Inactive users query should include user2.")

        # ✅ Case 2b: Retrieve inactive users (Failure - some users still inactive)
        self.user1.is_active = True  # Make active
        self.user2.is_active = True  # Make active (was inactive)
        self.user3.is_active = False  # Ensure at least one inactive user remains
        self.user4.is_active = True  # Make active

        self.user1.save(using="users_db")
        self.user2.save(using="users_db")
        self.user3.save(using="users_db")
        self.user4.save(using="users_db")

        inactive_users = User.objects.db_manager("users_db").inactive()
        print(f"✅ Inactive Users Count: {inactive_users.count()} (Expected: 1)")
        self.assertEqual(inactive_users.count(), 1, "❌ Inactive query should return only user3 as inactive.")
        self.assertIn(self.user3, inactive_users, "❌ Inactive users query should include user3.")

        # ✅ Case 3: Retrieve staff users (Success)
        staff_users = User.objects.db_manager("users_db").staff()
        print(f"✅ Staff Users Count: {staff_users.count()} (Expected: 1)")
        self.assertIn(self.user3, staff_users, "❌ Staff query should include user3.")

        # ✅ Case 3b: Retrieve staff users (Failure - some users still staff)
        self.user1.is_staff = True  # Make staff
        self.user3.is_staff = False  # Remove staff status

        self.user1.save(using="users_db")
        self.user3.save(using="users_db")

        staff_users = User.objects.db_manager("users_db").staff()
        print(f"✅ Staff Users Count: {staff_users.count()} (Expected: 1)")
        self.assertEqual(staff_users.count(), 1, "❌ Staff query should return only user1 as staff.")
        self.assertIn(self.user1, staff_users, "❌ Staff users query should include user1.")


        print("--- END DEBUG ---\n")

    """
    Tests UserManager query methods that filter users based on relationships (foreign keys).

    Purpose:
        - Ensures that users can be retrieved based on their assigned site or organization.
        - Confirms that filtering works correctly for active, inactive, and staff users at specific sites and organizations.
        - Verifies that queries return the correct count of users, not just an empty result.

    Verification Steps:
        1. **Retrieve Users by Site**:
            - Ensures `from_site()` returns only users assigned to a specific site.
            - Ensures `from_site()` excludes users from other sites.
        2. **Retrieve Users by Organization**:
            - Ensures `from_organization()` returns only users assigned to a specific organization.
            - Ensures `from_organization()` excludes users from other organizations.
        3. **Retrieve Active Users by Site**:
            - Ensures `active_from_site()` returns only active users assigned to a site.
            - Ensures `active_from_site()` excludes inactive users.
            - Ensures `active_from_site()` returns the correct number of active users.
        4. **Retrieve Inactive Users by Site**:
            - Ensures `inactive_from_site()` returns only inactive users assigned to a site.
            - Ensures `inactive_from_site()` excludes active users.
        5. **Retrieve Active Users by Organization**:
            - Ensures `active_from_organization()` returns only active users assigned to an organization.
            - Ensures `active_from_organization()` excludes inactive users.
        6. **Retrieve Inactive Users by Organization**:
            - Ensures `inactive_from_organization()` returns only inactive users assigned to an organization.
            - Ensures `inactive_from_organization()` excludes active users.
        7. **Retrieve Staff Users by Site**:
            - Ensures `staff_from_site()` returns only staff users assigned to a site.
            - Ensures `staff_from_site()` excludes non-staff users.
        8. **Retrieve Staff Users by Organization**:
            - Ensures `staff_from_organization()` returns only staff users assigned to an organization.
            - Ensures `staff_from_organization()` excludes non-staff users.

    Guarantees that relationship-based filtering correctly identifies users based on their assigned site and organization.
    """

    def test_user_manager_filter_by_relationships(self):

        print("\n--- DEBUG: Running test_user_manager_filter_by_relationships ---")

        # ✅ Case 1: Retrieve users from a specific site (Success)
        users_from_site1 = User.objects.db_manager("users_db").from_site(self.site1.id)
        print(f"✅ Users from Site 1 Count: {users_from_site1.count()} (Expected: 2)")
        self.assertEqual(users_from_site1.count(), 2, "❌ Users from site query should return exactly 2 users.")
        self.assertIn(self.user1, users_from_site1, "❌ Users from site query should include user1.")
        self.assertIn(self.user2, users_from_site1, "❌ Users from site query should include user2.")

        # ✅ Case 2: Retrieve users from a specific organization (Success)
        users_from_org1 = User.objects.db_manager("users_db").from_organization(self.organization1.id)
        print(f"✅ Users from Organization 1 Count: {users_from_org1.count()} (Expected: 2)")
        self.assertEqual(users_from_org1.count(), 2, "❌ Users from organization query should return exactly 2 users.")
        self.assertIn(self.user1, users_from_org1, "❌ Users from organization query should include user1.")
        self.assertIn(self.user2, users_from_org1, "❌ Users from organization query should include user2.")

        # ✅ Case 3: Retrieve active users from a specific site
        active_users_from_site1 = User.objects.db_manager("users_db").active_from_site(self.site1.id)
        print(f"✅ Active Users from Site 1 Count: {active_users_from_site1.count()} (Expected: 1)")
        self.assertEqual(active_users_from_site1.count(), 1, "❌ Active users from site query should return exactly 1 user.")
        self.assertIn(self.user1, active_users_from_site1, "❌ Active users from site query should include user1.")

        # ✅ Case 4: Retrieve inactive users from a specific organization
        inactive_users_from_org1 = User.objects.db_manager("users_db").inactive_from_organization(self.organization1.id)
        print(f"✅ Inactive Users from Organization 1 Count: {inactive_users_from_org1.count()} (Expected: 1)")
        self.assertEqual(inactive_users_from_org1.count(), 1, "❌ Inactive users from organization query should return exactly 1 user.")
        self.assertIn(self.user2, inactive_users_from_org1, "❌ Inactive users from organization query should include user2.")

        # ✅ Case 5: Retrieve staff users from a specific site
        staff_users_from_site2 = User.objects.db_manager("users_db").staff_from_site(self.site2.id)
        print(f"✅ Staff Users from Site 2 Count: {staff_users_from_site2.count()} (Expected: 1)")
        self.assertEqual(staff_users_from_site2.count(), 1, "❌ Staff users from site query should return exactly 1 user.")
        self.assertIn(self.user3, staff_users_from_site2, "❌ Staff users from site query should include user3.")

        # ✅ Case 6: Retrieve staff users from a specific organization
        staff_users_from_org2 = User.objects.db_manager("users_db").staff_from_organization(self.organization2.id)
        print(f"✅ Staff Users from Organization 2 Count: {staff_users_from_org2.count()} (Expected: 1)")
        self.assertEqual(staff_users_from_org2.count(), 1, "❌ Staff users from organization query should return exactly 1 user.")
        self.assertIn(self.user3, staff_users_from_org2, "❌ Staff users from organization query should include user3.")

        print("--- END DEBUG ---\n")

    """
    Tests UserManager query methods that filter users based on their MFA preferences.

    Purpose:
        - Ensures that users can be retrieved based on their selected MFA preference.
        - Matches expected results to predefined test data from `setUp()`.
        - Verifies that queries return the correct count of users, not just an empty result.

    Verification Steps:
        1. **Retrieve Users Without MFA**:
            - Ensures `without_mfa()` returns only users with MFA set to 'none'.
            - Ensures `without_mfa()` excludes users with any MFA enabled.
        2. **Retrieve Users Using Google Authenticator MFA**:
            - Ensures `with_google_authenticator()` returns only users with Google Authenticator enabled.
            - Ensures `with_google_authenticator()` excludes users with other MFA methods.
        3. **Retrieve Users Using SMS MFA**:
            - Ensures `with_sms()` returns only users with SMS MFA enabled.
            - Ensures `with_sms()` excludes users with other MFA methods.
        4. **Retrieve Users Using Email MFA**:
            - Ensures `with_email_mfa()` returns only users with Email MFA enabled.
            - Ensures `with_email_mfa()` excludes users with other MFA methods.
        5. **Ensure Non-Existent MFA Types Return No Results**:
            - Confirms that searching for an MFA type not present in `setUp()` returns an empty QuerySet.

    Guarantees that MFA-based filtering correctly identifies users based on their selected MFA preference.
    """


    def test_user_manager_filter_by_mfa_preferences(self):

        print("\n--- DEBUG: Running test_user_manager_filter_by_mfa_preferences ---")

        # ✅ Case 1: Retrieve users without MFA (Success)
        users_without_mfa = User.objects.db_manager("users_db").without_mfa()
        print(f"✅ Users Without MFA Count: {users_without_mfa.count()} (Expected: 1)")
        self.assertEqual(users_without_mfa.count(), 1, "❌ Users without MFA query should return exactly 1 user.")
        self.assertIn(self.user1, users_without_mfa, "❌ Users without MFA query should include user1.")

        # ✅ Case 2: Retrieve users using Google Authenticator MFA (Success)
        users_with_google_authenticator = User.objects.db_manager("users_db").with_google_authenticator()
        print(f"✅ Users with Google Authenticator Count: {users_with_google_authenticator.count()} (Expected: 1)")
        self.assertEqual(users_with_google_authenticator.count(), 1, "❌ Users with Google Authenticator query should return exactly 1 user.")
        self.assertIn(self.user2, users_with_google_authenticator, "❌ Users with Google Authenticator query should include user2.")

        # ✅ Case 3: Retrieve users using SMS MFA (Success)
        users_with_sms = User.objects.db_manager("users_db").with_sms()
        print(f"✅ Users with SMS MFA Count: {users_with_sms.count()} (Expected: 1)")
        self.assertEqual(users_with_sms.count(), 1, "❌ Users with SMS MFA query should return exactly 1 user.")
        self.assertIn(self.user3, users_with_sms, "❌ Users with SMS MFA query should include user3.")

        # ✅ Case 4: Retrieve users using Email MFA (Success)
        users_with_email_mfa = User.objects.db_manager("users_db").with_email_mfa()
        print(f"✅ Users with Email MFA Count: {users_with_email_mfa.count()} (Expected: 1)")
        self.assertEqual(users_with_email_mfa.count(), 1, "❌ Users with Email MFA query should return exactly 1 user.")
        self.assertIn(self.user4, users_with_email_mfa, "❌ Users with Email MFA query should include user4.")

        # ❌ Case 5: Ensure no users are returned for an MFA type that doesn't exist in setUp()
        users_with_facial_recognition = User.objects.db_manager("users_db").filter(mfa_preference="facial_recognition")
        print(f"❌ No Users with Facial Recognition MFA Found (Expected: 0)")
        self.assertEqual(users_with_facial_recognition.count(), 0, "❌ Users with Facial Recognition query should return no results.")

        print("--- END DEBUG ---\n")

    """
    Tests UserManager query methods that filter users based on creation and modification data.

    Purpose:
        - Ensures that users can be retrieved based on who created or modified them.
        - Confirms that filtering works correctly for users created within a specific time frame.
        - Verifies that queries return the correct count of users, not just an empty result.

    Verification Steps:
        1. **Retrieve Users Created by a Specific User**:
            - Ensures `created_by()` returns only users created by the given user.
            - Ensures `created_by()` excludes users created by others.
        2. **Retrieve Users Modified by a Specific User**:
            - Ensures `modified_by()` returns only users modified by the given user.
            - Ensures `modified_by()` excludes users modified by others.
        3. **Retrieve Users Recently Joined**:
            - Ensures `recently_joined()` returns only users created within the last X days.
            - Ensures `recently_joined()` excludes users older than X days.
        4. **Retrieve Users Recently Joined from a Specific Site**:
            - Ensures `recently_joined_from_site()` returns only users from a given site within the last X days.
            - Ensures `recently_joined_from_site()` excludes users outside of X days or the wrong site.
        5. **Retrieve Users Recently Joined from a Specific Organization**:
            - Ensures `recently_joined_from_organization()` returns only users from a given organization within the last X days.
            - Ensures `recently_joined_from_organization()` excludes users outside of X days or the wrong organization.

    Guarantees that filtering by creation and modification data correctly identifies users based on relationships and timestamps.
    """

    def test_user_manager_filter_by_creation_and_modification(self):

        print("\n--- DEBUG: Running test_user_manager_filter_by_creation_and_modification ---")

        # ✅ Case 1: Retrieve users created by a specific user (Success)
        users_created_by_user1 = User.objects.db_manager("users_db").created_by(self.user1.id)
        print(f"✅ Users Created by User1 Count: {users_created_by_user1.count()} (Expected: 1)")
        self.assertEqual(users_created_by_user1.count(), 1, "❌ Created by query should return exactly 1 user.")
        self.assertIn(self.user4, users_created_by_user1, "❌ Created by query should include user4.")

        # ❌ Case 1b: Retrieve users created by a user with no created users (Failure)
        users_created_by_user3 = User.objects.db_manager("users_db").created_by(self.user3.id)
        print(f"❌ No Users Created by User3 Found (Expected: 0)")
        self.assertEqual(users_created_by_user3.count(), 0, "❌ Created by query should return no results when the user has not created any users.")

        # ✅ Case 2: Retrieve users modified by a specific user (Success)
        users_modified_by_user1 = User.objects.db_manager("users_db").modified_by(self.user1.id)
        print(f"✅ Users Modified by User1 Count: {users_modified_by_user1.count()} (Expected: 2)")
        self.assertEqual(users_modified_by_user1.count(), 2, "❌ Modified by query should return exactly 2 users.")
        self.assertIn(self.user2, users_modified_by_user1, "❌ Modified by query should include user2.")
        self.assertIn(self.user3, users_modified_by_user1, "❌ Modified by query should include user3.")

        # ✅ Case 3: Retrieve recently joined users (Success)
        recently_joined_users = User.objects.db_manager("users_db").recently_joined(days=30)
        print(f"✅ Recently Joined Users Count: {recently_joined_users.count()} (Expected: 3)")
        self.assertEqual(recently_joined_users.count(), 3, "❌ Recently joined query should return exactly 3 users.")
        self.assertIn(self.user1, recently_joined_users, "❌ Recently joined query should include user1.")
        self.assertIn(self.user3, recently_joined_users, "❌ Recently joined query should include user3.")
        self.assertIn(self.user4, recently_joined_users, "❌ Recently joined query should include user4.")

        # ❌ Case 3b: Retrieve recently joined users with a short time frame (Failure)
        short_term_recently_joined = User.objects.db_manager("users_db").recently_joined(days=2)
        print(f"✅ Recently Joined Users in Last 2 Days Count: {short_term_recently_joined.count()} (Expected: 1)")
        self.assertEqual(short_term_recently_joined.count(), 1, "❌ Recently joined query should return exactly 1 user.")
        self.assertIn(self.user4, short_term_recently_joined, "❌ Recently joined query should include user4.")

        # ✅ Case 4: Retrieve recently joined users from a specific site (Success)
        recently_joined_from_site1 = User.objects.db_manager("users_db").recently_joined_from_site(self.site1.id, days=30)
        print(f"✅ Recently Joined from Site 1 Count: {recently_joined_from_site1.count()} (Expected: 1)")
        self.assertEqual(recently_joined_from_site1.count(), 1, "❌ Recently joined from site query should return exactly 1 user.")
        self.assertIn(self.user1, recently_joined_from_site1, "❌ Recently joined from site query should include user1.")

        # ✅ Case 5: Retrieve recently joined users from a specific organization (Success)
        recently_joined_from_org2 = User.objects.db_manager("users_db").recently_joined_from_organization(self.organization2.id, days=30)
        print(f"✅ Recently Joined from Organization 2 Count: {recently_joined_from_org2.count()} (Expected: 2)")
        self.assertEqual(recently_joined_from_org2.count(), 2, "❌ Recently joined from organization query should return exactly 2 users.")
        self.assertIn(self.user3, recently_joined_from_org2, "❌ Recently joined from organization query should include user3.")
        self.assertIn(self.user4, recently_joined_from_org2, "❌ Recently joined from organization query should include user4.")


        print("--- END DEBUG ---\n")








