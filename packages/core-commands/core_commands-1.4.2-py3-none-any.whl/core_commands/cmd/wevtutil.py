from ..bin.cmd import cmd

def wevtutil(arguments=None):
    return cmd(f"wevtutil {arguments}")