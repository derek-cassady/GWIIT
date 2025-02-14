from django.apps import AppConfig


class AuthorizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authorization'

def ready(self):
        print("DEBUG: AppConfig ready() running for authorization app")
        print("DEBUG: authorization app initialization complete.")