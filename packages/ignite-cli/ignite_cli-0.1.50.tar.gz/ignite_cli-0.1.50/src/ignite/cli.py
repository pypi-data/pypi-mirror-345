"""Main Typer application for IgniteOps CLI."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional, List, Tuple

# ensure igniteops_sdk importable when running installed package (installed under site-packages root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import click
from rich.console import Console
import typer
from typer import Argument, Option, Typer
from typer.main import TyperGroup
from rich.pretty import pprint

from .client import Client, TOKEN_FILE
from .auth import BrowserAuthenticator
from . import __version__
from .utils.output import show

console = Console()

# Typer root app (define early to allow decorators)
app = Typer(help="IgniteOps command-line interface.", rich_markup_mode="rich")

# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def die(message: str, code: int = 1):
    console.print(f"[bold red]Error:[/bold red] {message}")
    sys.exit(code)


# ---------------------------------------------------------------------------
# Auth commands (root level)
# ---------------------------------------------------------------------------

# real implementation
@app.command(rich_help_panel="Authentication")
def login(
    browser: bool = Option(True, "--browser/--no-browser", help="Use interactive browser flow"),
    token: Optional[str] = Option(None, "--token", help="Provide a JWT token directly"),
    api_key: Optional[str] = Option(None, "--api-key", help="Provide an API key for CI/non-interactive environments"),
):
    """Authenticate CLI.

    Default is interactive browser login (Cognito PKCE). You can also pass a
    pre-issued JWT or API key via --token or --api-key for CI/non-interactive environments.
    """

    client = Client()
    if api_key:
        client.save_token(f"PAT {api_key}")
        console.print("[green]API key saved.[/green]")
        return
    if token:
        client.save_token(token)
        console.print("[green]Token saved.[/green]")
        return

    if not browser:
        die("--no-browser requires --token or --api-key.")

    BrowserAuthenticator().login()


@app.command(rich_help_panel="Authentication")
def logout():
    """Remove stored token."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        console.print("[yellow]Token removed.[/yellow]")
    else:
        console.print("No token stored.")


@app.command("version", rich_help_panel="Info")
def version(
    json_: bool = Option(False, "--json", help="Raw JSON output"),
    yaml_: bool = Option(False, "--yaml", help="Raw YAML output"),
):
    """Show CLI version."""
    show({"version": __version__}, raw_json=json_, raw_yaml=yaml_)


# ---------------------------------------------------------------------------
# Core sample commands
# ---------------------------------------------------------------------------

# status alias – import underlying function
from ignite.commands.get import get_status as _get_status

# Alias for backward compatibility
@app.command(hidden=True)
def status(
    json: bool = Option(False, "--json", help="Raw JSON output"),
    yaml_: bool = Option(False, "--yaml", help="Raw YAML"),
):
    """Alias for 'get status'."""
    _get_status(json=json, yaml_=yaml_)


# ---------------------------------------------------------------------------
# Dynamic command loading (generated via scripts/gen_cli.py)
# ---------------------------------------------------------------------------

import pkgutil
from importlib import import_module

# built-in commands (handwritten) removed: legacy 'projects' now handled via generated 'get'
_commands_dir = Path(__file__).parent / "commands"
for mod_info in pkgutil.iter_modules([str(_commands_dir)]):
    mod_name = mod_info.name
    if mod_name in {"__init__", "projects"}:
        continue
    module = import_module(f"ignite.commands.{mod_name}")
    if not hasattr(module, "app"):
        continue

    # Always expose verb namespace (even if only 1 subcommand) to keep "verb object" pattern
    sub_app = module.app
    app.add_typer(sub_app, name=mod_name.replace("_", "-"), rich_help_panel="Actions")
