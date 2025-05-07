"""
Django signals for auto-annotation.
"""

import os
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
from pathlib import Path
import importlib
import sys

from django_annotate.parser import annotate_model_file
from django_annotate.db_introspect.factory import get_introspector
from django_annotate.config import load_config

@receiver(post_migrate)
def auto_annotate_after_migrate(sender, **kwargs):
    """Auto-annotate models after migrations."""
    from django.conf import settings
    from django.apps import apps
    from .config import load_config
    from .db_introspect.factory import get_introspector
    from .parser import annotate_model_file

    # Skip if disabled
    if not getattr(settings, 'DEBUG', False):
        return
    if getattr(settings, 'DJANGO_ANNOTATE_DISABLE_AUTO', False):
        return

    # Get config
    config = load_config()
    if config.get('skip_on_migrate', False):
        return

    # Get introspector
    introspector = get_introspector()

    # Process each app
    for app_config in apps.get_app_configs():
        # Skip ignored apps
        if app_config.label in config.get('ignore_apps', []):
            continue

        # Get models file
        models_file = os.path.join(app_config.path, 'models.py')
        if not os.path.exists(models_file):
            continue

        # Import the models module
        sys.path.insert(0, os.path.dirname(app_config.path))
        try:
            models_module = importlib.import_module(f"{app_config.label}.models")
        except ImportError:
            continue
        finally:
            sys.path.pop(0)

        # Define schema lookup function
        def schema_lookup(model_name):
            try:
                if '.' in model_name:
                    outer_name, inner_name = model_name.split('.')
                    outer_class = getattr(models_module, outer_name)
                    model_class = getattr(outer_class, inner_name)
                else:
                    model_class = getattr(models_module, model_name)
                if model_class is None:
                    raise LookupError(f'Model "{model_name}" not found in app "{app_config.label}"')
                return introspector.get_schema_for_model(model_class, config)
            except (AttributeError, ImportError) as e:
                raise LookupError(f'Model "{model_name}" not found in app "{app_config.label}"') from e

        # Annotate models
        try:
            with open(models_file, 'r+') as f:
                content = annotate_model_file(models_file, schema_lookup, config=config)
                f.seek(0)
                f.write(content)
                f.truncate()
        except Exception as e:
            print(f"Error annotating {app_config.label}: {e}")
            continue 