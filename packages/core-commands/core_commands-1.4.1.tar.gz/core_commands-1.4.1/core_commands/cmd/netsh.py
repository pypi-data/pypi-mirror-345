from ..bin.cmd import cmd

def netsh(arguments=None):
    return cmd("netsh",arguments)