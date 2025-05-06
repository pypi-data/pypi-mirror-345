from django.conf import settings
from .base import DatabaseIntrospector
from .postgresql import PostgreSQLIntrospector

def get_introspector() -> DatabaseIntrospector:
    """
    Get the appropriate database introspector based on the database engine.
    """
    engine = settings.DATABASES['default']['ENGINE']
    
    if 'postgresql' in engine:
        return PostgreSQLIntrospector()
    else:
        raise NotImplementedError(f"Database engine {engine} is not supported") 