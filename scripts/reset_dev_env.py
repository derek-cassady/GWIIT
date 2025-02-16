"""
This script resets the development environment by:
    - Removing all SQLite database files.
    - Deleting migration files except '__init__.py'.
    - Clearing all '__pycache__' directories.

This script is called automatically when the server stops, ensuring 
that everything is reset before the next startup.
"""

import os
import shutil
import glob
import sys
import time

# define project root directory
# script is inside "scripts/" and needs to go one level up
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DB_GLOB = os.path.join(PROJECT_ROOT, "*.sqlite3")

# define the database file path (SQLite for dev, testing, and demo)
DB_PATH = os.path.join(PROJECT_ROOT, "db.sqlite3")

# define paths to migration directories
# find all "migrations" folders inside each Django app
MIGRATIONS_GLOB = os.path.join(PROJECT_ROOT, "**", "migrations", "*.py")

# define paths to "__pycache__" directories
PYCACHE_GLOB = os.path.join(PROJECT_ROOT, "**", "__pycache__")

# """
# Check if the script was triggered by an actual shutdown,
# script is triggered with a "--shutdown" argument when the server stops.
# """
# if "--shutdown" not in sys.argv:
#     print("Reset script triggered incorrectly. Skipping cleanup.")
    
#     # Exit before running cleanup if shutdown flag isn't set.
#     # prevents accidental deletion of data during migrations or setup.
#     sys.exit(0)

print("Resetting development environment...")

"""
Terminates any Python processes to release locked resources.
"""

def cleanup_processes():

    print("Stopping all running Python processes...")
    os.system("taskkill /F /IM python.exe")  # Windows only
    time.sleep(4)  # Give OS time to free locked files

"""
Deletes all '__pycache__' directories in the project.
    - Python generates '__pycache__' folders to store compiled bytecode files (*.pyc).
        - These files are not needed for development and can cause issues when code changes.
        - Deleting them ensures that Python recompiles everything fresh on the next run. 
            - Searches for all '__pycache__' directories in the project.
            - Recursively deletes each '__pycache__' folder.

    - 'shutil.rmtree()' is used to remove directories and ignore errors.
    - 'ignore_errors=True' prevents the script from stopping if a directory is already deleted.
"""

def delete_pycache():

    print("DEBUG: Entering delete_pycache()")
    for pycache_dir in glob.glob(PYCACHE_GLOB, recursive=True):
        print(f"DEBUG: Found __pycache__ {pycache_dir}, attempting to delete...")
        try:
            shutil.rmtree(pycache_dir)
            print(f"SUCCESS: Deleted {pycache_dir}")
        except Exception as e:
            print(f"ERROR: Failed to delete {pycache_dir}. Reason: {e}")

"""
Deletes all migration files in the project, except '__init__.py'.
    - Migrations need to be rebuilt every time the development server starts.
        - If old migration files remain, they could cause conflicts with new changes
    - Keeping '__init__.py' ensures Django still recognizes the 'migrations' directory.
        - Searches all 'migrations/' directories in the project.
        - Deletes any `.py` migration file except '__init__.py'.

"""
def delete_migrations():

    print("DEBUG: Entering delete_migrations()")
    found_files = glob.glob(MIGRATIONS_GLOB, recursive=True)
    
    if not found_files:
        print("DEBUG: No migration files found. Skipping delete_migrations().")
        return
    
    for migration_file in found_files:
        if not migration_file.endswith("__init__.py"):  # Avoid deleting __init__.py
            print(f"DEBUG: Found migration {migration_file}, attempting to delete...")
            try:
                os.chmod(migration_file, 0o777)  # Ensure file is writable
                os.remove(migration_file)
                print(f"SUCCESS: Deleted {migration_file}")
            except Exception as e:
                print(f"ERROR: Failed to delete {migration_file}. Reason: {e}")
    print("DEBUG: Finished delete_migrations()")

"""
Deletes all SQLite database files used in the development environment.
    - Ensures that when resetting the environment, no database files remain.
        - Searches for all SQLite files (*.sqlite3) in the project directory.
        - Deletes each database file found.
"""

# function to delete database files
def delete_databases():
    print("DEBUG: Entering delete_databases()")
    time.sleep(1)  # Ensure processes have stopped

    print("DEBUG: Deleting database...")
    # Finds all .sqlite3 files
    for db_file in glob.glob(DB_GLOB):
        print(f"DEBUG: Found database file {db_file}, attempting to delete...")
        try:
            os.remove(db_file)
            print(f"SUCCESS: Deleted {db_file}")
        except PermissionError:
            print(f"WARNING: {db_file} is locked. Retrying after delay...")
            time.sleep(1)
            try:
                os.remove(db_file)
                print(f"SUCCESS: Deleted {db_file} on retry")
            except PermissionError:
                print(f"ERROR: Failed to delete {db_file}. It may still be in use.")

"""
Ensures cleanup script only runs when executed directly, not when imported as module.
- Prints a message indicating that the reset process has started.
    - Calls cleanup functions to:
        -Delete all database files (delete_databases()).
        -Remove all migration files except '__init__.py' (delete_migrations()).
        -Clear all '__pycache__' directories (delete_pycache()).
    - Prints a message confirming that the reset is complete.

    - Running this script resets the development environment to a clean state.
    - Prevents stale data, old migrations, and cached files from interfering with testing.

- This should only run when shutting down the server, not during setup.    
"""

if __name__ == "__main__":
    # Ensure the script was triggered by an actual shutdown
    if "--shutdown" not in sys.argv:
        print("Reset script triggered incorrectly. Skipping cleanup.")
        sys.exit(0)

    print("Resetting development environment...")
    
    # Execute cleanup functions in the correct order
    print("DEBUG: Calling delete_databases()")
    delete_databases()

    print("DEBUG: Calling delete_migrations()")
    delete_migrations()

    print("DEBUG: Calling delete_pycache()")
    delete_pycache()

    print("DEBUG: Now calling cleanup_processes() LAST to avoid premature shutdown")
    cleanup_processes()

    print("Development environment reset complete.")