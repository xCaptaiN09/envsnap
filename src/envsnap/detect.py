import json
import os
import platform
import re
import sys

SECRET_RE = re.compile(
    r"(AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{8,}|ghp_[A-Za-z0-9]{8,}|BEGIN (RSA )?PRIVATE KEY)"
)

SKIP_DIRS = {"node_modules", ".venv", "venv", ".git", "__pycache__"}


def scrub_value(v: str) -> bool:
    """True if value looks like a real secret."""
    return bool(SECRET_RE.search(v or ""))


def _ignore_globs(root: str) -> list:
    p = os.path.join(root, ".envsnapignore")
    if not os.path.exists(p):
        return []
    out = []
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line)
    return out


def detect_project(root: str) -> dict:
    files = set(os.listdir(root))
    py = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    node = None
    run = None
    if "package.json" in files:
        try:
            with open(os.path.join(root, "package.json")) as f:
                pkg = json.load(f)
            run = (pkg.get("scripts") or {}).get("dev")
        except Exception:
            run = None
        node = "18"
    if "app.py" in files and not run:
        run = "python app.py"
    env_template: list = []
    env_path = os.path.join(root, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                # Keys only — values never stored.
                env_template.append(k)
                # Caller (pack) must refuse secret values; detect only lists keys.
    return {
        "os": platform.system(),
        "arch": platform.machine(),
        "python": py,
        "node": node,
        "run": run or "python app.py",
        "env_template": env_template,
        "ignores": _ignore_globs(root),
    }
