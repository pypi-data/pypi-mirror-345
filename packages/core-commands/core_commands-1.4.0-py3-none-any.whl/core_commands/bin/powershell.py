from subprocess import run
from .shell_run import shell
from ._validate import _validateArguments

def powershell(command,arguments):
        full_command=None
        if _validateArguments(arguments):
                full_command = f"{command} {arguments}"
                return shell(["powershell", "-Command", full_command],arguments)
        full_command = command