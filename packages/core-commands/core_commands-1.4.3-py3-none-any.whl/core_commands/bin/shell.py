from subprocess import run,Popen,PIPE
from ..models.Command import Command
from sys import stdin,stderr
from threading import Thread

#TODO: crear un validador para command, 
#   1 verifica el tipo, puede ser string y lista,
#   2 verifica que no este vacio|None tanto la string como la lista 

def shell_run(command):
    process = run(command,
                    capture_output=True,
                    text=True,
                    shell=True
                    )
    result = Command(
        output=process.stdout,
        error=process.stderr,
        command=process.args,
        returncode=process.returncode,
        process_identifier=0
    )
    return result

def shell_open(command):
    # Inicia el proceso hijo
    process = Popen(
        command,
        stdin=stdin,          # Permite interacción desde el teclado
        stdout=PIPE,   # Captura stdout
        stderr=PIPE,   # Captura stderr
        text=True,                # Trabaja con texto (no bytes)
        bufsize=1,                # Buffering línea por línea
        shell=True
    )
    
    # Variables para almacenar output
    stdout_lines = []
    stderr_lines = []

    # ---- Función anidada 1: Para imprimir stdout en vivo ----
    def print_stdout():
        for line in process.stdout:   # type: ignore # Lee línea por línea del pipe
            print(line, end="")    # Muestra en tiempo real
            stdout_lines.append(line)

    # ---- Función anidada 2: Para imprimir stderr en vivo ----
    def print_stderr():
        for line in process.stderr:   # Lee línea por línea del pipe #type: ignore
            print(line, end="", file=stderr)  # Muestra errores en stderr
            stderr_lines.append(line)

    # ---- Inicia hilos para leer stdout y stderr sin bloquear ----
    stdout_thread = Thread(target=print_stdout)
    stderr_thread = Thread(target=print_stderr)
    
    stdout_thread.start()
    stderr_thread.start()

    # Espera a que el proceso termine
    process.wait()
    
    # muestra lo que quedo de la salida y de los errores.
    stdout_thread.join()
    stderr_thread.join()
    
    result = Command(
        output="".join(stdout_lines),
        error="".join(stderr_lines),
        command=command if isinstance(command, str) else " ".join(command),
        returncode=process.returncode,
        process_identifier=process.pid
        )
    
    return result

def no_shell_open(command: str|list):
    # Inicia el proceso hijo
    process = Popen(
        command,
        stdin=stdin,          # Permite interacción desde el teclado
        stdout=PIPE,   # Captura stdout
        stderr=PIPE,   # Captura stderr
        text=True,                # Trabaja con texto (no bytes)
        bufsize=1                # Buffering línea por línea
    )
    
    # Variables para almacenar output
    stdout_lines = []
    stderr_lines = []

    # ---- Función anidada 1: Para imprimir stdout en vivo ----
    def print_stdout():
        for line in process.stdout:   # type: ignore # Lee línea por línea del pipe
            print(line, end="")    # Muestra en tiempo real
            stdout_lines.append(line)

    # ---- Función anidada 2: Para imprimir stderr en vivo ----
    def print_stderr():
        for line in process.stderr:   # Lee línea por línea del pipe #type: ignore
            print(line, end="", file=stderr)  # Muestra errores en stderr
            stderr_lines.append(line)

    # ---- Inicia hilos para leer stdout y stderr sin bloquear ----
    stdout_thread = Thread(target=print_stdout)
    stderr_thread = Thread(target=print_stderr)
    
    stdout_thread.start()
    stderr_thread.start()

    # Espera a que el proceso termine
    process.wait()
    
    # muestra lo que quedo de la salida y de los errores.
    stdout_thread.join()
    stderr_thread.join()
    
    result = Command(
        output="".join(stdout_lines),
        error="".join(stderr_lines),
        command=command if isinstance(command, str) else " ".join(command),
        returncode=process.returncode,
        process_identifier=process.pid
        )
    
    return result
    
def no_shell(command: str|list):
    process = run(command,
                    capture_output=True,
                    text=True
                    )
    
    result = Command(
        output=process.stdout,
        error=process.stderr,
        command=process.args,
        returncode=process.returncode,
        process_identifier=0
    )
    
    return result