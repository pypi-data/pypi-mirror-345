from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from pathlib import Path

from django_annotate.parser import annotate_model_file
from django_annotate.db_introspect import get_schema_for_model
from django_annotate.config import load_config

class Command(BaseCommand):
    help = "Annotate Django model files with schema information (fields, indexes, foreign keys)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--app",
            type=str,
            help="Specify a single app to annotate (optional)",
        )

    def handle(self, *args, **options):
        config = load_config()
        app_label = options["app"]

        if app_label:
            try:
                app_configs = [apps.get_app_config(app_label)]
            except LookupError:
                raise CommandError(f"App '{app_label}' could not be found")
        else:
            app_configs = apps.get_app_configs()

        for app in app_configs:
            # Skip ignored apps
            if app.label in config["ignore_apps"]:
                self.stdout.write(self.style.NOTICE(f"Skipping ignored app: {app.label}"))
                continue

            models_file = Path(app.path) / "models.py"
            if not models_file.exists():
                self.stdout.write(self.style.NOTICE(f"Skipping: {models_file} not found"))
                continue

            self.stdout.write(f"Annotating models in: {models_file}")
            annotate_model_file(
                str(models_file),
                lambda model_name: get_schema_for_model(apps.get_model(app.label, model_name)),
                config=config
            )
