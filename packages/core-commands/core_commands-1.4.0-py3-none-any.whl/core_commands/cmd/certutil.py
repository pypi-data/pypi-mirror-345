from ..bin.cmd import cmd

def certutil(arguments = None):
     return cmd("certutil",f'{arguments}')