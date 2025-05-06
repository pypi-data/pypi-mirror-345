from django.db import connection

def get_table_name_for_model(model_class):
    return model_class._meta.db_table

def get_columns(table_name):
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
    if config is None:
        config = {}
    
    table_name = get_table_name_for_model(model_class)
    raw_columns = get_columns(table_name)
    raw_indexes = get_indexes(table_name)
    raw_fks = get_foreign_keys(table_name)

    fields = []
    for name, dtype, nullable, is_primary, comment in raw_columns:
        type_str = dtype
        if not nullable:
            type_str += " not null"
        if is_primary:
            type_str += ", primary key"
        if comment and config.get("show_comments", False):
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
