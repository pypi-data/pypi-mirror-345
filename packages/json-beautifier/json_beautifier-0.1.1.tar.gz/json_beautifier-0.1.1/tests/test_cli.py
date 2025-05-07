from click.testing import CliRunner
from json_beautifier.cli import main

def test_main_cli():
    """Unit test for running the CLI"""
    runner = CliRunner()
    result = runner.invoke(main, ['{"Sample Json" : {"Testing" : "Test", "testing": "test"}}'])

    assert result.exit_code == 0
