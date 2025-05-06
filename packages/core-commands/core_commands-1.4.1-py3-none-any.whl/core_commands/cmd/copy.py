from ..bin.cmd import cmd

def copy(source = "",destination = "",sourceArguments = "",destinationArguments = ""):
    arguments = f"{source} {sourceArguments} {destination} {destinationArguments}"
    return cmd("copy",arguments)