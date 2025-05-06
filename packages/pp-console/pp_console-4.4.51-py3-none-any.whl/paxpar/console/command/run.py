from typing import Optional

import typer
from rich.console import Console
from paxpar.cli.tools import call, root_command_callback, get_pp_conf

console = Console()

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
def core(
    ctx: typer.Context,
    container: bool = False,
    version: str = "4.2.1",
    entrypoint: str = "",
    reload: bool = True,
):
    """
    Start paxpar core service
    """
    # conf = get_conf()
    port = 8881

    if not container:
        # host = host_only(os.environ.get("SVC_CORE_PROXY", "0.0.0.0"))
        host = "0.0.0.0"
        cmd = rf"""
            uv run uvicorn paxpar.services.core.main:app \
                --host {host} \
                --port {port} \
                {'--reload' if reload else ''} \
        """
    else:
        # TODO: inject local IP
        cmd = rf"""
            docker run \
                -ti \
                --rm \
                -p {port}:8881 \
                -e PP_CONF \
                --add-host=paxpar-conv:192.168.108.106 \
                {f"--entrypoint {entrypoint}" if entrypoint != "" else ""} \
                registry.gitlab.com/arundo-tech/paxpar/paxpar-core:v{version}
        """

    call(cmd, ctx_obj=ctx.obj)

@app.command()
def forge(
    ctx: typer.Context,
    browser: bool = True,
    token: Optional[str] = None,
    uv: bool = True,
    container: bool = False,
):
    """
    Start paxpar forge service
    """
    conf = get_pp_conf()
    token = token or conf.NOTEBOOK_TOKEN

    cmd = rf"""alias pp="$PWD/pp && "
        {"uv run " if uv else ""}jupyter lab \
        --config=$PWD/paxpar/services/forge/jupyter_notebook_config.json \
        --notebook-dir=$PWD/ref \
        --ServerApp.ip=* \
        --IdentityProvider.token={token} \
        --allow-root \
        {"" if browser else "--no-browser"} \
        -y
    """
    call(cmd, ctx_obj=ctx.obj)

@app.command()
def conv(
    ctx: typer.Context,
):
    """
    Start paxpar conv service
    """
    conf = get_pp_conf()

    call(
        f"""podman run -it --rm \
        -p 0.0.0.0:{conf.services.conv.port}:3000 \
        {conf.services.conv.image}        
        """,
        ctx_obj=ctx.obj,
    )

@app.command()
def store(
    ctx: typer.Context,
):
    """
    Start paxpar minio service (dev only)
    """
    """
    Shared volume is not working with docker desktop ??
    #-v $PWD/temp/s3:/data \
    #TODO: create bucket if volume is not persistent

    podman run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"

    ./minio server /path/to/data 2>&1 | grep -oP '(?<=RequestHeader: Host: )[^ ]+|(?<=RequestPath: )[^ ]+' | paste -sd' \n'
    """
    conf = get_pp_conf()

    call(
        rf"""
        podman run -it --rm \
            -v ~/minio/data:/data \
            -p 9000:{conf.services.store.port} \
            -p 9001:9001 \
            -e 'MINIO_ROOT_USER={conf.ref.sources.common.fsspec.key}' \
            -e 'MINIO_ROOT_PASSWORD={conf.ref.sources.common.fsspec.secret}' \
            -e 'MINIO_TRACE=1' \
            {conf.services.store.image} \
            server /data --console-address ":9001"
        """,
        ctx_obj=ctx.obj,
    )

@app.command()
def office(
    ctx: typer.Context,
    secret: str,
):
    """
    Start paxpar only office service (dev only)
    """
    # TODO: read secret from conf/envvar
    call(
        rf"""
        podman run -it \
            -p 8303:80 \
            -e JWT_SECRET={secret} \
            onlyoffice/documentserver
        """,
        ctx_obj=ctx.obj,
    )

@app.command()
def ci(
    ctx: typer.Context,
    #before_script: bool = True,
):
    """
    Start a CI-like container
    """
    #extra_bash_cmd = (
    #    """-c "./packages/pp-cli/script/install_uv.sh; uv run pp setup all; exec bash" """
    #    if before_script
    #    else ""
    #)
    call(
        rf"""
        podman run -it --rm \
            -v $PWD:/builds/arundo-tech/paxpar \
            -w /builds/arundo-tech/paxpar \
            --entrypoint /bin/bash \
            python:3.13
        """,
        #{extra_bash_cmd}
        ctx_obj=ctx.obj,
    )

