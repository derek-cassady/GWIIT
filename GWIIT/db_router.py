class DatabaseRouter:
    
    # database router to control operations for each app

    """
    Determines which database should be used for read operations.
        - Each app has its own dedicated database.
        - This method routes read queries (`SELECT`) to the appropriate database.
    """

    def db_for_read(self, model, **hints):
        # point read operations to the correct database
        
        # authentication DB
        if model._meta.app_label == 'authentication':
            return 'auth_db'
        
        # authorization DB
        elif model._meta.app_label == 'authorization':
            return 'authorization_db'
        
        # organizations DB
        elif model._meta.app_label == 'organizations':
            return 'organizations_db'
        
        # sites DB
        elif model._meta.app_label == 'sites':
            return 'sites_db'
        
        # users DB
        elif model._meta.app_label == 'users':
            return 'users_db'
        
        return 'default'

    """
    Determines which database should be used for write operations.
        - Instead of duplicating logic, it calls `db_for_read()`
        - This ensures that write operations (`INSERT`, `UPDATE`, `DELETE`) 
            go to the same database as read operations.  
    """

    def db_for_write(self, model, **hints):
        
        return self.db_for_read(model, **hints)

    """
    Determines if a relation between two objects should be allowed.
        - Defines a set of valid database names (`db_set`).
        - Checks if both objects belong to one of the databases in `db_set`.
        - If both objects are stored in a recognized database, the relation is allowed (`True`).
        - If the condition fails, Django will disallow the relation (`None`).
    """
    
    def allow_relation(self, obj1, obj2, **hints):
        
        #  database names that are valid
        db_set = {'auth_db', 'authorization_db', 'organizations_db', 'sites_db', 'users_db', 'default'}
        
        # checks if DB for object 1 and then 2 are in the "db_set"
        if obj1._state.db in db_set and obj2._state.db in db_set:
            
            # allows relationship
            return True
        
        # if condition fails, DJango disallows relationship
        return None

    """
    Determines whether a model's migration should be applied to a given database.
        - Maps each app to its designated database.
        - Ensures migrations only run on the correct database.
            - `True` if the migration should be applied to the specified database.
            - `False` otherwise.
    """
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        
        app_db_mapping = {
        'authentication': 'auth_db',
        'authorization': 'authorization_db',
        'organizations': 'organizations_db',
        'sites': 'sites_db',
        'users': 'users_db',
    }

        # Check if the app is in the mapping and ensure migration runs on the correct database
        if app_label in app_db_mapping:
            return db == app_db_mapping[app_label]

        # Default fallback for other apps
        return db == 'default'
