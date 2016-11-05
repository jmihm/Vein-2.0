from __future__ import absolute_import
from datetime import timedelta
from celery.schedules import crontab
from daemon import CeleryBeatDaemon, CeleryWorkerDaemon

BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp://'
CELERY_IMPORTS = ('celery_tasks.tasks',)

CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'celery_tasks.tasks.add',
        'schedule': timedelta(seconds=2),
        'args': (16, 16)
    },
    'populate_tables': {
        'task': 'celery_tasks.tasks.populate_miso_tables',
        'schedule': crontab(minute=0, hour=0)
    }
}

CELERY_TIMEZONE = 'EST'

# TODO I couldnt find a good solution in celery for killing off tasks. One possible idea
# TODO is to have the tasks on a given queue and to try to kill the queue from rabbit rather than shutting
# TODO everything down.
def on_failure(self, exc, task_id, args, kwargs, einfo):
    # TODO log the error somewhere.
    beat = CeleryBeatDaemon.CeleryBeatDaemon()
    worker = CeleryWorkerDaemon.CeleryWorkerDaemon()
    beat.stop()
    worker.stop()

CELERY_ANNOTATIONS = {
    '*' : {'on_failure': on_failure}
}
