from ..bin.cmd import cmd

def auditpol(arguments = None):
    return cmd(f"auditpol",f"{arguments}")   # auditpol.exe