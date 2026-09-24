import tarfile

from envsnap.pack import save_snapshot
from envsnap.restore import list_snapshot_files


def test_inspect_lists_tree(tmp_path):
    p = tmp_path / "p"
    p.mkdir()
    (p / "app.py").write_text("print(1)")
    sub = p / "src"
    sub.mkdir()
    (sub / "main.py").write_text("x")
    snap = save_snapshot(str(p), str(tmp_path / "a.envsnap"))
    files = list_snapshot_files(snap)
    names = [f[0] for f in files]
    assert "app.py" in names and "src/main.py" in names
