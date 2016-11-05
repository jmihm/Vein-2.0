import os, subprocess, time, signal


def pid_exists(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def kill_and_wait(pid, signal, timeout_seconds):
    os.kill(pid, signal)
    #pexpect.spawn('kill -%s %s' % (pid, signal)).wait()
    total_time = 0
    while pid_exists(pid):
        if total_time >= timeout_seconds:
            raise Exception('Timed out trying to kill pid: %s' % pid)
        time.sleep(0.1)
        total_time += 0.1;