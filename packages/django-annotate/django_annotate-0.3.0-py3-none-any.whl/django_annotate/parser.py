import re

SCHEMA_HEADER = "# == Schema Information"
SCHEMA_FIELD_SECTION = "#\n# Table name: {table_name}\n#\n{fields}"
SCHEMA_INDEXES_SECTION = "#\n# Indexes\n#\n{indexes}"
SCHEMA_FOREIGN_KEYS_SECTION = "#\n# Foreign Keys\n#\n{foreign_keys}"

def format_field_line(name, field_info):
    """Format a single field line for the schema block."""
    if isinstance(field_info, tuple):
        field_type = field_info[0]
        comment = field_info[-1] if len(field_info) > 2 else None
    else:
        field_type = field_info
        comment = None
    
    line = f"#  {name:<18}: {field_type}"
    if comment:
        line += f"  # {comment}"
    return line

def generate_schema_block(table_name, fields, indexes, fks, config=None):
    """Generate a schema block for a model."""
    if config is None:
        config = {}
    
    parts = [SCHEMA_HEADER]
    
    # Filter out ignored columns
    ignored_columns = config.get("ignore_columns", [])
    filtered_fields = []
    for field in fields:
        if isinstance(field, tuple):
            name = field[0]
            field_info = field[1:]
            if name not in ignored_columns:
                filtered_fields.append((name, field_info[0]))
                if len(field_info) > 3 and field_info[3] and config.get("with_column_comments", True):
                    filtered_fields[-1] = (name, field_info[0], field_info[3])
        else:
            name = field
            if name not in ignored_columns:
                filtered_fields.append((name, name))
    
    if filtered_fields:
        field_lines = []
        for field in filtered_fields:
            if len(field) == 3:
                field_lines.append(format_field_line(field[0], (field[1], field[2])))
            else:
                field_lines.append(format_field_line(field[0], field[1]))
        parts.append(SCHEMA_FIELD_SECTION.format(table_name=table_name, fields="\n".join(field_lines)))
    
    if indexes and config.get("show_indexes", True):
        index_lines = "\n".join([f"# {idx}" for idx in indexes])
        parts.append(SCHEMA_INDEXES_SECTION.format(indexes=index_lines))
    
    if fks and config.get("show_foreign_keys", True):
        fk_lines = "\n".join([f"# {fk}" for fk in fks])
        parts.append(SCHEMA_FOREIGN_KEYS_SECTION.format(foreign_keys=fk_lines))
    
    # Add timestamp if configured
    if config.get("timestamp", False):
        from datetime import datetime
        parts.append(f"#\n# Generated at: {datetime.now().isoformat()}")
    
    # Add version if configured
    if config.get("include_version", False):
        from django_annotate import __version__
        parts.append(f"#\n# Version: {__version__}")
    
    return "\n".join(parts)

def annotate_model_file(file_path, schema_data_lookup, config=None):
    if config is None:
        config = {}
    
    with open(file_path, "r") as f:
        content = f.read()

    # Update pattern to match both Django ORM and Pydantic models
    class_pattern = re.compile(r'^(class\s+(\w+)\s*\(.*?(?:models\.Model|pydantic\.BaseModel).*?\):)', re.MULTILINE)
    matches = list(class_pattern.finditer(content))
    if not matches:
        print(f"No models found in {file_path}")
        return

    lines = content.splitlines()
    output = []
    last_idx = 0

    for match in matches:
        class_line_idx = content[:match.start(1)].count("\n")
        class_name = match.group(2)

        # Skip ignored models
        if class_name in config.get("ignore_models", []):
            output.extend(lines[last_idx:class_line_idx + 1])
            last_idx = class_line_idx + 1
            continue

        # Add lines up to this point
        output.extend(lines[last_idx:class_line_idx])

        # Remove existing block if present
        lookback = class_line_idx - 1
        while lookback >= 0 and (not lines[lookback].strip() or lines[lookback].startswith("#")):
            lookback -= 1
        lookback += 1
        if lookback < class_line_idx:
            output = output[:lookback]

        # Add new schema block
        table, fields, indexes, fks = schema_data_lookup(class_name)
        annotation = generate_schema_block(table, fields, indexes, fks, config)
        
        # Handle position configuration
        if config.get("position", "before") == "before":
            output.extend(annotation.rstrip().splitlines())
            output.append("")  # Add blank line
            output.append(lines[class_line_idx])
        else:
            output.append(lines[class_line_idx])
            output.append("")  # Add blank line
            output.extend(annotation.rstrip().splitlines())
            
        last_idx = class_line_idx + 1

    output.extend(lines[last_idx:])
    with open(file_path, "w") as f:
        f.write("\n".join(output) + "\n")
