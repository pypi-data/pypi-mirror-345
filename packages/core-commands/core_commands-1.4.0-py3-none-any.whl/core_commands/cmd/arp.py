from ..bin.cmd import cmd

def arp(arguments = None):
    command = [
        "arp",
        arguments
    ]
    return cmd(command)