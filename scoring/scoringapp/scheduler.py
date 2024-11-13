from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings
from .management.commands.check_services import Command

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    scheduler.add_job(
        Command().handle,
        'interval',
        seconds=30,
        name='checks',
        jobstore='default',
        replace_existing=True
    )

    scheduler.start()