import os
import subprocess
import sys
import django
from django.core.management import call_command
from django.contrib.auth import get_user_model
import time

print(f"DEBUG: setup_dev_env.py execution started at {time.time()}")
"""
Setup DJango environment for script
    - ensures Django commands,can be executed from script. 
        - even though it's outside "manage.py".
"""

# allows Django commands from this script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set the default Django settings module for the script
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GWIIT.settings")

# Initialize Django
django.setup()

"""
Applies all database migrations.
    - `reset_dev_env.py` deletes all migration files, regenerates them on startup.
        - Calls 'makemigrations' to recreate migration files.
    - Ensures that all database schema changes are applied before using the app.
        - Calls 'migrate' to apply all migrations to the database.
    - Prevents errors caused by missing tables or outdated models.

    - If the migrations were not deleted during reset, 
        'makemigrations' wouldn not be needed.
    - In a production environment, migrations are created once and committed to Git.    
"""

def run_migrations():

    print(f"DEBUG: Entering run_migrations() at {time.time()} (PID: {os.getpid()})")  # Entry log

    print("Applying database migrations...")
    print(f"DEBUG: setup_dev_env.py migration process started at {time.time()} (PID: {os.getpid()})")
    
    # generate migrations if needed
    print(f"DEBUG: Checking if migrations are needed at {time.time()} (PID: {os.getpid()})")
    if not subprocess.run(["python", "manage.py", "makemigrations", "--dry-run"], capture_output=True).stdout:
        print(f"DEBUG: No changes detected, skipping makemigrations. (PID: {os.getpid()})")
    else:
        print(f"DEBUG: Running makemigrations at {time.time()} (PID: {os.getpid()})")
        call_command("makemigrations", "users", verbosity=2)
        call_command("makemigrations", "organizations", verbosity=2)
        call_command("makemigrations", "sites", verbosity=2)
    
    print(f"DEBUG: Checking for unapplied migrations at {time.time()} (PID: {os.getpid()})")  
    result = subprocess.run(["python", "manage.py", "showmigrations", "--unapplied"], capture_output=True, text=True)

    if result.stdout.strip():  # If there are unapplied migrations, run migrate
        print(f"DEBUG: Running 'migrate' at {time.time()} (PID: {os.getpid()})")  
        call_command("migrate", verbosity=2)

        print(f"DEBUG: Migrations complete at {time.time()} (PID: {os.getpid()})")
    else:
        print(f"DEBUG: No unapplied migrations found, skipping migration process. (PID: {os.getpid()})")
    
    print(f"DEBUG: Exiting run_migrations() at {time.time()} (PID: {os.getpid()})")

"""
Main execution flow for setting up the development environment.
- Apply database migrations.
- Ensure a superuser exists.
- Load dummy data into the database.
- Start the Django server.
"""

if __name__ == "__main__":
    print("Setting up the development environment...")
    
    # run db migrations
    run_migrations()
    
    print("Development environment is ready!")
    
    # Indicate setup is complete by creating a lock file
    SETUP_COMPLETE_FILE = "setup_complete.lock"
    with open(SETUP_COMPLETE_FILE, "w") as f:
        f.write("Setup completed successfully.")

    print("DEBUG: Setup process is complete. Lock file created.")

# Ensure the script exits cleanly
sys.exit(0)