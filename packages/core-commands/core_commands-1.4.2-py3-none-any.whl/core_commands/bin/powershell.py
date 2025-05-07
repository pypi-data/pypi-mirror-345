from subprocess import run
from .shell import shell_open,no_shell,no_shell_open,shell_run


def powershell(command):
        
        return shell(["powershell", "-Command", full_command],arguments)
        