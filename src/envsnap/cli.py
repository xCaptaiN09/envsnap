"""EnvSnap CLI — save / open / share."""
import click
from rich import print as rprint


def _norm_out(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return "app.envsnap"
    if name.endswith(".envsnap"):
        return name
    # user types only name — we fix extension
    return f"{name}.envsnap"


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.version_option(
    package_name="envsnap",
    prog_name="envsnap",
    message="%(prog)s %(version)s",
    help="Show version.",
)
@click.option("-v", "--verbose", is_flag=True, help="Verbose output.")
@click.pass_context
def main(ctx, verbose):
    """Snapshot any dev env into one file."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    if ctx.invoked_subcommand is None:
        rprint("[bold]envsnap[/] — save / open / share")
        rprint("  envsnap save")
        rprint("  envsnap open <file>")
        rprint("  envsnap share <file>")


@main.command()
@click.option("-o", "--out", default=None, help="Snapshot name or file (extension auto-added).")
@click.option("--yes", is_flag=True, help="Non-interactive.")
@click.option("--allow-secrets", is_flag=True, help="Pack even if real secrets found (still never stores .env values).")
def save(out, yes, allow_secrets):
    """Snapshot this project."""
    import os

    from .detect import detect_project
    from .pack import find_secret_files, find_soft_secret_files, save_snapshot

    root = os.getcwd()
    m = detect_project(root)
    rprint(f"[green]✔ Found[/] py={m.get('python')} node={m.get('node')} run={m.get('run')}")
    default_name = os.path.basename(os.path.abspath(root)) or "app"
    if not yes:
        # 1) name only — no extension typing needed
        name = click.prompt("Snapshot name", default=out or default_name)
        out = _norm_out(name)
        # 2) multiple-choice for secrets: numbered list, pick one
        hard = find_secret_files(root, m.get("ignores", []))
        soft = find_soft_secret_files(root, m.get("ignores", []))
        if soft and not hard:
            rprint(f"[yellow]Note:[/] test-looking keys in {', '.join(soft[:3])} — packed, likely fixtures.")
        if hard and not allow_secrets:
            rprint(f"[red]Found possible secrets in:[/] {', '.join(hard[:5])}")
            rprint("  1) Skip those files and continue")
            rprint("  2) Cancel and let me remove them")
            pick = click.prompt("Choose", type=click.Choice(["1", "2"]), default="1")
            if pick == "2":
                rprint("Cancelled — remove secrets, then re-run save.")
                return
            path = save_snapshot(root, out, on_secret="skip")
        else:
            path = save_snapshot(root, out)
    else:
        out = _norm_out(out or default_name)
        mode = "skip" if allow_secrets else "ask"
        try:
            path = save_snapshot(root, out, on_secret=mode)
        except ValueError as e:
            rprint(f"[red]{e}[/] — re-run with --allow-secrets to skip those files, or remove them.")
            raise SystemExit(1)
    size = os.path.getsize(path)
    rprint(f"[green]✔ Saved → {path}[/] ({size // 1024} KB) — send it or run share")


@main.command(name="open")
@click.argument("path")
@click.option("--yes", is_flag=True, help="Non-interactive.")
@click.option("--docker", is_flag=True, help="Show Docker fallback.")
def open_cmd(path, yes, docker):
    """Restore a snapshot (file or http(s) link)."""
    import getpass
    import os
    import tempfile
    import urllib.request

    from .restore import inspect_snapshot, restore_full

    local = path
    if path.startswith("http://") or path.startswith("https://"):
        rprint("[cyan]Downloading snapshot...[/]")
        fd, local = tempfile.mkstemp(suffix=".envsnap")
        os.close(fd)
        try:
            urllib.request.urlretrieve(path, local)
        except Exception as e:
            rprint(f"[red]Can't reach sender:[/] {e}")
            rprint("Sender closed terminal (link dead?) or you're on different network.")
            rprint("Ask sender to run share again, or get the .envsnap file directly.")
            raise SystemExit(1)
    m = inspect_snapshot(local)
    rprint(f"[green]✔ Manifest:[/] py={m.get('python')} node={m.get('node')} run={m.get('run')}")
    vals: dict = {}
    for k in m.get("env_template", []):
        if yes:
            vals[k] = ""
        else:
            vals[k] = getpass.getpass(f"Enter {k} (kept private): ")
    dest = os.path.join(os.getcwd(), "restored-app")
    r = restore_full(local, dest)
    rprint(f"[green]✔ Restored → {r['dir']}[/] — next: cd {r['dir']} && ./setup.sh")
    if docker:
        rprint("[yellow]Docker fallback:[/] docker build -t envsnap-app . && docker run -p 8000:8000 envsnap-app")


@main.command()
@click.argument("path", required=False)
@click.option("--port", default=8765, show_default=True)
@click.option("--relay", is_flag=True, help="Try Cloudflare tunnel for NAT (needs cloudflared).")
def share(path, port, relay):
    """Share via temp sender-hosted link. Ctrl+C kills it."""
    import os
    import shutil
    import subprocess

    from .share import lan_ip, serve_file

    if not path:
        cands = [f for f in os.listdir(".") if f.endswith(".envsnap")]
        if len(cands) == 1:
            path = cands[0]
        elif not cands:
            rprint("[red]No .envsnap file here — run envsnap save first.[/]")
            return
        else:
            rprint(f"Found: {', '.join(cands)}")
            path = click.prompt("Which file", default=cands[0])
    srv, actual, token = serve_file(path, port=port)
    ip = lan_ip()
    url = f"http://{ip}:{actual}/{token}"
    rprint(f"[green]✔ Sharing {path}[/] — keep this terminal open, Ctrl+C to kill")
    rprint(f"  Friend runs: [bold]envsnap open {url}[/]")
    if relay:
        if not shutil.which("cloudflared"):
            rprint("[yellow]cloudflared not found — sharing on LAN only. Install cloudflared for far-away relay.[/]")
        else:
            p = subprocess.Popen(
                ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{actual}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            try:
                for line in p.stdout or []:
                    if "trycloudflare.com" in line:
                        import re

                        m = re.search(r"https://[^\s]*trycloudflare\.com", line)
                        if m:
                            rprint(f"  Relay (far-away): [bold]envsnap open {m.group(0)}/{token}[/]")
                            break
            finally:
                pass  # relay proc dies with Ctrl+C below
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        rprint("\n[red]Link dead.[/]")

