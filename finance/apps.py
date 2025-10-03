# finance/apps.py
from django.apps import AppConfig

class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'

    def ready(self):
        # import signals (safe import)
        try:
            import finance.signals  # noqa
        except Exception:
            # if signals fail, we don't want to crash startup — log in real app
            pass