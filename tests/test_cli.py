from click.testing import CliRunner
from envsnap.cli import main


def test_cli_help_lists_save_open_share():
    r = CliRunner().invoke(main, ["--help"])
    assert r.exit_code == 0
    assert "save" in r.output
    assert "open" in r.output
    assert "share" in r.output
