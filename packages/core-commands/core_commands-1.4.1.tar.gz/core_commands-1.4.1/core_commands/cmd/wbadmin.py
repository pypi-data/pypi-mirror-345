from ..bin.cmd import cmd

def wbadmin(arguments=None):
    return cmd(f"wbadmin {arguments}")