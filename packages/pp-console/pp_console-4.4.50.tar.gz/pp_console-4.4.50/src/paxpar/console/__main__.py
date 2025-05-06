# allow calling cli with : python -m paxpar.cli
from .pp import app
# see https://typer.tiangolo.com/tutorial/package/#set-a-program-name-in-__main__py
app(prog_name="pp")