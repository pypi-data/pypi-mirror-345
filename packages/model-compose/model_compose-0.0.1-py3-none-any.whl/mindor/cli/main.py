
import click

from .commands.up import up_command
from .commands.down import down_command
from .commands.exec import exec_command

@click.group()
def app():
    """Mindor CLI (model-compose)"""
    pass

app.add_command(up_command)
app.add_command(down_command)
app.add_command(exec_command)
