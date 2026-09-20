from envsnap.pack import save_snapshot
from envsnap.restore import inspect_snapshot, restore_dry


def test_open(tmp_path):
    p = tmp_path / "p"
    p.mkdir()
    (p / "app.py").write_text("print(1)")
    s = save_snapshot(str(p), str(tmp_path / "a.envsnap"))
    assert "python" in inspect_snapshot(s)
    assert restore_dry(s, str(tmp_path / "out"))["ok"] is True
