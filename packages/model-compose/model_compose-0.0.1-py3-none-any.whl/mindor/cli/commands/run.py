
import click
from mindor.core.workflow import run_workflow

@click.command(name="run")
@click.option('--input', help='Text input for the pipeline.')
def run_command(input):
    result = run_workflow(input)
    click.echo(f"🧠 Output: {result}")
