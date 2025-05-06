from subprocess import call
from paxpar.cli.tools import root_command_callback
import typer
from rich.console import Console


console = Console()

app = typer.Typer(
    help="Misc pp commands",
    callback=root_command_callback(),
)


@app.command()
def debugpy():
    """
    Start debugpy ... (NOT IMPLEMENTED)
    """
    # TODO:
    # python -m debugpy --listen 5678 --wait-for-client scripts/cli/pp.py ref refresh
    ...


@app.command()
def webui():
    #TODO: does not work with py 3.13 !!
    call(
        """DATA_DIR="$PWD\\data" uvx --python 3.11 open-webui@latest serve""",
        shell=True,
        #"""podman run \
        #    --rm \
        #    -p 3000:8080 \
        #    -v open-webui:./data \
        #    ghcr.io/open-webui/open-webui:main"""
    )


@app.command()
def ollama():
    call(
        #"""ollama run qwen3:30b-a3b"""
        """ollama serve"""
    )
