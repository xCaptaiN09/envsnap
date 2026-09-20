"""Pack a project dir into a single .envsnap tar.gz."""
import fnmatch
import io
import json
import os
import tarfile

from .detect import SKIP_DIRS, detect_project, scrub_value


def _should_skip(rel: str, globs: list) -> bool:
    parts = rel.split(os.sep)
    if any(p in SKIP_DIRS for p in parts):
        return True
    return any(fnmatch.fnmatch(rel, g) for g in globs)


def save_snapshot(root: str, out: str) -> str:
    m = detect_project(root)
    globs = m.get("ignores", [])
    # Refuse to pack real secret values found in small text files.
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, root)
            if _should_skip(rel, globs):
                continue
            try:
                if os.path.getsize(p) > 200_000:
                    continue
                with open(p, errors="ignore") as fh:
                    if scrub_value(fh.read(4000)):
                        raise ValueError(f"refusing to pack secret in {rel}")
            except ValueError:
                raise
            except Exception:
                continue
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
                    c.add(p, rel)
        buf.seek(0)
        data = buf.getvalue()
        ti2 = tarfile.TarInfo("code.tar.gz")
        ti2.size = len(data)
        t.addfile(ti2, io.BytesIO(data))
    return out
