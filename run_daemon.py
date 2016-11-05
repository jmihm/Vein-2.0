from daemon import CeleryBeatDaemon, CeleryWorkerDaemon, rabbitmq

from sys import argv

celerybeat = CeleryBeatDaemon.CeleryBeatDaemon()
celeryworker = CeleryWorkerDaemon.CeleryWorkerDaemon()

if argv[1] == 'restart':
    rabbitmq.restart_rabbitmq()
    celeryworker.restart('-A celery_tasks')
    celerybeat.restart('-A celery_tasks')
elif argv[1] == 'stop':
    rabbitmq.shutdown_rabbitmq()
    celeryworker.stop()
    celerybeat.stop()
else:
    print 'Valid commands are restart and stop.'