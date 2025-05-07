from ..bin.cmd import cmd

def echo(text = False):
    """
    Display messages on screen, turn command-echoing on or off.

    arguments: ON | OFF | /?
    """
    arguments=text
    return cmd("echo",arguments)