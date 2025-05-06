if __name__ == "__main__":
    from core_commands.bin.baxh import baxh
else:
    from ..bin.cmd import cmd
from pathlib import PurePath

def mkdir(arguments=None):
    return cmd('mkdir',arguments)
