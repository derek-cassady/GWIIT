import os
import sys
import django
import time
from django.contrib.auth import get_user_model

# DEBUG: Start script execution
print(f"DEBUG: create_superuser.py execution started at {time.time()}")

# Set up Django environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GWIIT.settings")
django.setup()

# Get the User model
User = get_user_model()


"""
    Ensures a Django superuser exists.
    - Only runs once per server start.
    - Exits cleanly if a superuser already exists.
    - Uses predefined credentials for development (change in production).
    """
def create_superuser():

    # DEBUG: Checking if superuser exists
    print(f"DEBUG: Checking if superuser exists at {time.time()}")

    # Check if a superuser already exists
    if User.objects.filter(is_superuser=True).exists():
        print("Superuser already exists. Skipping creation.")
        
        # DEBUG: Superuser already exists, exit script
        print(f"DEBUG: Superuser already exists. Skipping creation. Exiting script at {time.time()}")

        # Exit the script
        sys.exit(0)

    print("Creating a superuser for development...")

    # Define credentials (change in production)
    email = "admin@example.com"
    username = "admin"
    
    # Must meet password validators
    password = "Admin@12345!"

    try:
        # Create the superuser
        superuser = User.objects.create_superuser(
            email=email,
            username=username,
            password=password
        )

        # Confirm creation before exiting
        if User.objects.filter(is_superuser=True).exists():
            print(f"Superuser created successfully: {superuser.email}")
        
            # DEBUG: Successful creation script
            print(f"DEBUG: Superuser created successfully")
    
    
            # DEBUG: Successful exit script
            print(f"DEBUG: Superuser created successfully. Exiting script at {time.time()}")
    
            # Exit the script
            sys.exit(0)
    
        """
        Catch any unexpected errors that occur during superuser creation.
        Prevents the script from crashing if an issue arises:
            database connection error,
            missing required fields, 
            constraints not met, 
            etc.
        The error message is logged for debugging purposes.
        """
    
    except Exception as e:
        print(f"ERROR: Exception during superuser creation: {e}")
    
    # If the superuser was not found after creation attempt, log error
    print(f"ERROR: Superuser creation failed. Exiting script at {time.time()}")
    
    # Exit with error code 1 if creation failed
    sys.exit(1)

if __name__ == "__main__":
    create_superuser()