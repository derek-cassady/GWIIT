import os
import shutil
import glob

# define project root directory
# script is inside "scripts/" and needs to go one level up
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# define the database file path (SQLite for dev, testing, and demo)
DB_PATH = os.path.join(PROJECT_ROOT, "db.sqlite3")

# define paths to migration directories
# find all "migrations" folders inside each Django app
MIGRATIONS_GLOB = os.path.join(PROJECT_ROOT, "**", "migrations", "*.py")

# define paths to "__pycache__" directories
PYCACHE_GLOB = os.path.join(PROJECT_ROOT, "**", "__pycache__")

# function to delete the database file
def delete_database():
    """Deletes the SQLite database file if it exists."""
    if os.path.exists(DB_PATH):
        print(f"Deleting database: {DB_PATH}")
        os.remove(DB_PATH)
    else:
        print("No database file found.")

# function to delete "migration" files
def delete_migrations():
    """Deletes all migration files except '__init__.py'."""
    for migration_file in glob.glob(MIGRATIONS_GLOB, recursive=True):
        if not migration_file.endswith("__init__.py"):
            print(f"Deleting migration: {migration_file}")
            os.remove(migration_file)

# function to delete "__pycache__" directories
def delete_pycache():
    """Deletes all __pycache__ directories recursively."""
    for pycache_dir in glob.glob(PYCACHE_GLOB, recursive=True):
        print(f"Deleting __pycache__: {pycache_dir}")
        shutil.rmtree(pycache_dir, ignore_errors=True)

# execute cleanup functions when script runs
if __name__ == "__main__":
    print("Resetting development environment...")
    delete_database()
    delete_migrations()
    delete_pycache()
    print("Development environment reset complete.")
