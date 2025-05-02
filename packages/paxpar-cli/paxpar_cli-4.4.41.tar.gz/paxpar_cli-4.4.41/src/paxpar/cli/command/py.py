import typer
from paxpar.cli.tools import call, root_command_callback, console


app = typer.Typer(
    help="Python related pp commands",
    callback=root_command_callback(),
)


@app.command()
def api(ctx: typer.Context):
    """
    Run python from pp-api package
    """
    call(
        """uv run python""",
        cwd="packages/pp-api",
        ctx_obj=ctx.obj,
    )


@app.command()
def cli(ctx: typer.Context):
    """
    Run python from pp-api package
    """
    call(
        """uv run python""",
        cwd="packages/pp-api",
        ctx_obj=ctx.obj,
    )
