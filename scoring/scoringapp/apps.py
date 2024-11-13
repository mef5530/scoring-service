# scoringapp/apps.py

import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class ScoringappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scoringapp'

    def ready(self):
        logger.info("ScoringappConfig.ready() called.")
        from . import scheduler
        scheduler.start()
