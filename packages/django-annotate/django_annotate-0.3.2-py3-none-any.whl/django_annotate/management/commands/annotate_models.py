"""
Django management command to annotate models with schema information.
"""

from pathlib import Path
import os

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from django_annotate.config import load_config
from django_annotate.db_introspect.factory import get_introspector
from django_annotate.parser import annotate_model_file

class Command(BaseCommand):
    help = 'Annotate Django models with schema information'

    def add_arguments(self, parser):
        parser.add_argument('--app', help='App to annotate models for (optional)')

    def handle(self, *args, **options):
        """Handle the command."""
        app_name = options.get('app')
        config = load_config()
        
        # Get list of apps to process
        if app_name:
            app_configs = [apps.get_app_config(app_name)]
            if app_configs[0] is None:
                raise LookupError(f'App "{app_name}" not found')
        else:
            # Get all installed apps, excluding ignored ones
            app_configs = [
                app_config for app_config in apps.get_app_configs()
                if app_config.label not in config.get('ignore_apps', [])
            ]

        # Get introspector
        introspector = get_introspector()

        # Process each app
        for app_config in app_configs:
            # Get models file
            models_file = os.path.join(app_config.path, 'models.py')
            if not os.path.exists(models_file):
                self.stdout.write(self.style.WARNING(f'No models.py found in {app_config.label}'))
                continue

            # Import the models module
            import importlib
            import sys
            app_dir = os.path.dirname(app_config.path)
            if app_dir not in sys.path:
                sys.path.insert(0, app_dir)
            try:
                # Use the full app name for importing to ensure correct module path
                models_module = importlib.import_module(f"{app_config.name}.models")
            except ImportError as e:
                self.stdout.write(self.style.ERROR(f'Failed to import models from {app_config.name}: {e}'))
                continue
            finally:
                if app_dir in sys.path:
                    sys.path.remove(app_dir)

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
            self.stdout.write(f'Annotating models in: {models_file}')
            try:
                with open(models_file, 'r+') as f:
                    content = annotate_model_file(models_file, schema_lookup, config=config)
                    f.seek(0)
                    f.write(content)
                    f.truncate()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error annotating models: {e}'))
                continue
