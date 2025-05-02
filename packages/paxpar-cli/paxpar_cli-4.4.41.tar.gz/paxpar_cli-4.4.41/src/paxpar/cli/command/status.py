from typing import Callable
import typer
from rich.console import Console
from paxpar.cli.tools import (
    call,
    call_json,
    root_command_callback,
)


console = Console()

def root_command(
    ctx: typer.Context,
):
    print("paxpar status (NOT IMPLEMENTED) ...")


app = typer.Typer(
    help="Show pp status",
    invoke_without_command=True,
    callback=root_command_callback(root_command),
)


@app.command()
def main(
    ctx: typer.Context,
):
    """basic status (DEFAULT)"""
    root_command(ctx)


@app.command()
def graph():
    """
    Show paxpar status as a graph
    """

    print("scaleway instances ...")
    sw_containers = call_json("""scw container container list -o json""")
    """
      - id: 30a89147-362d-44aa-a961-7f3a158dbab9
        name: paxpar-core-2c48f2d6
        namespaceid: 8080c26f-515c-40c7-b388-fb168520207c
        status: ready
        environmentvariables:
            PP_CONF_1: s3://ppadmin:minioh76zKE7DVpEQRGrd@ppref.arundo.tech:9000/pp-ref-common/_sys/conf/single.yaml
        minscale: 0
        maxscale: 5
        memorylimit: 3072
        cpulimit: 1000
        timeout:
            seconds: 300
            nanos: 0
        errormessage: null
        privacy: public
        description: ""
        registryimage: rg.fr-par.scw.cloud/pp-registry-test1/paxpar-core:0a82971c
        maxconcurrency: 80
        domainname: ppdev9acq2zcp-paxpar-core-2c48f2d6.functions.fnc.fr-par.scw.cloud
        protocol: http1
        port: 8881
        secretenvironmentvariables: []
        httpoption: enabled
        sandbox: v2
        localstoragelimit: 5703
        scalingoption:
            concurrentrequeststhreshold: 80
            cpuusagethreshold: null
            memoryusagethreshold: null
        healthcheck:
            http: null
            tcp: {}
            failurethreshold: 30
            interval:
                seconds: 10
                nanos: 0
        createdat: 2025-02-13T15:16:30.471394Z
        updatedat: 2025-02-14T09:19:30.823079Z
        readyat: 2025-02-14T09:19:30.81315Z
        region: fr-par

    """
    print(sw_containers)

    print("TODO: cloudflare instances ...")
    print("TODO: gitlab instances ...")
    print("TODO: arundo.tech instances ...")


@app.command()
def deps():
    """
    Show dependency graph
    """

    def _do_pydep(service: str):
        """
        poetry run pydeps ../core \
            -o ../../services/docs/docs/dev/deps/core_ref.svg \
            --exclude *test_* *tests* *module* \
            --rmprefix services. \
            --only services \
            --noshow
        """
        call(
            f"""
            poetry run pydeps ../{service} \
                -o ../../../services/docs/docs_dev/deps/deps_{service}.svg \
                --exclude *test_* *tests* *module* \
                --rmprefix services. \
                --only services \
                --noshow
        """,
            cwd="paxpar/services/core",
        )

    _do_pydep("auth")
    _do_pydep("core")
    _do_pydep("docs")
    _do_pydep("forge")
    _do_pydep("perm")