"""Inspect + dry-restore + full restore a .envsnap file."""
import io
import json
import os
import tarfile


def inspect_snapshot(path: str) -> dict:
    with tarfile.open(path) as t:
        f = t.extractfile("manifest.json")
        assert f is not None
        return json.load(f)


def restore_dry(path: str, dest: str) -> dict:
    m = inspect_snapshot(path)
    os.makedirs(dest, exist_ok=True)
    with tarfile.open(path) as t:
        c = t.extractfile("code.tar.gz")
        assert c is not None
        with open(os.path.join(dest, "code.tar.gz"), "wb") as out:
            out.write(c.read())
    return {"ok": True, "run": m.get("run")}


def restore_full(path: str, dest: str) -> dict:
    """Extract all code files + write setup.sh. No secrets ever written."""
    from .setupgen import generate_setup

    m = inspect_snapshot(path)
    os.makedirs(dest, exist_ok=True)
    with tarfile.open(path) as t:
        c = t.extractfile("code.tar.gz")
        assert c is not None
        data = c.read()
    buf = io.BytesIO(data)
    with tarfile.open(fileobj=buf) as inner:
        inner.extractall(dest, filter="data")
    setup = generate_setup(m)
    with open(os.path.join(dest, "setup.sh"), "w") as f:
        f.write(setup)
    os.chmod(os.path.join(dest, "setup.sh"), 0o755)
    return {"ok": True, "run": m.get("run"), "dir": dest}
