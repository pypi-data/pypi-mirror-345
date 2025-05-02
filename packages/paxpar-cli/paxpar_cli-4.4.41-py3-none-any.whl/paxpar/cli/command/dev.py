import os

import typer
from paxpar.cli.tools import call, host_only, console, root_command_callback


app = typer.Typer(
    help="developement related commands",
    callback=root_command_callback(),
)


@app.command()
def all():
    """
    Start all paxpar services
    See .tmuxp.yaml for session details
    """
    call("""tmuxp load .""")


@app.command()
def debug_core():
    """
    Start paxpar core service for debugging
    """
    # host = host_only(os.environ["SVC_CORE_PROXY"])
    call(
        """
        python -m paxpar.services.core.main
    """,
        # --log-level debug
        # cwd="paxpar/services/core",
    )


@app.command()
def dev_dummymetric():
    """
    Start a dummy metric prometheus target
    """
    # TODO: add --reload !!!
    host = host_only(os.environ["SVC_CORE_PROXY"])
    call(
        f"""
        poetry run uvicorn paxpar.services.dummymetric.main:app \
            --host {host} \
            --port 8932 \
            --reload \
            --log-level debug
    """,
        cwd="services/core",
    )
