import os
import signal
from typing import Annotated


from fastpluggy.core.tools.inspect_tools import InjectDependency
from fastpluggy.fastpluggy import FastPluggy


def restart_application(fast_pluggy: Annotated[FastPluggy,InjectDependency]):
    #fast_pluggy.executor.shutdown()
    os.kill(os.getpid(), signal.SIGINT)


def restart_application_force(fast_pluggy: Annotated[FastPluggy,InjectDependency]):
    #fast_pluggy.executor.shutdown(wait=False)
    os.kill(os.getpid(), signal.SIGKILL)

