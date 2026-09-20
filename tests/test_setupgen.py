import io
import os
import tarfile

from envsnap.setupgen import generate_setup


def test_setupgen(tmp_path):
    m = {"python": "3.10.12", "node": "18", "run": "python app.py", "python_has_app": True, "env_template": ["OPENAI_KEY"]}
    s = generate_setup(m)
    assert "python app.py" in s and "OPENAI_KEY" in s


def test_setupgen_node_only_falls_back_to_npm_test():
    m = {"python": "3.10.12", "node": "v26.9.0", "run": "python app.py", "python_has_app": False}
    assert "npm test" in generate_setup(m)
