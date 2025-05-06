from django.db import connection
from pydantic import BaseModel
from typing import Type, Optional

def get_table_name_for_model(model_class):
    """Get the table name for a model class, handling both Django ORM and Pydantic models."""
    if hasattr(model_class, '_meta'):
        return model_class._meta.db_table
    elif hasattr(model_class, 'model_config') and 'table_name' in model_class.model_config:
        return model_class.model_config['table_name']
    elif hasattr(model_class, '__table__'):
        return model_class.__table__
    return None

def get_columns(table_name):
    """Get columns from the database for a given table."""
    query = """
        SELECT
            a.attname AS column_name,
            pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
            NOT a.attnotnull AS is_nullable,
            coalesce(i.indisprimary, false) AS is_primary,
            pg_catalog.col_description(a.attrelid, a.attnum) AS column_comment
        FROM
            pg_attribute a
        JOIN pg_class c ON a.attrelid = c.oid
        JOIN pg_namespace n ON c.relnamespace = n.oid
        LEFT JOIN pg_index i ON i.indrelid = c.oid AND a.attnum = ANY(i.indkey) AND i.indisprimary
        WHERE
            c.relname = %s AND
            a.attnum > 0 AND
            NOT a.attisdropped
        ORDER BY a.attnum;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [table_name])
        return cursor.fetchall()

def get_pydantic_fields(model_class: Type[BaseModel]) -> list:
    """Get field information from a Pydantic model."""
    fields = []
    for field_name, field in model_class.model_fields.items():
        field_type = str(field.annotation.__name__ if hasattr(field.annotation, '__name__') else field.annotation)
        is_required = field.is_required()
        is_primary = getattr(field.json_schema_extra or {}, 'primary_key', False) or field_name == 'id'
        
        type_str = field_type.lower()
        if is_required:
            type_str += " not null"
        if is_primary:
            type_str += ", primary key"
        if field.default is not None:
            type_str += f" default={field.default}"
            
        fields.append((field_name, type_str))
    return fields

def get_indexes(table_name):
    query = """
        SELECT
            indexname, indexdef
        FROM
            pg_indexes
        WHERE
            tablename = %s;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [table_name])
        return cursor.fetchall()

def get_foreign_keys(table_name):
    query = """
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM
            information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE
            constraint_type = 'FOREIGN KEY' AND
            tc.table_name = %s;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [table_name])
        return cursor.fetchall()

def get_schema_for_model(model_class, config=None):
    """Get schema information for a model, handling both Django ORM and Pydantic models."""
    if config is None:
        config = {}
    
    # Handle Pydantic models
    if isinstance(model_class, type) and issubclass(model_class, BaseModel):
        table_name = get_table_name_for_model(model_class)
        fields = get_pydantic_fields(model_class)
        # Pydantic models don't have database indexes or foreign keys
        return table_name, fields, [], []
    
    # Handle Django ORM models (existing code)
    table_name = get_table_name_for_model(model_class)
    raw_columns = get_columns(table_name)
    raw_indexes = get_indexes(table_name)
    raw_fks = get_foreign_keys(table_name)

    fields = []
    for name, dtype, nullable, is_primary, comment in raw_columns:
        # Skip ignored columns
        if name in config.get("ignore_columns", []):
            continue
            
        type_str = dtype
        if not nullable:
            type_str += " not null"
        if is_primary:
            type_str += ", primary key"
            
        # Handle column comments
        if comment and config.get("with_column_comments", True):
            type_str += f"  # {comment}"
        fields.append((name, type_str))

    indexes = []
    if config.get("show_indexes", True):
        for index_name, definition in raw_indexes:
            if "UNIQUE" in definition:
                suffix = "UNIQUE"
            else:
                suffix = ""
            column_match = definition.split("(")[-1].split(")")[0]
            indexes.append(f"{index_name}  ({column_match}) {suffix}".strip())

    fks = []
    if config.get("show_foreign_keys", True):
        for col, ref_table, ref_col in raw_fks:
            fks.append(f"{col} => {ref_table}.{ref_col}")

    return table_name, fields, indexes, fks
