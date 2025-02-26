#!/usr/bin/env python
"""
    Django Management Script (`manage.py`)

    Purpose:
        - Acts as the command-line utility for executing Django administrative tasks.
        - Loads Django settings and initializes the execution environment.

    **What is `#!/usr/bin/env python`?**
        - The shebang (`#!`) at the beginning of the script tells Unix-based operating systems which interpreter to use.
        - `env python` ensures that the correct Python interpreter is found in the system’s `$PATH`, allowing the script to run across different environments.
        - On Windows, this line is ignored, but it is necessary for compatibility on Linux/macOS.

    Expected Behavior:
        - **Sets up Django’s environment** by defining the `DJANGO_SETTINGS_MODULE`.
        - **Calls Django’s command-line utility** to execute management commands.
        - **Handles errors gracefully**, ensuring meaningful error messages if setup fails.

    Guarantees:
        - **Ensures Django is properly initialized** before executing any command.
        - **Supports multi-database configurations** by using Django’s built-in settings detection.
        - **Provides a consistent method to manage the project in all environments.**
"""

import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GWIIT.settings')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()