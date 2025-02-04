from django.conf import settings
from django.core.management import call_command
import sys

def is_testing_environment():
    """
    Check if we are in a testing environment by detecting SQLite usage.
    If all databases use SQLite, return True (test mode). Otherwise, return False (production).
    """
    for db_config in settings.DATABASES.values():
        if db_config["ENGINE"] != "django.db.backends.sqlite3":
            # We are in production
            return False
    # We are in testing/demo mode    
    return True

def load_test_data():
    """
    Automatically loads test data for all apps on server startup if in testing mode.
    """
    if is_testing_environment():
        print("\n Loading test data for development environment...\n")
        
        try:
            # Call test data scripts for each app
            call_command("add_test_data_organizations")
            call_command("add_test_data_sites")
            call_command("add_test_data_users")
            
            print("\n Test data successfully loaded.\n")
        except Exception as e:
            print(f"\n Error loading test data: {e}\n")
    else:
        print("\n Running in production mode. Skipping test data.\n")

# Run this function automatically on startup
if "runserver" in sys.argv:
    load_test_data()
