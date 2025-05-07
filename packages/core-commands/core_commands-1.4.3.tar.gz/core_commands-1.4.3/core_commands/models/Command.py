from dataclasses import dataclass

@dataclass
class Command:
        output: str
        error: str
        command: str
        returncode: int
        process_identifier: int