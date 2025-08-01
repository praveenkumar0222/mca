from django.apps import AppConfig

class ExamsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exams'
    
    def ready(self):
        # This ensures the template tags are loaded
        import exams.templatetags