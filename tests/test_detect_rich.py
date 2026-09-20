from envsnap.detect import detect_project


def test_detect_rich_fields(tmp_path):
    (tmp_path / "app.py").write_text("print(1)")
    (tmp_path / "requirements.txt").write_text("fastapi==0.110\n")
    d = detect_project(str(tmp_path))
    assert "pip_packages" in d and "os_detail" in d and "node_version" in d
