from click.testing import CliRunner

from envsnap.cli import main


def test_save_yes_creates_file(tmp_path):
    proj = tmp_path / "p"
    proj.mkdir()
    (proj / "app.py").write_text("print(1)")
    import os

    cwd = os.getcwd()
    os.chdir(proj)
    try:
        r = CliRunner().invoke(main, ["save", "-o", str(tmp_path / "s.envsnap"), "--yes"])
        assert r.exit_code == 0, r.output
        assert (tmp_path / "s.envsnap").exists()
    finally:
        os.chdir(cwd)
