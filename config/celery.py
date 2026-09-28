import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('mediconnect')

# namespace='CELERY' means all celery-related configuration keys
# should have a `CELERY_` prefix in settings.py.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django app packages.
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'daily-appointment-reminders': {
        'task': 'notifications.schedule_reminders_for_tomorrow',
        'schedule': crontab(hour=8, minute=0),  # Runs daily at 08:00 UTC
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Celery Debug Request: {self.request!r}')
