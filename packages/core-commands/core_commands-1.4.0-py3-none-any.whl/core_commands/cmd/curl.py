from ..bin.cmd import cmd

def curl(opciones,url):
    """
    Transfer data from or to a server, using one of the supported protocols (HTTP, HTTPS, FTP, FTPS, SCP, SFTP, TFTP, DICT, TELNET, LDAP or FILE). 
    """
    arguments = f"{opciones} {url}"
    return cmd("curl",arguments)