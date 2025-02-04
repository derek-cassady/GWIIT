#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
# ability register a shutdown hook
import atexit
# ability to run scripts
import subprocess

# define path to setup and cleanup scripts
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")
SETUP_SCRIPT = os.path.join(SCRIPTS_DIR, "setup_dev_env.py")
RESET_SCRIPT = os.path.join(SCRIPTS_DIR, "reset_dev_env.py")

def cleanup():
    """
    Runs the cleanup script when the server shuts down.
    This ensures that the database, migrations, and cache files are removed automatically.
    """
    print("Server stopping... Running cleanup script.")
    os.system(f"python {RESET_SCRIPT}")

# register cleanup function to execute when script exits
atexit.register(cleanup)

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GWIIT.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # check if user is running the Django server
    if len(sys.argv) > 1 and sys.argv[1] == "runserver":
        print("Detected 'runserver' command. Running setup script first...")
        
        # run setup script before launching server
        result = subprocess.run(["python", SETUP_SCRIPT], check=True)
        
        if result.returncode != 0:
            print("Error running setup script. Exiting.")
            sys.exit(1)

    # execute Django command-line utility
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
