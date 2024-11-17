# scoringapp/scheduler.py

import threading
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from django.core.management import call_command
from .models import Competition, ScheduleLock

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

# Use SQLAlchemyJobStore with a separate SQLite3 database
scheduler.add_jobstore(
    SQLAlchemyJobStore(url='sqlite:///scheduler_db.sqlite3'),
    alias='scheduler_jobstore'
)

def start():
    if ScheduleLock.objects.all().filter(id=1).first().locked == False:
        logging.info('locked scheduler')
        schedule_lock = ScheduleLock.objects.all().filter(id=1).first()
        schedule_lock.locked = True
        schedule_lock.save()
        logger.info("Starting scheduler...")
        scheduler.add_job(
            check_all_services,
            trigger='interval',
            minutes=1,
            id='check_all_services',
            replace_existing=True,
            jobstore='scheduler_jobstore'
        )
        scheduler.start()
        logger.info("Scheduler started.")
    else:
        logger.warn('schedule locked, aborting!')

def check_all_services():
    if Competition.objects.all().filter(id=1).first().paused == False:
        logger.info("Executing check_all_services job...")
        try:
            call_command('checkall')
        except Exception as e:
            logger.exception(f"Error executing checkall command: {e}")
    else:
        logger.info("Aborting, comp is paused")
