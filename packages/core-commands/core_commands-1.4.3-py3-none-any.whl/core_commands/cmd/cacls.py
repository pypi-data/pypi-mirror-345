from ..bin.cmd import cmd

def cacls(arguments = None):
    return cmd("cacls",f"{arguments}")