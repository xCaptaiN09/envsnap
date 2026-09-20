from envsnap.detect import detect_project, scrub_value


def test_detect_demo(tmp_path):
    (tmp_path / "app.py").write_text("print('hi')")
    d = detect_project(str(tmp_path))
    assert "python" in d and "run" in d


def test_scrub():
    assert scrub_value("AKIA1234567890ABCDEF") is True
    assert scrub_value("hello") is False


def test_env_keys_only(tmp_path):
    (tmp_path / "app.py").write_text("x")
    (tmp_path / ".env").write_text("OPENAI_KEY=sk-abc123XYZ\nDEBUG=1\n")
    d = detect_project(str(tmp_path))
    assert "OPENAI_KEY" in d["env_template"]
    assert "sk-abc123XYZ" not in str(d)
