from daemon import Daemon

class PostgresDaemon(Daemon.Daemon):

    def pid_file(self):
        return "./daemon/pids/postgres.pid"

    def output_file(self):
        return "./daemon/outputs/postgres.out"

    def base_command(self):
        return "postgres -D /usr/local/var/postgres"

    def strings_indicating_setup_complete(self):
        return ["database system is ready to accept connections"]