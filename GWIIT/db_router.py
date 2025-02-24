from django.apps import apps

class AuthenticationRouter:
    route_app_labels = {"authentication"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "authentication_db"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "authentication_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        allowed_apps = {"users", "organizations", "sites", "authentication", "authorization", "admin", "auth", "contenttypes", "sessions"}
        if obj1._meta.app_label in allowed_apps and obj2._meta.app_label in allowed_apps:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "authentication_db"
        return None


class AuthorizationRouter:
    route_app_labels = {"authorization"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "authorization_db"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "authorization_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        allowed_apps = {"users", "organizations", "sites", "authentication", "authorization", "admin", "auth", "contenttypes", "sessions"}
        if obj1._meta.app_label in allowed_apps and obj2._meta.app_label in allowed_apps:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "authorization_db"
        return None


class OrganizationsRouter:
    route_app_labels = {"organizations"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "organizations_db"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "organizations_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        allowed_apps = {"users", "organizations", "sites", "authentication", "authorization", "admin", "auth", "contenttypes", "sessions"}
        if obj1._meta.app_label in allowed_apps and obj2._meta.app_label in allowed_apps:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "organizations_db"
        return None


class SitesRouter:
    route_app_labels = {"sites"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "sites_db"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "sites_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        allowed_apps = {"users", "organizations", "sites", "authentication", "authorization", "admin", "auth", "contenttypes", "sessions"}
        if obj1._meta.app_label in allowed_apps and obj2._meta.app_label in allowed_apps:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "sites_db"
        return None


class UsersRouter:
    route_app_labels = {"users"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "users_db"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "users_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        allowed_apps = {"users", "organizations", "sites", "authentication", "authorization", "admin", "auth", "contenttypes", "sessions"}
        if obj1._meta.app_label in allowed_apps and obj2._meta.app_label in allowed_apps:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "users_db"
        return None


class DefaultRouter:
    # """Router for Django's default apps (admin, auth, contenttypes, sessions)."""
    # route_app_labels = {"admin", "auth", "contenttypes", "sessions"}

    # def db_for_read(self, model, **hints):
    #     if model._meta.app_label in self.route_app_labels:
    #         return "default"
    #     return None

    # def db_for_write(self, model, **hints):
    #     if model._meta.app_label in self.route_app_labels:
    #         return "default"
    #     return None

    # def allow_relation(self, obj1, obj2, **hints):
    #     allowed_apps = {"users", "organizations", "sites", "authentication", "authorization", "admin", "auth", "contenttypes", "sessions"}
    #     if obj1._meta.app_label in allowed_apps and obj2._meta.app_label in allowed_apps:
    #         return True
    #     return None

    # # def allow_migrate(self, db, app_label, model_name=None, **hints):
    # #     """Ensure default models only migrate to default."""
    # #     if app_label in self.route_app_labels:
    # #         return db == "default"
    # #     return None
    
    # def allow_migrate(self, db, app_label, model_name=None, **hints):
    #     if app_label == 'admin':
    #         return db == 'default'
    #     return None
    """Router for Django's default apps (admin, auth, contenttypes, sessions)."""
    route_app_labels = {"admin", "auth", "contenttypes", "sessions"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "default"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "default"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        allowed_apps = {
            "users", "organizations", "sites", "authentication", "authorization",
            "admin", "auth", "contenttypes", "sessions"
        }
        if obj1._meta.app_label in allowed_apps and obj2._meta.app_label in allowed_apps:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Allow `auth`, `contenttypes`, `sessions`, and `admin` to migrate in all databases that need them.
        This ensures models like `django_admin_log` are available where required.
        """
        if app_label in {"admin", "auth", "contenttypes", "sessions"}:
            return db in {"default", "users_db", "organizations_db", "sites_db"}
        return None