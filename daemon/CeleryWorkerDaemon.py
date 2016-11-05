from daemon import Daemon

class CeleryWorkerDaemon(Daemon.Daemon):

    def pid_file(self):
        return "./daemon/pids/celeryworker.pid"

    def output_file(self):
        return "./daemon/outputs/celeryworker.out"

    def base_command(self):
        return "celery worker"

    def strings_indicating_setup_complete(self):
        return ['ready.']
