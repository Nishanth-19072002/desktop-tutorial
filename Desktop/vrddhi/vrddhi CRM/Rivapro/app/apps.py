from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

class AppConfig(AppConfig):
    name = 'app'

    def ready(self):
        import app.signals  # Import the signals to connect the signal handlers
