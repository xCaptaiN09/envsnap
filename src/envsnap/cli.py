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


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Snapshot any dev env into one file."""
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
    """Restore a snapshot."""
    import getpass
    import os

    from .restore import inspect_snapshot, restore_full

    m = inspect_snapshot(path)
    rprint(f"[green]✔ Manifest:[/] py={m.get('python')} node={m.get('node')} run={m.get('run')}")
    vals: dict = {}
    for k in m.get("env_template", []):
        if yes:
            vals[k] = ""
        else:
            vals[k] = getpass.getpass(f"Enter {k} (kept private): ")
    dest = os.path.join(os.getcwd(), "restored-app")
    r = restore_full(path, dest)
    rprint(f"[green]✔ Restored → {r['dir']}[/] — next: cd {r['dir']} && ./setup.sh")
    if docker:
        rprint("[yellow]Docker fallback:[/] docker build -t envsnap-app . && docker run -p 8000:8000 envsnap-app")


@main.command()
@click.argument("path", required=False)
def share(path):
    """Share via temp link (V0 stub)."""
    rprint("[yellow]V0:[/] send the .envsnap file directly (Telegram/Drive).")
    rprint("Relay temp links land in V0.2 — direct P2P first.")
    if path:
        rprint(f"File: {path}")

