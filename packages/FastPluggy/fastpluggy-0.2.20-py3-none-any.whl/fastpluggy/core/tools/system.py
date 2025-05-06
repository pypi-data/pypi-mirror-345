import os
import signal

def restart_application():
    os.kill(os.getpid(), signal.SIGINT)

def restart_application_force():
    os.kill(os.getpid(), signal.SIGKILL)
