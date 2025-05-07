"""
Parser module for django-annotate.
"""

import ast
import importlib.util
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from .db_introspect.factory import get_introspector

SCHEMA_HEADER = "# == Schema Information"
SCHEMA_FIELD_SECTION = "#\n# Table name: {table_name}\n#\n{fields}"
SCHEMA_INDEXES_SECTION = "#\n# Indexes\n#\n{indexes}"
SCHEMA_FOREIGN_KEYS_SECTION = "#\n# Foreign Keys\n#\n{foreign_keys}"

def format_field_line(field_info: Union[Tuple[str, str], Tuple[str, str, bool, bool, Optional[str]]]) -> str:
    """Format a field line for the schema block."""
    if len(field_info) == 2:
        # Old format: (name, type_info)
        name, type_info = field_info
        return f"{name}: {type_info}"
    else:
        # New format: (name, type_info, nullable, primary_key, comment)
        name, type_info, nullable, primary_key, comment = field_info
        line = f"{name}: {type_info}"
        if comment:
            line += f"  # {comment}"
        return line

def format_field_type(field_type: str) -> str:
    """Format field type with consistent padding."""
    # Split the field type into base type and modifiers
    parts = field_type.split(' not null')
    base_type = parts[0]
    modifiers = []
    
    # Add "not null" if present
    if len(parts) > 1:
        modifiers.append('not null')
    
    # Add "primary key" if present
    if 'primary key' in field_type:
        modifiers.append('primary key')
    
    # Return base type and modifiers separately for alignment
    return base_type, ', '.join(modifiers) if modifiers else None

def format_index(index: str) -> str:
    """Format an index with consistent padding."""
    # Extract index name and columns
    parts = index.split()
    name = parts[0]
    
    # Find the column list between parentheses
    start = index.find('(')
    end = index.find(')')
    if start != -1 and end != -1:
        columns = index[start:end+1]  # Keep the parentheses
        # Handle UNIQUE constraint
        if 'UNIQUE' in index:
            # Remove any extra parentheses from the end
            columns = columns.rstrip(')')
            return name, f"{columns}) UNIQUE"
        return name, columns
    
    return name, index  # Fallback for unexpected format

def format_foreign_key(fk: str) -> str:
    """Format a foreign key with consistent padding."""
    # Extract the parts before and after the arrow
    if '=>' in fk:
        name, target = fk.split('=>')
        return f"{name.strip()} => {target.strip()}"
    return fk

def generate_schema_block(
    table_name: str,
    columns: List[Union[Tuple[str, str], Tuple[str, str, Optional[str]]]],
    indexes: List[str],
    foreign_keys: List[str],
    config: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate a schema block for a model."""
    config = config or {}
    show_indexes = config.get('show_indexes', True)
    show_foreign_keys = config.get('show_foreign_keys', True)

    lines = [
        "# == Schema Information",
        "#",
        f"# Table name: {table_name}",
        "#"
    ]

    # Find the longest attribute name and data type for alignment
    max_name_length = max(len(col[0]) for col in columns)
    max_type_length = max(len(format_field_type(col[1])[0]) for col in columns)
    max_modifier_length = max(len(format_field_type(col[1])[1] or '') for col in columns)

    # Add columns
    for column in columns:
        name = column[0]
        type_info, modifiers = format_field_type(column[1])
        comment = column[2] if len(column) > 2 else None
        
        # Format with consistent spacing:
        # - Name left-aligned and padded to max_name_length
        # - Type left-aligned in its column
        # - Modifiers right-aligned in their column
        line = f"#  {name:<{max_name_length}}  :{type_info:<{max_type_length}}"
        if modifiers:
            line += f"         {modifiers:>{max_modifier_length}}"
        if comment:
            line += f" {comment}"
        lines.append(line)

    # Add indexes if enabled
    if show_indexes and indexes:
        lines.extend(["#", "# Indexes", "#"])
        # Find the longest index name for alignment
        max_index_length = max(len(format_index(idx)[0]) for idx in indexes)
        for index in indexes:
            name, columns = format_index(index)
            lines.append(f"#  {name:<{max_index_length}}    {columns}")

    # Add foreign keys if enabled
    if show_foreign_keys and foreign_keys:
        lines.extend(["#", "# Foreign Keys", "#"])
        for fk in foreign_keys:
            formatted_fk = format_foreign_key(fk)
            lines.append(f"#  {formatted_fk}")
        lines.append("#")  # Add extra newline after foreign keys

    return "\n".join(lines)

def get_model_class(file_path: str, model_name: str):
    """Import and return a model class from a file."""
    spec = importlib.util.spec_from_file_location("module", file_path)
    if not spec or not spec.loader:
        raise ImportError(f"Could not load module from {file_path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Handle nested classes
    if '.' in model_name:
        outer_name, inner_name = model_name.split('.')
        outer_class = getattr(module, outer_name)
        return getattr(outer_class, inner_name)
    
    return getattr(module, model_name)

def find_model_classes(file_path: str) -> List[str]:
    """Find all model classes in a file."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    model_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if the class inherits from models.Model
            for base in node.bases:
                if isinstance(base, ast.Attribute):
                    if base.attr == 'Model' and isinstance(base.value, ast.Name) and base.value.id == 'models':
                        model_names.append(node.name)
                elif isinstance(base, ast.Name) and base.id == 'Model':
                    model_names.append(node.name)

            # Check for nested model classes
            for child in node.body:
                if isinstance(child, ast.ClassDef):
                    for base in child.bases:
                        if isinstance(base, ast.Attribute):
                            if base.attr == 'Model' and isinstance(base.value, ast.Name) and base.value.id == 'models':
                                model_names.append(f"{node.name}.{child.name}")
                        elif isinstance(base, ast.Name) and base.id == 'Model':
                            model_names.append(f"{node.name}.{child.name}")

    return model_names

def annotate_model_file(file_path: str, schema_lookup, config: Optional[Dict[str, Any]] = None) -> str:
    """Annotate a model file with schema information."""
    config = config or {}
    position = config.get('position', 'before')  # 'before' or 'after'
    ignored_columns = set(config.get('ignore_columns', []))

    with open(file_path, 'r') as f:
        content = f.read()

    # Find all model classes
    model_names = find_model_classes(file_path)

    # Remove all existing schema blocks
    content = re.sub(r'# == Schema Information\n(?:#.*\n)*(?=\s*(?:class|$))', '', content)

    # Process each model in order
    for model_name in model_names:
        try:
            # Get schema information
            table_name, columns, indexes, foreign_keys = schema_lookup(model_name)

            # Filter out ignored columns and handle column tuples
            filtered_columns = []
            for col in columns:
                name = col[0]
                if name not in ignored_columns:
                    if len(col) >= 5 and config.get('with_column_comments', False):
                        # Include comment if available and enabled
                        filtered_columns.append((name, col[1], col[4]))
                    else:
                        # Just include name and type
                        filtered_columns.append((name, col[1]))

            # Skip if all columns are ignored
            if not filtered_columns:
                continue

            # Generate schema block
            schema_block = generate_schema_block(table_name, filtered_columns, indexes, foreign_keys, config)

            # Find the model class definition
            model_pattern = re.compile(fr"class\s+{model_name}\s*\([^)]*\):")
            match = model_pattern.search(content)
            if not match:
                continue

            # Insert schema block
            if position == 'before':
                insert_pos = match.start()
                # Add a newline before the schema block if it's not at the start of the file
                if insert_pos > 0 and content[insert_pos-1] != '\n':
                    schema_block = '\n' + schema_block
                # Add a newline after the schema block
                content = content[:insert_pos] + schema_block + "\n\n" + content[insert_pos:]
            else:  # after
                class_end = content.find("\n\n", match.end())
                if class_end == -1:
                    class_end = len(content)
                content = content[:class_end] + "\n\n" + schema_block + content[class_end:]

        except LookupError:
            continue

    # Clean up any extra newlines (but keep double newlines between models)
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    return content

def format_schema_info(table_name: str, columns: List[Tuple], indexes: List[Tuple], foreign_keys: List[Tuple]) -> str:
    """
    Format schema information into a readable string.
    """
    lines = [f"Table: {table_name}"]

    if columns:
        lines.append("\nColumns:")
        for col in columns:
            # Handle both old (2-tuple) and new (5-tuple) formats
            if len(col) == 2:
                name, type_ = col
                nullable = False
                is_primary = False
                comment = None
            else:
                name, type_, nullable, is_primary, comment = col

            # Format the column information
            line = f"  {name}: {type_}"
            if comment:
                line += f" # {comment}"
            lines.append(line)

    if indexes:
        lines.append("\nIndexes:")
        for idx in indexes:
            if isinstance(idx, tuple):
                name, defn = idx
                lines.append(f"  {name}: {defn}")
            else:
                lines.append(f"  {idx}")

    if foreign_keys:
        lines.append("\nForeign Keys:")
        for fk in foreign_keys:
            if isinstance(fk, tuple):
                name, defn = fk
                lines.append(f"  {name}: {defn}")
            else:
                lines.append(f"  {fk}")

    return "\n".join(lines)
