#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks, 
including server setup and cleanup.
"""
import os
import sys
# ability register a shutdown hook
import atexit
# ability to run scripts
import subprocess

# define path to setup and cleanup scripts

# Locate the "scripts/" folder
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")

# Path to setup script
SETUP_SCRIPT = os.path.join(SCRIPTS_DIR, "setup_dev_env.py")

# Path to cleanup script
RESET_SCRIPT = os.path.join(SCRIPTS_DIR, "reset_dev_env.py")

"""
Ensures the development environment resets on server shutdown.
    - Prevents old data from lingering between test sessions.
    - Automatically removes databases, migrations, and cached files.
        - Runs `reset_dev_env.py` when the script exits.
        - Prints a message to confirm cleanup is running.
"""
def cleanup():

    print("Server stopping... Running cleanup script.")
    os.system(f"python {RESET_SCRIPT}")

# register cleanup function to execute when script exits
atexit.register(cleanup)

"""
Run administrative tasks.
    - Ensures the correct Django settings module is set.
    - Calls Django's command-line interface (manage.py commands).
    - If the server stops (either manually or due to an error), cleanup is triggered.
"""

def main():
    # run administrative tasks.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GWIIT.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    try:
        # Run Django command-line utility
        execute_from_command_line(sys.argv)
    
    except KeyboardInterrupt:
        # Handle manual server stop (Ctrl + C)
        print("\nServer stopped manually. Running cleanup...")
        subprocess.run(["python", "scripts/reset_dev_env.py", "--shutdown"])
    
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error: {e}")
    
    finally:
        # If the server was running and has stopped, trigger cleanup
        if "runserver" in sys.argv:
            print("Server stopping... Running cleanup script.")
            subprocess.run(["python", "scripts/reset_dev_env.py", "--shutdown"])


if __name__ == '__main__':
    main()
