from .shell import shell_open,no_shell,no_shell_open,shell_run

def cmd(command,mode="shell_open"):
    if mode == "shell_open":
        return shell_open(command)
    if mode == "no_shell":
        return no_shell(command)
    if mode == "no_shell_open":
        return no_shell_open(command)
    if mode == "shell_run":
        return shell_run(command)