
from click.testing import CliRunner
from mindor.cli import app

def test_exec_command():
    runner = CliRunner()
    result = runner.invoke(app, ['exec', '--input', 'Hello'])
    assert "Processed" in result.output
