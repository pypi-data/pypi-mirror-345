from ..bin.cmd import cmd

def call(arguments=None):
    """
    Call one batch program from another, or call a subroutine.
    """
    return cmd("call",arguments) #pylint: disable=no-member