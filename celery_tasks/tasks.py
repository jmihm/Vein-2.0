from __future__ import absolute_import
from celery_tasks.celery import app
from data_loading import LoaderSystem
from datetime import date, timedelta

import os

@app.task
def add(x, y):

    filepath = '/Users/chris/dummy'
    if os.path.isfile(filepath):
        f = open(filepath, 'r')
        res = int(f.read())
        f.close()
        f = open(filepath, 'w')
        f.write(str(res + 1))
        f.close()
        return res + 1
    else:
        f = open(filepath, 'w')
        f.write(str(1))
        f.close()
        return 1

@app.task
def populate_miso_tables():
    system = LoaderSystem.LoaderSystem()
    system.insert_accessible_unloaded_dates(earliest_date = date.today() - timedelta(days=90))
