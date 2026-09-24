"""OS-aware doctor: detect + install missing deps. No sudo without confirm."""
from __future__ import annotations

import platform
import shutil
import subprocess
import sys

# (os_id_fragment, manager) in priority order. Covers your list + extras.
MGRS = [
    ("apt", "apt"), ("dpkg", "apt"),
    ("dnf", "dnf"), ("rpm-ostree", "rpm-ostree"), ("rpm", "dnf"), ("yum", "yum"),
    ("zypper", "zypper"), ("pacman", "pacman"), ("apk", "apk"),
    ("xbps", "xbps"), ("emerge", "emerge"), ("eopkg", "eopkg"),
    ("slackpkg", "slackpkg"), ("nix", "nix"), ("guix", "guix"), ("swupd", "swupd"),
    ("brew", "brew"), ("port", "port"), ("fink", "fink"), ("mas", "mas"),
    ("winget", "winget"), ("choco", "choco"), ("scoop", "scoop"), ("vcpkg", "vcpkg"),
]

INSTALL_TMPL = {
    "apt": "sudo apt install -y {pkg}",
    "dnf": "sudo dnf install -y {pkg}",
    "yum": "sudo yum install -y {pkg}",
    "zypper": "sudo zypper install -y {pkg}",
    "pacman": "sudo pacman -S --noconfirm {pkg}",
    "apk": "sudo apk add {pkg}",
    "xbps": "sudo xbps-install -y {pkg}",
    "emerge": "sudo emerge {pkg}",
    "eopkg": "sudo eopkg install -y {pkg}",
    "slackpkg": "sudo slackpkg install {pkg}",
    "nix": "nix-env -iA nixpkgs.{pkg}",
    "guix": "guix install {pkg}",
    "rpm-ostree": "rpm-ostree install {pkg}",
    "swupd": "sudo swupd bundle-add {pkg}",
    "brew": "brew install {pkg}",
    "port": "sudo port install {pkg}",
    "fink": "fink install {pkg}",
    "mas": "mas install {pkg}",
    "winget": "winget install {pkg}",
    "choco": "choco install -y {pkg}",
    "scoop": "scoop install {pkg}",
    "vcpkg": "vcpkg install {pkg}",
}


def detect_manager() -> str | None:
    for bin_name, mgr in MGRS:
        if shutil.which(bin_name):
            # prefer real installer over dpkg/rpm query tools when apt/dnf present
            if bin_name in ("dpkg", "rpm") and (
                shutil.which("apt") or shutil.which("dnf") or shutil.which("yum")
            ):
                continue
            return mgr
    if platform.system() == "Windows":
        return "winget"
    if platform.system() == "Darwin":
        return "brew"
    return None


def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def plan_missing(manifest: dict) -> list:
    """Compare manifest vs this machine. Returns [{name, have, want, kind}]."""
    plan: list = []
    want_py = (manifest.get("python") or "")[:4]
    have_py = f"{sys.version_info.major}.{sys.version_info.minor}"
    if want_py and not want_py.startswith(have_py):
        plan.append({"name": f"python {manifest.get('python')}", "have": have_py, "want": manifest.get("python"), "kind": "lang"})
    if manifest.get("node") and not _have("node"):
        plan.append({"name": f"node {manifest.get('node_version') or manifest.get('node')}", "have": "missing", "want": manifest.get("node"), "kind": "lang"})
    for pkg in (manifest.get("pip_packages") or [])[:10]:
        base = pkg.split("==")[0].split(">=")[0].strip()
        try:
            __import__(base.replace("-", "_"))
        except Exception:
            plan.append({"name": f"pip {pkg}", "have": "missing", "want": pkg, "kind": "pip"})
    return plan


def install_cmd(manager: str | None, pkg: str) -> str:
    tmpl = INSTALL_TMPL.get(manager or "", "{pkg}")
    return tmpl.format(pkg=pkg)


def run_cmd(cmd: str) -> tuple:
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        return p.returncode, (p.stdout + p.stderr)[-2000:]
    except Exception as e:
        return 1, str(e)
