from envsnap.pack import save_snapshot


def test_save_skips_own_output(tmp_path):
    p = tmp_path / "p"
    p.mkdir()
    (p / "app.py").write_text("print(1)")
    out = str(p / "self.envsnap")
    save_snapshot(str(p), out, on_secret="skip")
    import tarfile

    inner = tarfile.open(out).extractfile("code.tar.gz")
    names = tarfile.open(fileobj=inner).getnames()
    assert "self.envsnap" not in names
    assert "restored-app" not in str(names)
