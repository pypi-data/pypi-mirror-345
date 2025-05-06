from django.db import connection
from .base import DatabaseIntrospector

class PostgreSQLIntrospector(DatabaseIntrospector):
    """PostgreSQL-specific database introspection."""
    
    def get_table_name(self, model_class) -> str:
        return model_class._meta.db_table
    
    def get_columns(self, table_name: str):
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
    
    def get_indexes(self, table_name: str):
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
    
    def get_foreign_keys(self, table_name: str):
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