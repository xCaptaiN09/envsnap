"""--air transport via magic-wormhole codes. No central storage, NAT-piercing."""
from __future__ import annotations


def is_code(s: str) -> bool:
    """Wormhole codes look like '7-purple-sunset' (num + words, dashes, no slash/dot)."""
    if not s or "/" in s or "\\" in s or "." in s or ":" in s:
        return False
    parts = s.strip().split("-")
    return len(parts) >= 2 and parts[0].isdigit() and all(p.isalpha() for p in parts[1:])


def ensure_wormhole() -> None:
    """Offer one-shot install on first --air use. No separate pip command to remember."""
    try:
        import wormhole  # noqa: F401
        return
    except Exception:
        pass
    import shutil

    if shutil.which("wormhole"):
        return
    try:
        import click
        from rich import print as rprint

        rprint("[yellow]Air needs magic-wormhole (one-time, ~50MB).[/]")
        if click.confirm("Install it now?", default=True):
            import subprocess
            import sys

            r = subprocess.run(
                [sys.executable, "-m", "pip", "install", "magic-wormhole>=0.12"],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if r.returncode == 0:
                rprint("[green]✔ Air ready.[/]")
                return
            rprint("[red]Install failed — run: pip install magic-wormhole[/]")
    except Exception:
        pass
    raise SystemExit("Need magic-wormhole for --air: pip install magic-wormhole")


def send_file(path: str) -> str:
    """Stream send. Prints code immediately, blocks until receiver grabs it."""
    ensure_wormhole()
    import re
    import subprocess

    p = subprocess.Popen(
        ["wormhole", "send", path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    code = None
    assert p.stdout is not None
    for line in p.stdout:
        print(line, end="")
        if code is None:
            m = re.search(r"wormhole receive (\S+)", line)
            if m:
                code = m.group(1)
            else:
                for tok in line.split():
                    if is_code(tok.strip()):
                        code = tok.strip()
                        break
        if code and ("Waiting for receiver" in line or "On the other computer" in line):
            break
    if not code:
        raise SystemExit("wormhole send failed — is magic-wormhole installed?")
    rc = p.wait()
    if rc != 0:
        raise SystemExit("send cancelled or failed.")
    return code


def recv_file(code: str, dest_dir: str = ".") -> str:
    ensure_wormhole()
    import subprocess

    p = subprocess.run(
        ["wormhole", "receive", "--accept-file", code],
        cwd=dest_dir,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if p.returncode != 0:
        raise SystemExit(f"receive failed: {(p.stdout + p.stderr)[-500:]}")
    return dest_dir
