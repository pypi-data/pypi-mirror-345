import os
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
from pathlib import Path

from django_annotate.parser import annotate_model_file
from django_annotate.db_introspect import get_schema_for_model
from django_annotate.config import load_config

@receiver(post_migrate)
def auto_annotate_after_migrate(sender, **kwargs):
    config = load_config()
    
    # Check if we should skip annotation
    if config["skip_on_migrate"]:
        return
        
    # Safety check: don't run in production
    if getattr(settings, 'DJANGO_ANNOTATE_DISABLE_AUTO', False):
        return
        
    # Additional safety: don't run if DEBUG is False (production)
    if not getattr(settings, 'DEBUG', False):
        return

    # Get all installed apps
    app_configs = apps.get_app_configs()

    for app in app_configs:
        # Skip ignored apps
        if app.label in config["ignore_apps"]:
            continue

        models_file = Path(app.path) / "models.py"
        if not models_file.exists():
            continue

        annotate_model_file(
            str(models_file),
            lambda model_name: get_schema_for_model(apps.get_model(app.label, model_name)),
            config=config
        ) 