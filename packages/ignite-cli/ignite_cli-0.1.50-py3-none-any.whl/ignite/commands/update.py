from __future__ import annotations
"""Generated, do not edit."""
from typer import Typer, Option, Argument
from igniteops_sdk.client import AuthenticatedClient
from igniteops_sdk.types import UNSET
from ignite.utils.output import show
from ignite.client import API_BASE, TOKEN_FILE

def _sdk_client() -> AuthenticatedClient:
    token = None
    try:
        if TOKEN_FILE.exists():
            token = TOKEN_FILE.read_text().strip()
    except Exception:
        pass
    return AuthenticatedClient(base_url=API_BASE, token=token or "")

from igniteops_sdk.api.projects.update_project import sync as update_project_sync

app = Typer(help="Update commands.")


@app.command("project")
def update_project(project_id: str = Argument(...), body: str = Argument(...), json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Update a project (favourite/unfavourite)"""
    client = _sdk_client()
    resp = update_project_sync(client=client, project_id=project_id if project_id is not None else UNSET, body=body if body is not None else UNSET)
    show(resp, raw_json=json, raw_yaml=yaml_)

