"""EnvSnap CLI — save / open / share."""
import click
from rich import print as rprint


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Snapshot any dev env into one file."""
    if ctx.invoked_subcommand is None:
        rprint("[bold]envsnap[/] — save / open / share")
        rprint("  envsnap save -o app.envsnap")
        rprint("  envsnap open app.envsnap")
        rprint("  envsnap share app.envsnap")


@main.command()
@click.option("-o", "--out", default="app.envsnap", show_default=True)
@click.option("--yes", is_flag=True, help="Non-interactive.")
def save(out, yes):
    """Snapshot this project."""
    import os

    from .detect import detect_project
    from .pack import save_snapshot

    root = os.getcwd()
    m = detect_project(root)
    rprint(f"[green]✔ Found[/] py={m.get('python')} node={m.get('node')} run={m.get('run')}")
    if not yes:
        out = click.prompt("Name this snapshot", default=out)
    path = save_snapshot(root, out)
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

