from click.testing import CliRunner

from envsnap.cli import main


def test_help_short_flag():
    for args in (["-h"], ["--help"]):
        r = CliRunner().invoke(main, args)
        assert r.exit_code == 0
        assert "save" in r.output and "open" in r.output and "share" in r.output


def test_version_flags():
    import re

    from envsnap import __version__

    for args in (["--version"],):
        r = CliRunner().invoke(main, args)
        assert r.exit_code == 0, r.output
        assert re.search(r"\d+\.\d+\.\d+", r.output)
        assert __version__ in r.output
