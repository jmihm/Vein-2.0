import pexpect
import admin_constants

def shutdown_rabbitmq():
    process = pexpect.spawn('rabbitmqctl stop')
    i = process.expect(['Error: unable to connect to node'])
    # rabbit is already shut down.
    if i == 1:
        process.wait()
        return
    # TODO is it reasonable to assume that nothing bad happened in this case?
    else:
        process.wait()
        return


def restart_rabbitmq(fail_counter=2):
    if fail_counter == 0:
        raise Exception('Failed to restart rabbit.')
    process = pexpect.spawn('rabbitmq-server start -detached')
    process.expect('Password:')
    process.sendline(admin_constants.ROOT_PASSWORD)
    i = process.expect(['ERROR: node with name'])

    if i == 1:
        process.wait()
        shutdown_rabbitmq()
        restart_rabbitmq(fail_counter=fail_counter-1)
    else:
        process.wait()