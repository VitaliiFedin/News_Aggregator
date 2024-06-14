import os

import eventlet
from celery import Celery
from celery.schedules import crontab

# eventlet.monkey_patch()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_aggregator.settings")

app = Celery("news_aggregator")
app.config_from_object("django.conf:settings", namespace="CELERY")


app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


app.conf.beat_schedule = {
    "run-every-min": {
        "task": "sentiment-task",
        "schedule": crontab(minute="*"),
    },
}
