import asyncio
import importlib.metadata
import json
import os
import signal
import subprocess
import sys
from functools import wraps
from pathlib import Path
from typing import Any, Callable

import typer
import yaml
from pydantic import BaseModel, JsonValue
from rich.console import Console

console = Console()

class PaxparCLI_ObjCtx(BaseModel):
    verbose: bool = False
    dry_run: bool = False


def set_pp_pythonpath(
    this_file: str | None = None,
    ctx_obj: PaxparCLI_ObjCtx | None = None,
) -> str:
    app_path = str(Path(this_file or __file__).absolute().parent.parent)
    sys.path.append(app_path)
    # typer.echo(f"{app_path} added to PYTHONPATH")
    if ctx_obj and ctx_obj.verbose:
        print(f"{app_path} added to PYTHONPATH")
    return app_path


def call(
    cmd: str,
    cwd: str | None = None,
    pythonpath_set: bool = True,
    extra_envvars: dict[str, Any] | None = None,
    stdout: Any = None,
    dry_run: bool = False,
    verbose: bool = False,
    executable: str | None = None,
    check: bool = True,
    ctx_obj: PaxparCLI_ObjCtx | None = None,
) -> subprocess.CompletedProcess[bytes]:
    if dry_run or (ctx_obj and ctx_obj.dry_run):
        print(cmd)
        return b""

    my_env = os.environ.copy()

    if pythonpath_set:
        my_env["PYTHONPATH"] = set_pp_pythonpath(ctx_obj=ctx_obj)

    if verbose or (ctx_obj and ctx_obj.verbose):
        if cwd:
            typer.echo(f"[{cwd}] {cmd}")
        else:
            typer.echo(cmd)

    if extra_envvars:
        for k, v in extra_envvars.items():
            if verbose or (ctx_obj and ctx_obj.verbose):
                typer.echo(f"setting envvar {k}")
            my_env[k] = v

    if (ctx_obj is None and not dry_run) or (ctx_obj and not ctx_obj.dry_run):
        return subprocess.run(
            cmd.strip(),
            shell=True,
            env=my_env,
            cwd=cwd,
            stdout=stdout,
            executable=executable,
            check=check,
        )


def call_text_output(
    cmd: str | None,
    strip: bool = True,
    executable: str = "/bin/bash",
    ctx_obj: PaxparCLI_ObjCtx | None = None,
) -> str:
    '''
    Execute external command and return the output from a a string
    '''
    if cmd is None:
        return ""

    query = call(
        cmd,
        stdout=subprocess.PIPE,
        ctx_obj=ctx_obj,
        executable=executable,
    )
    raw = query.stdout.decode()
    return raw.strip() if strip else raw


def call_json(
    cmd: str | None,
    executable: str = "/bin/bash",
    ctx_obj: PaxparCLI_ObjCtx | None = None,
) -> dict[str, JsonValue]:
    '''
    Execute external command and return the output from a JSON payload
    '''
    raw_test = call_text_output(
        cmd,
        executable=executable,
        ctx_obj=ctx_obj,
    )
    return json.loads(raw_test)


def call_yaml(
    cmd: str | None,
    executable: str = "/bin/bash",
    ctx_obj: PaxparCLI_ObjCtx | None = None,
) -> dict[str, JsonValue]:
    '''
    Execute external command and return the output from a JSON payload
    '''
    raw_test = call_text_output(
        cmd,
        executable=executable,
        ctx_obj=ctx_obj,
    )
    return yaml.safe_load(raw_test)


def host_only(host: str) -> str:
    """
    '[2a01:4f9:2a:25d5::17]' -> '2a01:4f9:2a:25d5::17'
    'localhost' -> 'localhost'
    """
    host = host.strip()
    if host.startswith("["):
        host = host[1:]
    if host.endswith("]"):
        host = host[:-1]

    return host


# see https://github.com/fastapi/typer/issues/950#issuecomment-2351076467
def cli_coro(
    signals=(signal.SIGHUP, signal.SIGTERM, signal.SIGINT),
    shutdown_func=None,
):
    """Decorator function that allows defining coroutines with click."""

    def decorator_cli_coro(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            if shutdown_func:
                for ss in signals:
                    loop.add_signal_handler(ss, shutdown_func, ss, loop)
            return loop.run_until_complete(f(*args, **kwargs))

        return wrapper

    return decorator_cli_coro


def root_command_callback(
    root_command: Callable[[typer.Context], None] | None = None,
):
    """
    typer callback factory with support of root_command
    and verbose, dry_run options

    usage:

    def my_root(ctx: typer.Context):
        print("My own root command !!!!!")

    app = typer.Typer(
        help="Show pp status",
        invoke_without_command=True,
        callback=root_command_callback(my_root),
    )
    """

    def _root(
        ctx: typer.Context,
        verbose: bool = False,
        dry_run: bool = False,
    ):
        if ctx.obj is None:
            ctx.obj = PaxparCLI_ObjCtx()
        ctx_obj: PaxparCLI_ObjCtx = ctx.obj

        if verbose:
            cli_version = importlib.metadata.version("paxpar.cli")
            print(f'pp-cli version {cli_version} (verbose output)')
            ctx_obj.verbose = True

        if dry_run:
            ctx_obj.dry_run = True
            print("Dry run (no effect)")

        if ctx.invoked_subcommand is None and root_command:
            # print("do root command2 ...")
            root_command(ctx)

    return _root


def get_pp_conf():
    #try:
    from paxpar.services.core.conf import get_conf
    #except ModuleNotFoundError:
    return get_conf()
