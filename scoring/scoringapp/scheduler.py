# scoringapp/scheduler.py

import threading
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from django.core.management import call_command

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

# Use SQLAlchemyJobStore with a separate SQLite3 database
scheduler.add_jobstore(
    SQLAlchemyJobStore(url='sqlite:///scheduler_db.sqlite3'),
    alias='scheduler_jobstore'
)

scheduler_started = False
scheduler_lock = threading.Lock()

def start():
    global scheduler_started
    with scheduler_lock:
        if not scheduler_started:
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
            scheduler_started = True
            logger.info("Scheduler started.")

def check_all_services():
    logger.info("Executing check_all_services job...")
    try:
        call_command('checkall')
    except Exception as e:
        logger.exception(f"Error executing checkall command: {e}")
