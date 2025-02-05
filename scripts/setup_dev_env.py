import os
import sys
import django
from django.core.management import call_command
from django.contrib.auth import get_user_model

# set up Django environment
# allows Django commands from this script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GWIIT.settings")
django.setup()

def run_migrations():
    """
    Runs Django migrations. If no migrations exist, it creates them first.
    """
    print("Applying database migrations...")
    # generate migrations if needed
    call_command("makemigrations")
    # apply migrations
    call_command("migrate")
    print("Migrations complete.")

def create_superuser():
    """
    Creates a Django superuser if one does not already exist.
    This ensures a valid user exists for `created_by` references in dummy data.
    """
    call_command("migrate", database="users_db")

    User = get_user_model()
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating a superuser for development...")

        # Auto-generate a secure password
        password = "Admin@12345!"

        # Create the superuser with required fields
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            # Optional; superuser can log in via email
            username="admin",  # optional; superuser can log in via email
            password=password # hardcoded for testing and demo
        )

        print("Superuser created successfully.")

    else:
        print("Superuser already exists. Skipping creation.")

def load_dummy_data():
    
    """
    Loads dummy data from multiple fixture files into their respective databases.
    This ensures each app's data is stored correctly in its assigned database.
    """
    
    print("Loading dummy data...")
    
    # map to add dummy data from fixture files
    # must be loaded in order
    fixture_files = {
        "organizations_db": [
            "organizations/fixtures/organization_types.json",
            "organizations/fixtures/organizations.json",
            "organizations/fixtures/organization_contacts.json",
        ],
        "sites_db": [
            "sites/fixtures/sites.json",
            "sites/fixtures/site_contacts.json",
        ],
        "users_db": [
            "users/fixtures/users.json",
        ]
    }

    # load each set of fixtures into specified database
    for db_name, files in fixture_files.items():
        for fixture in files:
            if os.path.exists(fixture):
                print(f"Loading fixture: {fixture} into database: {db_name}")
                call_command("loaddata", fixture, database=db_name)
            else:
                print(f"Warning: {fixture} not found, skipping.")

    print("Dummy data loaded.")

def start_server():
    """
    Starts the Django development server automatically.
    """
    print("Starting the Django development server...")
    os.system("python manage.py runserver")

if __name__ == "__main__":
    print("Setting up the development environment...")
    
    # run migrations
    run_migrations()
    
    # ensure superuser exists
    create_superuser()
    
    # load dummy data
    load_dummy_data()

    # start Django server
    start_server()

    print("Development environment is ready!")
