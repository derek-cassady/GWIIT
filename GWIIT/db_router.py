class DatabaseRouter:
    
    # database router to control operations for each app
    
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

    # database used for reading a model will also be used for writing
        #write operations: save(), create(), update()
    def db_for_write(self, model, **hints):
        
        '''calls "db_for_read", determines which database to use for read operations
        then uses the same for writes'''
        return self.db_for_read(model, **hints)

    # allow relations if both objects belong to the same database
    def allow_relation(self, obj1, obj2, **hints):
        
        #  database names that are valid
        db_set = {'auth_db', 'authorization_db', 'organizations_db', 'sites_db', 'users_db', 'default'}
        
        # checks if DB for object 1 and then 2 are in the "db_set"
        if obj1._state.db in db_set and obj2._state.db in db_set:
            
            # allows relationship
            return True
        
        # if condition fails, DJango disallows relationship
        return None

    # ensure migrations occur on the correct database
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        
        # authentication DB
        if app_label == 'authentication':
            return db == 'auth_db'
        
        # authorization DB
        elif app_label == 'authorization':
            return db == 'authorization_db'
        
        # organizations DB
        elif app_label == 'organizations':
            return db == 'organizations_db'
        
        # sites DB
        elif app_label == 'sites':
            return db == 'sites_db'
        
        # users DB
        elif app_label == 'users':
            return db == 'users_db'
        
        return db == 'default'
