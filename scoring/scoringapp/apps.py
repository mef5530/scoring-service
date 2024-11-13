from django.apps import AppConfig


class ScoringappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scoringapp'
    
    #def ready(self):
    #    from . import scheduler
    #    scheduler.start()
