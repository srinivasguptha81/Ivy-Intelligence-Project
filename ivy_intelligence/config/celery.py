import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('ivy_intelligence')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic task schedule
from celery.schedules import crontab

app.conf.beat_schedule = {
    'scrape-opportunities-every-6-hours': {
        'task': 'apps.opportunities.tasks.scrape_all_universities',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    'recalculate-incoscores-daily': {
        'task': 'apps.incoscore.tasks.recalculate_all_scores',
        'schedule': crontab(minute=0, hour=2),  # 2 AM daily
    },
}
