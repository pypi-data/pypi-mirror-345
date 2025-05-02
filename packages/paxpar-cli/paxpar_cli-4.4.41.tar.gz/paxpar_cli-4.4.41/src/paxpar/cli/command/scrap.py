from pathlib import Path

import typer
from rich.console import Console
from paxpar.cli.tools import cli_coro


# Conditionnal import
try:
    from paxpar.services.core.ref.stores import DEFAULT_STORE_ID
    from paxpar.services.shared.scrap import lib

    MODULE_ENABLED = True
except ModuleNotFoundError:
    MODULE_ENABLED = False


console = Console()

app = typer.Typer(
    name="pp scrap", add_completion=False, help="pp scrap related commands"
)

if MODULE_ENABLED:

    @app.command()
    def build(
        definition: Path = Path("scrap.yaml"),
        dest: Path = Path("scrap"),
        only: str = "*",
        prune: bool = False,
        mode: str = "cut",
        sign: bool = False,
        store: str = DEFAULT_STORE_ID,
        subst: bool = False,
        statfile: str = "stats.xlsx",
    ):
        """Scrap a document from its definition"""

        @cli_coro()
        async def do_async():
            await lib.scrap(
                definition=definition,
                dest=dest,
                only=only,
                prune=prune,
                mode=mode,
                sign=sign,
                subst=subst,
                store_id=store,
                statfile=statfile,
                stats=lib.Stats(),
            )

        do_async()

    @app.command()
    def init(
        pdf: Path,
    ):
        """Create a new scram definition from a PDF file"""
        raise NotImplementedError()

    @app.command()
    def analyse(
        definition: Path = Path("scrap.yaml"),
    ):
        """Analyse an existings scrap to show PDF sources, coverage, template usage, ..."""
        # TODO:- List all origin PDF
        # TODO:- Show origin PDF with no full range page coverage
        # TODO:- Show origin PDF with range page overlapping
        # TODO:- Show origin PDF without template
        # TODO:- Show PDF without data attached
        # TODO:- Show PDF without schema
        # TODO:- Show PDF without signatures
        # TODO:- Show PDF without checklist
        # TODO:- Show PDF without craftform

        raise NotImplementedError()


else:
    console.print(f"CLI module {__name__} disabled", style="red")
