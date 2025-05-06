from ..bin.cmd import cmd

def attrib(arguments = None):
    """
    Display or change file attributes.
    """
    return cmd('attrib',f"{arguments}")