import json
import os
import platform
import re
import shutil
import subprocess
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


def _node_version() -> str | None:
    if not shutil.which("node"):
        return None
    try:
        return subprocess.check_output(["node", "--version"], text=True, timeout=5).strip()
    except Exception:
        return None


def _pip_packages(root: str, limit: int = 50) -> list:
    req = os.path.join(root, "requirements.txt")
    if os.path.exists(req):
        out = []
        with open(req) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    out.append(line)
        return out[:limit]
    try:
        txt = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"], text=True, timeout=15
        )
        return [l.strip() for l in txt.splitlines() if l.strip()][:limit]
    except Exception:
        return []


def _os_detail() -> str:
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return f"{platform.system()} {platform.release()}"


def detect_project(root: str) -> dict:
    files = set(os.listdir(root))
    py = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    node = None
    node_version = _node_version()
    run = None
    if "package.json" in files:
        try:
            with open(os.path.join(root, "package.json")) as f:
                pkg = json.load(f)
            scripts = pkg.get("scripts") or {}
            run = scripts.get("dev") or scripts.get("start") or scripts.get("test")
        except Exception:
            run = None
        node = node_version or "18"
    for cand in ("app.py", "main.py", "server.py", "manage.py"):
        if cand in files and not run:
            run = f"python {cand}"
            break
    python_has_app = any(c in files for c in ("app.py", "main.py", "server.py", "manage.py"))
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
        "os_detail": _os_detail(),
        "arch": platform.machine(),
        "python": py,
        "pip_packages": _pip_packages(root),
        "node": node,
        "node_version": node_version,
        "run": run or "python app.py",
        "python_has_app": python_has_app,
        "env_template": env_template,
        "ignores": _ignore_globs(root),
    }
