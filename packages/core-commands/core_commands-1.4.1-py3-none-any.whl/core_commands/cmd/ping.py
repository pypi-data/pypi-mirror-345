from ..bin.cmd import cmd

def ping(arguments=None):
    return cmd(f"ping {arguments}")