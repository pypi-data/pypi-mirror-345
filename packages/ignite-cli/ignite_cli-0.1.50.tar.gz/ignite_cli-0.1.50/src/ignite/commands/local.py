from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional, List

import yaml
import typer
from rich.console import Console

from ignite.cli import die
from ignite.client import Client

app = typer.Typer(help="Local operations", rich_help_panel="Local")
console = Console()


def _load_config(config_path: Path) -> dict:
    if not config_path.exists():
        die(f"Config file '{config_path}' not found.")
    try:
        return yaml.safe_load(config_path.read_text()) or {}
    except Exception as e:
        die(f"Failed to read config file: {e}")


# ---------------------------------------------------------------------------
# Local build command
# ---------------------------------------------------------------------------
@app.command("build", context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
def build(ctx: typer.Context,
    config: Path = typer.Option(Path("igniteops.yaml"), "--config", "-c", help="Path to local config file."),
    wrapper: Optional[Path] = typer.Option(None, "--wrapper", help="Path to build wrapper executable."),
    tasks: Optional[List[str]] = typer.Option(None, "--task", "-t", help="Tasks to execute. Can be repeated."),
):
    """Run local build as defined in config."""
    cfg = _load_config(config)
    tool = cfg.get("type")
    project_id = cfg.get("projectId")
    # infer build tool if not explicitly set
    if not tool:
        if project_id:
            client = Client()
            try:
                project = client.get(f"/projects/{project_id}")
            except Exception as e:
                die(f"Failed to fetch project '{project_id}': {e}")
            language = project.get("language")
            if language == "java":
                tool = "gradle"
            else:
                die(f"Unsupported project language '{language}' for local build.")
        else:
            die("Config file must include 'type' or 'projectId'.")
    if tool != "gradle":
        die(f"Unsupported build type '{tool}'. Only 'gradle' is supported.")
    gradle_cfg = cfg.get("gradle", {})
    exec_path = wrapper or Path(gradle_cfg.get("wrapper", "./gradlew"))
    if not exec_path.exists():
        die(f"Wrapper executable '{exec_path}' not found.")
    # determine tasks: use CLI-provided or config default
    cmd_tasks = tasks if tasks else gradle_cfg.get("tasks", ["build"])
    # forward extra flags to build tool
    extra_args = ctx.args
    cmd = [str(exec_path)] + cmd_tasks + extra_args
    console.print(f"[blue]Running:[/blue] {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        die(f"Build failed with exit code {e.returncode}")
    console.print("[green]Build succeeded.[/green]")


# ---------------------------------------------------------------------------
# Local test command
# ---------------------------------------------------------------------------
@app.command("test", context_settings={"ignore_unknown_options": True, "allow_extra_args": True})
def test(
    ctx: typer.Context,
    config: Path = typer.Option(Path("igniteops.yaml"), "--config", "-c", help="Path to local config file."),
    wrapper: Optional[Path] = typer.Option(None, "--wrapper", help="Path to build wrapper executable."),
    tasks: Optional[List[str]] = typer.Option(None, "--task", "-t", help="Tasks to execute. Can be repeated."),
):
    """Run local tests as defined in config."""
    cfg = _load_config(config)
    tool = cfg.get("type")
    project_id = cfg.get("projectId")
    # infer tool if not set
    if not tool:
        if project_id:
            client = Client()
            try:
                project = client.get(f"/projects/{project_id}")
            except Exception as e:
                die(f"Failed to fetch project '{project_id}': {e}")
            language = project.get("language")
            if language == "java":
                tool = "gradle"
            else:
                die(f"Unsupported project language '{language}' for local test.")
        else:
            die("Config file must include 'type' or 'projectId'.")
    if tool != "gradle":
        die(f"Unsupported test type '{tool}'. Only 'gradle' is supported.")
    gradle_cfg = cfg.get("gradle", {})
    exec_path = wrapper or Path(gradle_cfg.get("wrapper", "./gradlew"))
    if not exec_path.exists():
        die(f"Wrapper executable '{exec_path}' not found.")
    # determine test tasks
    cmd_tasks = tasks if tasks else ["test"]
    # forward extra flags
    extra_args = ctx.args
    cmd = [str(exec_path)] + cmd_tasks + extra_args
    console.print(f"[blue]Running tests:[/blue] {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        die(f"Tests failed with exit code {e.returncode}")
    console.print("[green]Tests succeeded.[/green]")
