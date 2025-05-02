import typer
from typing import Annotated, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from paxpar.cli.tools import cli_coro, root_command_callback

import yaml

from paxpar.shared.conf import (
        Conf,
        get_conf_payload,
        get_envars_keys,
        load_single,
    )


## Conditionnal import
#try:
#    from paxpar.services.core.ref.base import ObjectRefBase
#    from paxpar.services.core.ref.refcontext import RefContext
#    from paxpar.services.core.ref.source import RefException
#
#    MODULE_ENABLED = True
#except ModuleNotFoundError:
#    MODULE_ENABLED = False


console = Console()

app = typer.Typer(
    name="pp conf",
    help="pp conf related commands",
    callback=root_command_callback(),    
)


#if MODULE_ENABLED:

@app.command()
def show(
    validate: bool = True,
    conf_file: list[str] = [],
    envvars: bool = True,

):
    """
    Show paxpar conf
    """

    conf_payload = get_conf_payload(
        conf_files = conf_file,
        use_envvars=envvars,
    )

    if validate:
        conf = Conf.model_validate(conf_payload)

    print(yaml.dump(conf_payload, indent=2))

@app.command()
def env(
    no_expand: bool = False,
):
    """
    Show env var conf
    """
    conf_vars = get_envars_keys(expand=not no_expand)
    if len(conf_vars) == 0:
        print("paxpar no env vars found !")
    else:
        print("paxpar env vars:")

        for k, v in conf_vars.items():
            print(f"{k}={v}")

@app.command()
def single(
    #url: Annotated[Optional[str], typer.Argument(default=None)],
):
    """
    Load conf from a single endpoint
    """
    if url:
        conf_payload = load_single(url)
        print(yaml.dump(conf_payload, indent=2))

#else:
#    console.print(f"CLI module {__name__} disabled", style="red")
