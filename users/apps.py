from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = _('Users')

# class UsersConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "users"

    # # Ensure signals are loaded
    # def ready(self):
    #     import users.signals

    def ready(self):
        print("DEBUG: AppConfig ready() running for users app")
        print("DEBUG: Users app initialization complete.")