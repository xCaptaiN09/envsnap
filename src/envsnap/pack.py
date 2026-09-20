"""Pack a project dir into a single .envsnap tar.gz."""
import fnmatch
import io
import json
import os
import tarfile

from .detect import SKIP_DIRS, detect_project, scrub_value

# Test/fixture dirs: flag their fake keys but don't hard-block (they're
# usually 'AKIA...EXAMPLE' or PEM in assertions, not real creds).
SOFT_DIRS = {"tests", "test", "__tests__", "fixtures", "examples", "docs"}


def _should_skip(rel: str, globs: list) -> bool:
    parts = rel.split(os.sep)
    if any(p in SKIP_DIRS for p in parts):
        return True
    return any(fnmatch.fnmatch(rel, g) for g in globs)


def _is_soft_path(rel: str) -> bool:
    parts = rel.split(os.sep)
    if any(p in SOFT_DIRS for p in parts):
        return True
    base = os.path.basename(rel).lower()
    return base.startswith("test") or ".test." in base or ".spec." in base


def find_secret_files(root: str, globs: list) -> list:
    found = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root)
            if _should_skip(rel, globs):
                continue
            if _is_soft_path(rel):
                continue  # soft: warn only, handled by caller
            try:
                if os.path.getsize(p) > 200_000:
                    continue
                with open(p, errors="ignore") as fh:
                    if scrub_value(fh.read(4000)):
                        found.append(rel)
            except Exception:
                continue
    return found


def find_soft_secret_files(root: str, globs: list) -> list:
    """Fake-looking keys in tests/fixtures — warn, don't block."""
    found = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root)
            if _should_skip(rel, globs):
                continue
            if not _is_soft_path(rel):
                continue
            try:
                if os.path.getsize(p) > 200_000:
                    continue
                with open(p, errors="ignore") as fh:
                    if scrub_value(fh.read(4000)):
                        found.append(rel)
            except Exception:
                continue
    return found


def save_snapshot(root: str, out: str, on_secret: str = "ask") -> str:
    m = detect_project(root)
    globs = m.get("ignores", [])
    hard = find_secret_files(root, globs)
    if hard and on_secret == "skip":
        globs = globs + hard
    elif hard:
        raise ValueError(f"refusing to pack secret in {hard[0]}")
    with tarfile.open(out, "w:gz") as t:
        b = json.dumps(m, indent=2).encode()
        ti = tarfile.TarInfo("manifest.json")
        ti.size = len(b)
        t.addfile(ti, io.BytesIO(b))
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as c:
            for dp, dn, fn in os.walk(root):
                dn[:] = [d for d in dn if d not in SKIP_DIRS]
                for f in fn:
                    p = os.path.join(dp, f)
                    rel = os.path.relpath(p, root)
                    if _should_skip(rel, globs):
                        continue
                    if rel in hard and on_secret == "skip":
                        continue
                    c.add(p, rel)
        buf.seek(0)
        data = buf.getvalue()
        ti2 = tarfile.TarInfo("code.tar.gz")
        ti2.size = len(data)
        t.addfile(ti2, io.BytesIO(data))
    return out
