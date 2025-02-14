#!/usr/bin/env python
print("DEBUG: manage.py execution started...")
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
import time

# define path to setup and cleanup scripts

# Locate the "scripts/" folder
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts")

# Path to setup script
SETUP_SCRIPT = os.path.join(SCRIPTS_DIR, "setup_dev_env.py")

# # Path to cleanup script
# RESET_SCRIPT = os.path.join(SCRIPTS_DIR, "reset_dev_env.py")

"""
Runs the setup script before starting the server.
    - Ensures migrations are applied and the environment is ready.
    - Only runs if 'runserver' is the command.
"""

def run_setup():
    lock_file = "setup_running.lock"

    # If the lock file exists, another process is already running setup, so exit
    if os.path.exists(lock_file):
        print("DEBUG: Setup is already running in another process. Skipping duplicate execution.")
        return
    
    # Create a lock file to indicate setup is running
    with open(lock_file, "w") as f:
        f.write(str(time.time()))

    print(f"DEBUG: run_setup() function called at {time.time()} before running setup_dev_env.py")
    
    try:
        subprocess.run(["python", "scripts/setup_dev_env.py"], check=True)
        print(f"DEBUG: setup_dev_env.py completed successfully at {time.time()}")

    except subprocess.CalledProcessError as e:
        print(f"ERROR: setup_dev_env.py failed with exit code {e.returncode}")
        sys.exit(1)

    finally:
        # Remove the lock file after setup completes
        if os.path.exists(lock_file):
            os.remove(lock_file)

"""
Ensures the development environment resets on server shutdown.
    - Prevents old data from lingering between test sessions.
    - Automatically removes databases, migrations, and cached files.
        - Runs `reset_dev_env.py` when the script exits.
        - Prints a message to confirm cleanup is running.
"""
# def cleanup():
#     print("Server stopping... Running cleanup script.")
#     subprocess.run(["python", RESET_SCRIPT, "--shutdown"], check=True)

# from django.core.management.commands.runserver import Command as RunserverCommand

# class CustomRunserverCommand(RunserverCommand):
#     def handle(self, *args, **options):
#         try:
#             super().handle(*args, **options)
#         finally:
#             print("DEBUG: Django server shutting down, calling cleanup...")
#             cleanup()

"""
Run administrative tasks.
    - Ensures the correct Django settings module is set.
    - Calls Django's command-line interface (manage.py commands).
    - If the server stops (either manually or due to an error), cleanup is triggered.
"""
print("DEBUG: Entering main() function...")
def main():
    print(f"DEBUG: manage.py execution started at {time.time()}")
    # run administrative tasks.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GWIIT.settings')
    
    print("DEBUG: manage.py execution started...")


    try:
        # Ensure setup runs first before continuing
        run_setup()

        # Wait for setup_complete.lock before continuing
        SETUP_COMPLETE_FILE = "setup_complete.lock"
        
        # Max wait time in seconds
        MAX_WAIT_TIME = 60
        
        # Check every 2 seconds
        WAIT_INTERVAL = 2

        start_time = time.time()
        while not os.path.exists(SETUP_COMPLETE_FILE):
            if time.time() - start_time > MAX_WAIT_TIME:
                
                print("ERROR: Setup did not complete within the expected time.")
                sys.exit(1)
            
            print("DEBUG: Waiting for setup to complete...")
            time.sleep(WAIT_INTERVAL)

        # Once the lock file is detected, remove it to avoid future interference
        os.remove(SETUP_COMPLETE_FILE)
        print("DEBUG: Setup complete. Lock file removed.")
        
        from django.core.management import execute_from_command_line
        print("DEBUG: Calling execute_from_command_line()...")
        execute_from_command_line(sys.argv)
    
    except Exception as e:
        print(f"ERROR: Exception occurred in manage.py: {e}")
        sys.exit(1)

    # finally:
    #     # if "runserver" in sys.argv:
    #         print("Server shutting down... Running cleanup script.")
    #         # cleanup()

print("DEBUG: manage.py execution complete.")    

if __name__ == '__main__':
    main()
