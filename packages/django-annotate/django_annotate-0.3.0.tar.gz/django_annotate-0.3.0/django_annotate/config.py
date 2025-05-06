import os
from pathlib import Path
import yaml

DEFAULT_CONFIG = {
    # Position settings
    "position": "before",  # before or after the model class

    # Schema information settings
    "show_indexes": True,
    "show_foreign_keys": True,
    "with_column_comments": True,
    "include_version": False,
    "timestamp": False,

    # Pydantic-specific settings
    "pydantic": {
        "show_field_types": True,  # Show Pydantic field types
        "show_validators": False,  # Show field validators
        "show_defaults": True,  # Show default values
    },

    # Exclusion settings
    "ignore_models": [],  # list of model names to ignore
    "ignore_apps": [],  # list of app labels to ignore
    "ignore_columns": [],

    # Auto-annotation settings
    "skip_on_migrate": False,
    "force": False,
    "frozen": False,
}

def load_config_from_file(config_file):
    """Load configuration from a specific YAML file."""
    try:
        with open(config_file) as f:
            user_config = yaml.safe_load(f) or {}
            # Create a new dict with defaults and update with user config
            config = DEFAULT_CONFIG.copy()
            # Update each section separately to ensure proper merging
            for key, value in user_config.items():
                if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                    config[key].update(value)
                else:
                    config[key] = value
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()

def load_config():
    """Load configuration from YAML file or return defaults."""
    # Look for config file in project root
    project_root = Path(os.getcwd())
    config_file = project_root / ".django_annotate.yml"
    
    if not config_file.exists():
        return DEFAULT_CONFIG.copy()
    
    return load_config_from_file(config_file) 
