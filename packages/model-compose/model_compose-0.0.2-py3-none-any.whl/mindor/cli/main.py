
import click

from .commands.up import up_command
from .commands.down import down_command
from .commands.run import run_command

@click.group()
def app():
    """model-compose (from Mindor)"""
    pass

app.add_command(up_command)
app.add_command(down_command)
app.add_command(run_command)
