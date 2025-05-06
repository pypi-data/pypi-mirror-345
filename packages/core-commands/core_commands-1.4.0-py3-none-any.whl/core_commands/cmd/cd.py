from ..bin.cmd import cmd

def cd(arguments=None):
    """
    Change Directory - Select a Folder (and drive)
    """
    return cmd("cd",f'{arguments}')  # type: ignore