Django uses the model definitions in `models.py` to resolve relationships in fixture files.
Foreign key fields (e.g., `"type": 1`) reference the primary key (`pk`) of related records 
from other models. Ensure that referenced models are loaded first to maintain data integrity.

Fixtures should be loaded in this order:
1. `users.json`