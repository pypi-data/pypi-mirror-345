import os
from pathlib import Path
import yaml

DEFAULT_CONFIG = {
    "skip_on_migrate": False,
    "position": "before",  # before or after the model class
    "format": "plain",     # plain, markdown, or rdoc
    "show_indexes": True,
    "show_foreign_keys": True,
    "show_comments": False,
    "ignore_models": [],   # list of model names to ignore
    "ignore_apps": [],     # list of app labels to ignore
}

def load_config():
    """Load configuration from .django_annotate.yml if it exists, otherwise return defaults."""
    config = DEFAULT_CONFIG.copy()
    
    # Look for config file in project root
    project_root = Path(os.getcwd())
    config_file = project_root / ".django_annotate.yml"
    
    if config_file.exists():
        with open(config_file) as f:
            user_config = yaml.safe_load(f) or {}
            config.update(user_config)
    
    # Environment variables override config file
    if os.environ.get("DJANGO_ANNOTATE_SKIP_ON_MIGRATE") == "1":
        config["skip_on_migrate"] = True
    
    return config 
