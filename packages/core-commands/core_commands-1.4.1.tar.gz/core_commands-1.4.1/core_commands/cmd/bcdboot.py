from ..bin.cmd import cmd

# TODO: este comando es mas profundo

def bcdboot(arguments = None):
    return cmd(f"bcdboot",f"{arguments}")