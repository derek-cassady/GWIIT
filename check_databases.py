import os
import django
from django.conf import settings
from django.db import connections

# Initialize Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GWIIT.settings")
django.setup()

def check_databases():
    """
    Verifies that all configured databases exist and contain the required tables.
    
    - Connects to each database in `settings.DATABASES`.
    - Lists all tables present in each database.
    - Compares against expected tables for each app.
    - Prints missing tables, if any.
    """

    # Define expected tables per app (modify this as needed for your project)
    expected_tables = {
        "default": {"django_migrations", "auth_user", "auth_group", "django_content_type"},
        "users_db": {"users_user"},
        "organizations_db": {"organizations_organization"},
        "sites_db": {"sites_site"},
    }

    for alias in settings.DATABASES:
        try:
            connection = connections[alias]
            with connection.cursor() as cursor:
                # Retrieve all tables in the database
                tables = connection.introspection.table_names()

                print(f"Database: {alias}")
                print(f"Found {len(tables)} tables.")

                # Compare with expected tables
                expected = expected_tables.get(alias, set())
                missing_tables = expected - set(tables)

                if missing_tables:
                    print(f"Missing tables: {', '.join(missing_tables)}")
                else:
                    print("All expected tables are present.")

                print("-" * 50)

        except Exception as e:
            print(f"ERROR: Could not check database '{alias}': {e}")

if __name__ == "__main__":
    check_databases()

"""
Epected output:

Database: default
Found 7 tables.
Missing tables: auth_user
--------------------------------------------------
Database: authentication_db
Found 1 tables.
All expected tables are present.
--------------------------------------------------
Database: authorization_db
Found 1 tables.
All expected tables are present.
--------------------------------------------------
Database: organizations_db
Found 10 tables.
All expected tables are present.
--------------------------------------------------
Database: sites_db
Found 9 tables.
All expected tables are present.
--------------------------------------------------
Database: users_db
Found 8 tables.
All expected tables are present.
--------------------------------------------------

"""