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
def save(out):
    """Snapshot this project."""
    import os

    from .pack import save_snapshot

    path = save_snapshot(os.getcwd(), out)
    rprint(f"[green]✔ Saved → {path}[/]")


@main.command(name="open")
@click.argument("path")
def open_cmd(path):
    """Restore a snapshot."""
    from .restore import inspect_snapshot

    m = inspect_snapshot(path)
    rprint(f"[green]✔ Manifest:[/] py={m.get('python')} node={m.get('node')} run={m.get('run')}")
    if m.get("env_template"):
        rprint(f"[yellow]Need env keys:[/] {', '.join(m['env_template'])}")


@main.command()
@click.argument("path", required=False)
def share(path):
    """Share via temp link (V0 stub)."""
    rprint("[yellow]V0:[/] send the .envsnap file directly (Telegram/Drive).")
    rprint("Relay temp links land in V0.2 — direct P2P first.")
    if path:
        rprint(f"File: {path}")

