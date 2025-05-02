import typer
from rich.console import Console


console = Console()

app = typer.Typer(help="Misc pp commands")



@app.command()
def debugpy():
    """
    Start debugpy ... (NOT IMPLEMENTED)
    """
    # TODO:
    # python -m debugpy --listen 5678 --wait-for-client scripts/cli/pp.py ref refresh
    ...


