from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class SitesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sites'
    verbose_name = _('Sites')