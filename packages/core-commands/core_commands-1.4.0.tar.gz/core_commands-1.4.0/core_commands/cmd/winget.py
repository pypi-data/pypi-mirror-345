from ..bin.cmd import cmd

def winget(arguments=None):
    return cmd(f"winget",arguments)