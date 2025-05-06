from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Annotated, Callable
from rich.table import Table
import typer
from rich.console import Console
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from paxpar.cli.tools import (
    PaxparCLI_ObjCtx,
    call,
    root_command_callback,
    call_text_output,
)

console = Console()

app = typer.Typer(
    help="Setup/clean pp env",
    callback=root_command_callback(),
)


# cf https://peps.python.org/pep-0440/#version-specifiers
SPEC_SPECIAL_CHARS = "~=!<>"


# ~=: Compatible release clause
# ==: Version matching clause
# !=: Version exclusion clause
# <=, >=: Inclusive ordered comparison clause
# <, >: Exclusive ordered comparison clause
# ===: Arbitrary equality clause
def _version_strip(version: str | None) -> str:
    if version:
        for char in SPEC_SPECIAL_CHARS:
            version = version.replace(char, "")
    return version or ""


@dataclass
class SetupTool:
    name: str
    version: str | None = None
    checked_version: str | None = None
    # version_get: Callable[[], str | None]
    # install: Callable[[], None]
    version_get: str | None = None
    install: str | None = None

    # @abstractmethod
    # def install(self): ...

    # @abstractmethod
    # def version_get(self) -> str | None: ...

    def _current_version_extract(
        self,
        ctx_obj: PaxparCLI_ObjCtx,
    ) -> str:
        if self.version_get is None:
            return "0.0.0"
        try:
            version_current = call_text_output(
                self.version_get,
                ctx_obj=ctx_obj,
            )
        except subprocess.CalledProcessError:
            return "0.0.0"
        # print('version_current====', version_current)
        match = re.search(r"(\d+\.\d+\.\d+)", version_current)
        self.checked_version = match.group(0) if match else "0.0.0"
        return self.checked_version

    # see https://packaging.pypa.io/en/stable/specifiers.html#usage
    def _version_valid(
        self,
        version: str | None,
    ) -> bool:
        if self.version:
            if self.version[0] in SPEC_SPECIAL_CHARS:
                v = Version(version)
                v_spec = SpecifierSet(self.version or "0.0.0")
                return v in v_spec
            else:
                return self.version in version
        else:
            return True

    def setup(
        self,
        ctx_obj: PaxparCLI_ObjCtx,
        silent: bool = False,
    ):
        ctx_obj.verbose = False if silent else ctx_obj.verbose
        version_current = self._current_version_extract(ctx_obj=ctx_obj)
        # if version_current is None:
        if not self._version_valid(version_current) and self.install:
            if ctx_obj.verbose:
                print(f"Installing {self.name}{self.version} ...")
            call(
                # run install snippet from /tmp
                f"""
                    pushd /tmp
                    {self.install.format(version=_version_strip(self.version))}
                    popd
                """,
                dry_run=ctx_obj.dry_run,
                verbose=False if silent else ctx_obj.verbose,
                executable="/bin/bash",
            )
            version_current = self._current_version_extract(ctx_obj=ctx_obj)

    def check(
        self,
        ctx_obj: PaxparCLI_ObjCtx,
    ) -> bool:
        version_current = self._current_version_extract(ctx_obj=ctx_obj)
        valid = self._version_valid(version_current)
        if ctx_obj.verbose:
            if valid:
                print(f"{self.name}{self.version} ok (found {version_current})")
            else:
                print(f"{self.name}{self.version} not found ! (found {version_current})")
        return valid


tools: list[SetupTool] = [
    SetupTool(
        name="bun",
        version=">=1.2.11",
        install="""
            curl -fsSL https://bun.sh/install | bash -s "bun-v{version}"
            sudo mv ~/.bun/bin/bun* /usr/local/bin/
        """,
        version_get="""bun --version""",
    ),
    SetupTool(
        name="helm",
        version="==3.17.2",
        install="""
            wget --quiet -nv https://get.helm.sh/helm-v{version}-linux-amd64.tar.gz
            tar -xf helm-*.tar.gz
            sudo mv linux-amd64/helm /usr/local/bin/helm
            rm -R helm-*.tar.gz* linux-amd64
            helm repo add stable https://charts.helm.sh/stable
            helm repo update

        """,
        version_get="""helm version""",
    ),
    SetupTool(
        name="hx",
        version=">=25.01.1",
        install="""
            curl -sLO "https://github.com/helix-editor/helix/releases/download/{version}/helix-{version}-x86_64-linux.tar.xz"
            tar xf helix-{version}-x86_64-linux.tar.xz
            rm helix-{version}-x86_64-linux.tar.xz
            sudo mv helix-{version}-x86_64-linux/hx /usr/local/bin/
            mkdir -p ~/.config/helix/runtime
            mv helix-{version}-x86_64-linux/runtime ~/.config/helix/runtime
            rm -Rf helix-{version}-x86_64-linux
        """,
        version_get="hx --version",
    ),
    SetupTool(
        name="java",
        version=">=17.0.0",
        install="""
            apt update
            apt install --yes openjdk-17-jre
        """,
        version_get="""java --version""",
    ),
    SetupTool(
        name="k9s",
        version=">=0.50.4",
        install="""
            curl -sLO "https://github.com/derailed/k9s/releases/download/v{version}/k9s_Linux_amd64.tar.gz"
            tar xf k9s_Linux_amd64.tar.gz
            sudo mv k9s /usr/local/bin/
        """,
        version_get="k9s version",
    ),
    SetupTool(
        name="kubectl",
        # curl -L -s https://dl.k8s.io/release/stable.txt
        version=">=1.32.3",
        install="""
            curl -LO "https://dl.k8s.io/release/v{version}/bin/linux/amd64/kubectl"
            chmod a+x kubectl
            sudo mv kubectl /usr/local/bin/
        """,
        version_get="""kubectl version --client""",
    ),
    SetupTool(
        name="minio",
        # wget -q -O - https://dl.min.io/server/minio/release/linux-amd64/ | grep -Eo 'minio_[^"]*_amd64\.deb' | sort -u
        # version= 'RELEASE.2025-03-12T18-04-18Z',
        # RUN MINIO_FILENAME=`wget -q -O - https://dl.min.io/server/minio/release/linux-amd64/ | grep -Eo 'minio_[^"]*_amd64\.deb' | sort -u` \
        #    && wget --quiet https://dl.min.io/server/minio/release/linux-amd64/$MINIO_FILENAME \
        #    && dpkg -i minio_*_amd64.deb \
        #    && rm *.deb
        install="""
            wget --quiet https://dl.min.io/server/minio/release/linux-amd64/minio_20250312180418.0.0_amd64.deb
            dpkg -i minio_*_amd64.deb
            rm minio_*_amd64.deb
        """,
        version_get="""minio --version""",
    ),
    SetupTool(
        name="nvm",
        version="==0.40.2",
        install="""curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v{version}/install.sh | bash""",
        version_get="""
            . $HOME/.nvm/nvm.sh
            nvm --version
        """,
    ),
    SetupTool(
        name="npx",
        version="==10.9.2",
        install="""
            . $HOME/.nvm/nvm.sh
            nvm install --lts
            nvm use --lts
        """,
        version_get="""
            . $HOME/.nvm/nvm.sh
            npx --version
        """,
    ),

    SetupTool(
        name="playwright",
        version=">=1.51.0",
        install="""
            uvx playwright install-deps
            uvx playwright install
        """,
        version_get="""uvx playwright --version""",
    ),
    SetupTool(
        name="podman",
        version=">=4.3.1",
        install="""
            apt update
            apt install --yes podman
        """,
        version_get="""podman --version""",
    ),
    SetupTool(
        name="scw",
        version=">=2.39.0",
        # curl -s https://raw.githubusercontent.com/scaleway/scaleway-cli/master/scripts/get.sh | sh
        install="""
            curl -LO "https://github.com/scaleway/scaleway-cli/releases/download/v{version}/scaleway-cli_{version}_linux_amd64"
            chmod a+x scaleway-cli_{version}_linux_amd64
            sudo mv scaleway-cli_{version}_linux_amd64 /usr/local/bin/scw
        """,
        version_get="""scw version""",
    ),
    SetupTool(
        name="typst",
        version=">=0.13.1",
        install="""
            curl -LO "https://github.com/typst/typst/releases/download/v{version}/typst-x86_64-unknown-linux-musl.tar.xz"
            tar xvf typst-x86_64-unknown-linux-musl.tar.xz
            sudo mv typst-x86_64-unknown-linux-musl/typst /usr/local/bin/
            rm -Rf typst-x86_64-unknown-linux-musl
        """,
        version_get="""typst --version""",
    ),
    SetupTool(
        name="zellij",
        version="==0.42.1",
        install="""
            wget --quiet -nv https://github.com/zellij-org/zellij/releases/download/v{version}/zellij-x86_64-unknown-linux-musl.tar.gz
            tar -xvf zellij*.tar.gz
            rm zellij*.tar.gz
            chmod +x zellij
            mv zellij /usr/local/bin/
        """,
        version_get="""zellij --version""",
    ),
]


@app.command()
def tool(
    ctx: typer.Context,
    tool: Annotated[list[str], typer.Argument()],
    install: bool = True,
    summary: bool = True,
    silent: bool = False,
    #tool:  Annotated[list[str], typer.Argument()] = [],

):
    installed_tools: list[SetupTool] = []
    if tool == ['all']:
        tool = [t.name for t in tools]
    for single_tool in tool:
        for t in tools:
            if single_tool in (t.name, ""):
                installed_tools.append(t)
                if install:
                    t.setup(ctx_obj=ctx.obj, silent=silent)
                if single_tool != "":
                    # return only if single tool install, stay for all
                    break
        else:
            if single_tool != "":
                # only if ask for a specific tool
                print(f"tool {single_tool} not supported !")

    if summary:
        table = Table(title="installed pp tools")

        table.add_column("tool", style="cyan", no_wrap=True)
        table.add_column("required", justify="right", style="magenta")
        table.add_column("installed", justify="right", style="green")

        for t in installed_tools:
            valid = t.check(ctx_obj=ctx.obj)
            table.add_row(
                t.name, t.version, t.checked_version, style="red" if not valid else None
            )

        console.print(table)


@app.command()
def all(
    ctx: typer.Context,
    summary: bool = True,
    install: bool = True,
):
    """
    Setup all paxpar tools
    """
    tool(
        ctx=ctx,
        tool=[""],
        summary=summary,
        install=install,
    )


@app.command()
def clean():
    """
    Clean paxpar env
    """
    # for svc in (
    #    "paxpar/services/core",
    #    "paxpar/services/forge",
    # ):
    #    call("""rm -Rf .venv""", cwd=svc)
    call("""find . -type d -name "__pycache__" | xargs rm -rf {}""")
    call("""rm -Rf node_modules .coverage .mypy_cache""")
    # for svc in ("front",):
    #    call("""rm -Rf node_modules""", cwd=f"services/{svc}")
    call("""rm -Rf .venv""")
    call("""rm -Rf ~/.pyenv""")


@app.command()
def registry_reset():
    """
    Reset the microk8s registry
    """

    """
    TODO: other hints :

        microk8s disable storage:destroy-storage
        microk8s enalbe storage

        microk8s.ctr images list -q | grep paxpa
        microk8s.ctr images remove ###ref
        docker image rm ###
        ctr images remove
    """
    call(
        """
        docker system prune -a -f --volumes
        microk8s.disable registry
        sleep 3
        microk8s.enable registry
    """
    )
