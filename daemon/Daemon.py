import time, os, subprocess, signal
from datetime import datetime

from daemon import process_tools


class Daemon(object):

    def pid_file(self):
        raise NotImplemented

    def output_file(self):
        raise NotImplemented

    def base_command(self):
        raise NotImplemented

    def strings_indicating_setup_complete(self):
        raise NotImplemented

    def stop(self, timeout_seconds=10):
        if os.path.isfile(self.pid_file()):
            pid = None
            with open(self.pid_file(), 'r') as f:
                pid = int(f.readline())
            if not process_tools.pid_exists(pid):
                os.remove(self.pid_file())
            else:
                process_tools.kill_and_wait(pid, signal.SIGINT, timeout_seconds)
                os.remove(self.pid_file())


    def get_modified_files(self, path_list, last_datetime):
        return [path for path in path_list if datetime.fromtimestamp(os.path.getmtime(path)) > last_datetime]


    def is_setup_complete(self):
        with open(self.output_file(), 'r') as f:
            data = f.read()
            return all(s in data for s in self.strings_indicating_setup_complete())


    def restart(self, arg_list, timeout_seconds=10):
        # kill any existing daemon.
        self.stop(self.pid_file())
        # clear the output and error logs.
        with open(self.output_file(), 'w') as f:
            pass
        with open(self.pid_file(), 'w') as f:
            pass

        # construct the command to run the task as a daemon
        arg_string = ' '.join(arg_list)
        # TODO separate stdout and stderr
        command = 'nohup %s %s > %s 2> %s & echo $! > %s' % (
            self.base_command(), arg_string, self.output_file(), self.output_file(), self.pid_file())
        subprocess.check_call(command, shell=True)
        pid = None
        with open(self.pid_file(), 'r') as f:
            pid = int(f.readline())
        # monitor the output file until the daemon set up is complete, then return control to the user.
        total_time = 0
        last_datetime = datetime.now()

        setup_complete = False
        while setup_complete:
            if total_time > timeout_seconds:
                raise Exception('Timed out restarting process pid: %s. Check output logs at %s' % (pid, self.output_file()))

            modified_files = self.get_modified_files([self.output_file()], last_datetime)
            last_datetime = datetime.now()
            for m in modified_files:
                if m == self.output_file():
                    if self.is_setup_complete():
                        setup_complete = True

            time.sleep(0.1)
            total_time += 0.1






