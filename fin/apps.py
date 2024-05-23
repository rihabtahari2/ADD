from django.apps import AppConfig

class FinConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fin'
    def ready(self):
        # Initialiser mongoengine
        from .mongo_setup import init_mongoengine
        init_mongoengine()