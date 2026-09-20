from click.testing import CliRunner

from envsnap.cli import main


def test_share_stub(tmp_path):
    r = CliRunner().invoke(main, ["share", str(tmp_path / "a.envsnap")])
    assert r.exit_code == 0
    assert "V0" in r.output or "relay in V0.2" in r.output
