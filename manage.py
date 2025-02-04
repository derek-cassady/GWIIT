#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import atexit

# define path to cleanup script
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "scripts", "reset_dev_env.py")

def cleanup():
    """
    Runs the cleanup script when the server shuts down.
    This ensures that the database, migrations, and cache files are removed automatically.
    """
    print("Server stopping... Running cleanup script.")
    os.system(f"python {SCRIPT_PATH}")

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
    
    # execute Django command-line utility
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
