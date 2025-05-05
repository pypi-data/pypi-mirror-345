import inspect

from rich.console import Console

console = Console()


def loc_print(message):
    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    console.print(f"[bold green]{filename}:{lineno}[/bold green] {message}")
