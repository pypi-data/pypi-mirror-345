import typer
from rich.console import Console
from paxpar.cli.tools import call


console = Console()

app = typer.Typer(help="s3 related commands")



@app.command()
def fs(path: str = typer.Argument(None)):
    """
    Mount S3 pp ref via s3fs
    """
    call("""mkdir -p temp/pp-ref-common""")
    call(
        """s3fs pp-ref-common \
        $PWD/temp/pp-ref-common \
        -o profile=paxpar \
        -o use_path_request_style \
        -o endpoint=fr-par \
        -o parallel_count=15 \
        -o multipart_size=5 \
        -o nocopyapi \
        -o url=https://s3.fr-par.scw.cloud
    """
    )


@app.command()
def mount(path: str = typer.Argument(None)):
    """
    Mount S3 pp ref via rclone
    """
    # --allow-non-empty
    # Option --vfs-cache-mode full is usefull to allow libreoffice/inkscape to edit in-place
    call(
        """rclone mount -v \
        --vfs-cache-mode full \
        --ignore-checksum \
        --allow-non-empty \
        pprefprod:/pp-ref-common ~/pp-ref-common
    """
    )


@app.command()
def mountsrc(path: str = typer.Argument(None)):
    """
    Mount S3 pp ref via rclone in the src folder
    """
    # --allow-non-empty
    # Option --vfs-cache-mode full is usefull to allow libreoffice/inkscape to edit in-place
    call(
        """rclone mount -v \
        --vfs-cache-mode full \
        --ignore-checksum \
        --allow-non-empty \
        pprefprod:/pp-ref-common ref/common
    """
    )


@app.command()
def clean(path: str = typer.Argument(None)):
    """
    Clean S3 mounted pp ref content
    """
    call(
        r"""
        rm -Rf ~/Nextcloud/pp-ref-common/.Trash*
        find ~/Nextcloud/pp-ref-common -type d -name '__pycache__' -print -exec rm -Rf {} \;
        find ~/Nextcloud/pp-ref-common -type d -name '.ipynb_checkpoints' -print -exec rm -Rf {} \;
        find ~/Nextcloud/pp-ref-common -type f -name '*.pyc' -print -delete
        find ~/Nextcloud/pp-ref-common -type f -name '.~lock.*' -print -delete
    """
    )


@app.command()
def mountforge(path: str = typer.Argument(None)):
    """
    Mount S3 pp ref via rclone in forge folder
    """
    # --allow-non-empty
    # Option --vfs-cache-mode full is usefull to allow libreoffice/inkscape to edit in-place
    call(
        """rclone mount -v \
        --vfs-cache-mode full \
        --ignore-checksum \
        --allow-non-empty \
        pprefprod:/pp-ref-common services/forge/pp-ref-common
    """
    )


@app.command()
def sync(path: str = typer.Argument(None)):
    """
    Sync S3 pp ref content
    """
    call(
        """rclone sync -v \
            --filter-from filter-rclone.txt \
            pprefprod:/pp-ref-common ref/common
    """
    )
