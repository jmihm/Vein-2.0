from __future__ import absolute_import

from celery import Celery

app = Celery('celery_tasks')
app.config_from_object('celery_tasks.celeryconfig')

if __name__ == '__main__':
    app.start()

