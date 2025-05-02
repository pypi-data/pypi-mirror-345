from django.apps import AppConfig


class DjangoCkeditor5Config(AppConfig):
    name = "hs_django_ckeditor"
    verbose_name = "Django CkEditor"

    def ready(self):
        from . import signals  # noqa: F401
