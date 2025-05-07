from ..bin.cmd import cmd

def w32tm(arguments=None):
    return cmd(f"w32tm {arguments}")