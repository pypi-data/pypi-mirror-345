from ..bin.cmd import cmd

def bcdedit(arguments = None):
    return cmd('bcdedit',f"{arguments}")