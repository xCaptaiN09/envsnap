import io
import os
import tarfile

from envsnap.setupgen import generate_setup


def test_setupgen(tmp_path):
    m = {"python": "3.10.12", "node": "18", "run": "python app.py", "env_template": ["OPENAI_KEY"]}
    s = generate_setup(m)
    assert "python app.py" in s and "OPENAI_KEY" in s
