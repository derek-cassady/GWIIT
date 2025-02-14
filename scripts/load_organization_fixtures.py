import os
import sys
import django
import time
from django.core.management import call_command

# DEBUG: Start script execution
print(f"DEBUG: load_organization_fixtures.py execution started at {time.time()}")

# Set up Django environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GWIIT.settings")
django.setup()

from organizations.models import OrganizationType, Organization, OrganizationContact

# Define fixture files for the Organizations app
ORGANIZATION_FIXTURES = [
    ("organizations/fixtures/organization_types.json", OrganizationType),
    ("organizations/fixtures/organizations.json", Organization),
    ("organizations/fixtures/organization_contacts.json", OrganizationContact),
]

# Database assigned to the Organizations app
DATABASE_NAME = "organizations_db"

"""
    Loads fixture data into the 'organizations_db'.
    - Ensures organization-related data is available.
    - Loads fixtures in a specific order to prevent foreign key issues.
    - Skips missing fixtures and logs warnings instead of crashing.
"""
def load_organization_fixtures():
    
    # DEBUG: Start fixture loading for Organizations app
    print(f"DEBUG: Starting fixture loading for Organizations app at {time.time()}")

    for fixture, model in ORGANIZATION_FIXTURES:
        if os.path.exists(fixture):
            try:

                # DEBUG: Loading fixture: {fixture}
                print(f"DEBUG: Loading fixture: {fixture} into database: {DATABASE_NAME}")
                
                call_command("loaddata", fixture, database=DATABASE_NAME)
            
                """
                Catch any unexpected errors that occur during fixture loading.
                Prevents the script from crashing if an issue arises, such as:
                    - Database connection error
                    - Missing required fields in the fixture file
                    - Constraint violations (e.g., foreign key errors)
                    - Corrupt or malformed fixture data
                The error message is logged for debugging purposes.
                """
            except Exception as e:

                # ERROR: Failed to load
                print(f"ERROR: Failed to load {fixture}: {e}")
                
                # Unexpected error exit the script
                sys.exit(1)

            # Wait and verify that data was actually loaded
            try:
                max_retries = 3
                retries = 0
                while retries < max_retries:
                    
                    # Wait 2 seconds before checking
                    time.sleep(2)

                    try:
                        if model.objects.exists():
                            
                            # DEBUG: Successfully loaded
                            print(f"DEBUG: Successfully loaded {fixture}")
                            
                            # Exit loop if data is confirmed loaded
                            break
                        
                        """
                        Catch errors that occur while verifying if fixture data was successfully loaded.
                            Possible causes:
                                - Database query failure (e.g., database is unavailable)
                                - Model table does not exist (migration issue)
                                - Unexpected data corruption in the database
                        Logs the error for debugging and allows for further investigation.
                        """
                    except Exception as e:
                        
                        # ERROR: Exception while checking
                        print(f"ERROR: Exception while checking if {fixture} data was loaded: {e}")

                    retries += 1
                    
                    # WARNING: Fixture data not found
                    print(f"WARNING: {fixture} data not found. Retrying... ({retries}/{max_retries})")

                if not model.objects.exists():
                    
                    # ERROR: Fixture data not loaded after max attempts.
                    print(f"ERROR: {fixture} data not loaded after {max_retries} attempts. Exiting.")
                    
                    # Failed, max attempts, exit the script
                    sys.exit(1)

                """
                Catch errors that occur during the retry verification loop.
                    Possible causes:
                        - Database timeout while querying for loaded data
                        - Memory/resource exhaustion causing the check to fail
                        - Model query execution failure due to an unhandled condition
                Ensures that unexpected errors do not silently stop the fixture loading process.
                """
            except Exception as e:
                
                # ERROR: Unexpected error occurred while verifying
                print(f"ERROR: Unexpected error occurred while verifying {fixture} data: {e}")
                
                # Unexpected error exit the script
                sys.exit(1)

        else:
            
            # WARNING: Fixture not found
            print(f"WARNING: {fixture} not found. Skipping.")

    # Final verification check after all fixtures
    try:
        if all(model.objects.exists() for _, model in ORGANIZATION_FIXTURES):
            
            # DEBUG: All loaded successfully
            print(f"DEBUG: All organization fixtures loaded successfully.")
        
        else:
            
            # ERROR: Some organization fixture data is missing after loading
            print(f"ERROR: Some organization fixture data is missing after loading. Exiting.")
            
            # Fixture data is missing exit the script
            sys.exit(1)

        """
        Catch errors that occur during the final verification step after all fixtures are loaded.
            Possible causes:
                - Database inconsistency (some data loaded while others failed)
                - Schema changes that prevent expected data from being retrieved
                - Query execution failure due to database corruption
        This step ensures that fixture data is confirmed before the script exits.
        """

    except Exception as e:
        
        # ERROR: Exception during final verification
        print(f"ERROR: Exception during final verification: {e}")
        
        # Unexpected error exit the script
        sys.exit(1)

    # DEBUG: Organization fixtures loaded successfully
    print(f"DEBUG: Organization fixtures loaded successfully. Exiting script at {time.time()}")
    
    # Exit the script
    sys.exit(0)

if __name__ == "__main__":
    load_organization_fixtures()