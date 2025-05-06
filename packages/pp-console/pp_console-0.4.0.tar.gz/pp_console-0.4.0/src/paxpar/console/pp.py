# /// script
# dependencies = [
#   "pydantic",
#   "python-dotenv",
#   "pyyaml",
#   "typer",
# ]
# ///
#!/usr/bin/env python3
#
#!.venv/bin/python
#!services/core/.venv/bin/python
#
# bootstrap env with :
#
#    pyenv install --skip-existing
#    poetry install -vv

import os
import signal

import typer
from dotenv import load_dotenv

from paxpar.cli.tools import set_pp_pythonpath


set_pp_pythonpath()

# take environment variables from .env
# this is not the app conf but the devops env conf
if load_dotenv():
    typer.echo(".env found and loaded !")

from paxpar.cli.command.build import app as app_build
from paxpar.cli.command.conf import app as app_conf
from paxpar.cli.command.deploy import app as app_deploy
from paxpar.cli.command.dev import app as app_dev
from paxpar.cli.command.image import app as app_image
from paxpar.cli.command.misc import app as app_misc
from paxpar.cli.command.py import app as app_py
from paxpar.cli.command.ref import app as app_ref
from paxpar.cli.command.run import app as app_run
from paxpar.cli.command.s3 import app as app_s3
from paxpar.cli.command.scrap import app as app_scrap
from paxpar.cli.command.setup import app as app_setup
from paxpar.cli.command.status import app as app_status
from paxpar.cli.command.test import app as app_test
from paxpar.cli.command.version import app as app_version

app = typer.Typer(
    name="pp cli",
    help="paxpar command line interface",  # , callback=callback
)


# subcommands as a group
#app.add_typer(app_conf, name="conf")
app.add_typer(app_build, name="build")
app.add_typer(app_conf, name="conf")
app.add_typer(app_deploy, name="deploy")
app.add_typer(app_dev, name="dev")
app.add_typer(app_image, name="image")
app.add_typer(app_misc, name="misc")
app.add_typer(app_py, name="py")
app.add_typer(app_ref, name="ref")
app.add_typer(app_run, name="run")
app.add_typer(app_s3, name="s3")
app.add_typer(app_scrap, name="scrap")
app.add_typer(app_setup, name="setup")
app.add_typer(app_status, name="status")
app.add_typer(app_test, name="test")
app.add_typer(app_version, name="version")


# see https://stackoverflow.com/questions/320232/ensuring-subprocesses-are-dead-on-exiting-python-program
USE_KILL = False

# ____________________________________________________________________


if __name__ == "__main__":
    if USE_KILL:
        # see https://stackoverflow.com/questions/320232/ensuring-subprocesses-are-dead-on-exiting-python-program
        os.setpgrp()  # create new process group, become its leader
        try:
            app()
        finally:
            os.killpg(0, signal.SIGKILL)  # kill all processes in my group
    else:
        app()
# ____________________________________________________________________
