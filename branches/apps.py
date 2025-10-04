# branches/apps.py
from django.apps import AppConfig

class BranchesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'branches'

    def ready(self):
        # import signals so they are registered
        try:
            import branches.signals  # noqa
        except Exception:
            pass