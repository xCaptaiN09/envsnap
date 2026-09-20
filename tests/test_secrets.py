from envsnap.pack import find_secret_files, save_snapshot


def test_find_secrets_skips_test_fixtures(tmp_path):
    p = tmp_path / "p"
    p.mkdir()
    (p / "app.py").write_text("print(1)")
    tdir = p / "tests"
    tdir.mkdir()
    (tdir / "a.test.ts").write_text("const raw = '-----BEGIN PRIVATE KEY-----\\nabc\\n';")
    assert find_secret_files(str(p), []) == []


def test_real_secret_still_found(tmp_path):
    p = tmp_path / "p"
    p.mkdir()
    (p / ".env").write_text("KEY=AKIA1234567890ABCDEF")
    found = find_secret_files(str(p), [])
    assert found == [".env"]


def test_save_skips_flag(tmp_path):
    p = tmp_path / "p"
    p.mkdir()
    (p / ".env").write_text("KEY=AKIA1234567890ABCDEF")
    (p / "app.py").write_text("print(1)")
    out = str(tmp_path / "a.envsnap")
    save_snapshot(str(p), out, on_secret="skip")
    assert "manifest.json" in __import__("tarfile").open(out).getnames()
