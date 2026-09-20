import tarfile

import pytest

from envsnap.pack import save_snapshot


def test_save(tmp_path):
    p = tmp_path / "p"
    p.mkdir()
    (p / "app.py").write_text("print(1)")
    out = str(tmp_path / "a.envsnap")
    save_snapshot(str(p), out)
    assert "manifest.json" in tarfile.open(out).getnames()


def test_save_refuses_secrets(tmp_path):
    p = tmp_path / "p"
    p.mkdir()
    (p / "app.py").write_text("AKIA1234567890ABCDEF")
    with pytest.raises(ValueError):
        save_snapshot(str(p), str(tmp_path / "b.envsnap"))
