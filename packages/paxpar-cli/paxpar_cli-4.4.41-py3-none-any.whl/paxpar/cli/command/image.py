import os
from typing import Annotated, Any, Literal
from paxpar.cli.command.version import version_get
import typer
from rich.console import Console

from paxpar.cli.tools import PaxparCLI_ObjCtx, call, root_command_callback

console = Console()

app = typer.Typer(
    help="container image related commands",
    callback=root_command_callback(),
)


REGISTRIES = {
    "gitea": {
        "url": "gitea.arundo.tech",
    },
    "gitlab": {
        "url": "registry.gitlab.com",
    },
    "scaleway": {
        "url": "rg.fr-par.scw.cloud/pp-registry-test1",
    },
    "scaleway-public": {
        "url": "rg.fr-par.scw.cloud/pp-registry-public",
        "secret_env_var": "SCALEWAY_SECRET_KEY",
    },
}

@app.command("list")
def list_command():
    """
    List image registries
    """
    print(REGISTRIES)


@app.command()
def login(
    ctx: typer.Context,
    registry_id: str = "all",
):
    """
    Login to image registry
    """
    registries = list(REGISTRIES.keys()) if registry_id == "all" else [registry_id]

    for registry_id in registries:
        registry = REGISTRIES[registry_id]
        envv = registry.get('secret_env_var') or f"{registry_id.upper()}_SECRET_KEY"
        secret = os.environ[envv]
        cmd = f'''podman login {registry["url"]} -u nologin -p "{secret}"'''

        call(cmd, ctx_obj=ctx.obj)


#ImageType = Literal['base', 'core']
ImageType = str
images_conf : dict[ImageType, dict[str, Any]] = {
    'base': {
        'registry': 'scaleway-public',
        'context' : 'packages/pp-base',
        'name': 'pp-base',
    },
    'core': {
        'registry': 'scaleway',
        'context' : '.',
        'name': 'pp-core',
    },
}

@app.command()
def build(
    ctx: typer.Context,
    image_publish: bool = True,
    registry: str = "",

    image: Annotated[ImageType, typer.Argument()] = "core",
    version: Annotated[str | None, typer.Argument()] = None,

):
    """
    Build paxpar images
    """
    ctx_obj: PaxparCLI_ObjCtx = ctx.obj

    if version is None:
        version = version_get(ctx_obj)
        if ctx_obj.verbose:
            print(f"No version specified, assuming {version}")

    image_conf = images_conf[image]
    registry_id = registry if len(registry) > 0 else image_conf['registry']
    registry_conf = REGISTRIES[registry_id]
    image_fullname = f"{registry_conf['url']}/{image_conf['name']}:{version}"

    if image_publish:
        login(ctx, registry_id)

    call(
        f'''podman build -t "{image_fullname}" {image_conf['context']}''',
        ctx_obj=ctx_obj,
    )
    
    if image_publish:
        call(
            f'podman push "{image_fullname}"',
            ctx_obj=ctx_obj,
        )

@app.command()
def pull(
    ctx: typer.Context,
    version: str = "latest",
):
    """
    Pull paxpar core image
    """
    registry = REGISTRIES["gitlab"]
    if version[0].isdigit():
        version = f"v{version}"

    call(
        f"""podman pull {registry["url"]}/arundo-tech/paxpar/paxpar-core:{version}""",
        ctx_obj=ctx.obj,
    )


@app.command()
def run(
    ctx: typer.Context,
):
    """
    Run default python image
    """

    call(
        """
        podman run \
            -t -i --rm \
            -v $PWD:/builds/arundo-tech/paxpar \
            -w /builds/arundo-tech/paxpar \
            --entrypoint /bin/bash \
            python:3.13
        """,
        ctx_obj=ctx.obj,
    )
