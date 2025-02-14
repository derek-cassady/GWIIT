from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'

def ready(self):
        print("DEBUG: AppConfig ready() running for authentication app")
        print("DEBUG: authentication app initialization complete.")