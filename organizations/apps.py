from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class OrganizationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'organizations'
    verbose_name = _('Organizations')

    def ready(self):
        print("DEBUG: AppConfig ready() running for organizations app")
        print("DEBUG: organizations app initialization complete.")