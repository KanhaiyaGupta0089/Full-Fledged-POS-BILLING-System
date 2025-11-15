from django.apps import AppConfig

class DaybookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'daybook'
    
    def ready(self):
        """Import signals when app is ready"""
        import daybook.signals  # noqa

