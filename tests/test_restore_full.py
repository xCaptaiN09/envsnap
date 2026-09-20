from envsnap.pack import save_snapshot
from envsnap.restore import restore_full


def test_restore_full(tmp_path):
    p = tmp_path / "p"
    p.mkdir()
    (p / "app.py").write_text("print(1)")
    s = save_snapshot(str(p), str(tmp_path / "a.envsnap"))
    dest = tmp_path / "out"
    r = restore_full(s, str(dest))
    assert r["ok"] is True
    assert (dest / "app.py").exists()
    assert (dest / "setup.sh").exists()
