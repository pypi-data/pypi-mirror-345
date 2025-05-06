from django.apps import AppConfig

class DjangoAnnotateConfig(AppConfig):
    name = 'django_annotate'
    verbose_name = 'Django Annotate'

    def ready(self):
        import django_annotate.signals  # noqa 
