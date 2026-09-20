"""Inspect + dry-restore a .envsnap file."""
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
