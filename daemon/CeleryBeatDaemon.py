from daemon import Daemon

class CeleryBeatDaemon(Daemon.Daemon):

    def pid_file(self):
        return "./daemon/pids/celerybeat.pid"

    def output_file(self):
        return "./daemon/outputs/celerybeat.out"

    def base_command(self):
        return "celery beat"

    def strings_indicating_setup_complete(self):
        return ['beat: Starting...']
