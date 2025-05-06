import re

SCHEMA_HEADER = "# == Schema Information"
SCHEMA_FIELD_SECTION = "#\n# Table name: {table_name}\n#\n{fields}"
SCHEMA_INDEXES_SECTION = "#\n# Indexes\n#\n{indexes}"
SCHEMA_FOREIGN_KEYS_SECTION = "#\n# Foreign Keys\n#\n{foreign_keys}"

def format_field_line(name, dtype):
    return f"# {name:<16} : {dtype}"

def generate_schema_block(table_name, fields, indexes, fks, config=None):
    if config is None:
        config = {}
        
    parts = [SCHEMA_HEADER]

    if fields:
        field_lines = "\n".join([format_field_line(n, t) for n, t in fields])
        parts.append(SCHEMA_FIELD_SECTION.format(table_name=table_name, fields=field_lines))

    if indexes and config.get("show_indexes", True):
        index_lines = "\n".join([f"# {idx}" for idx in indexes])
        parts.append(SCHEMA_INDEXES_SECTION.format(indexes=index_lines))

    if fks and config.get("show_foreign_keys", True):
        fk_lines = "\n".join([f"# {fk}" for fk in fks])
        parts.append(SCHEMA_FOREIGN_KEYS_SECTION.format(foreign_keys=fk_lines))

    return "\n".join(parts) + "\n"

def annotate_model_file(file_path, schema_data_lookup, config=None):
    if config is None:
        config = {}
    
    with open(file_path, "r") as f:
        content = f.read()

    class_pattern = re.compile(r'^(class\s+(\w+)\s*\(.*?models\.Model.*?\):)', re.MULTILINE)
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
