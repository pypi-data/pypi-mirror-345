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

from igniteops_sdk.api.integrations.delete_repository import sync as delete_repository_sync
from igniteops_sdk.api.projects.delete_project import sync as delete_project_sync

app = Typer(help="Delete commands.")


@app.command("repository")
def delete_repository(repo_id: str = Argument(...), json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Delete a repository integration"""
    client = _sdk_client()
    resp = delete_repository_sync(client=client, repo_id=repo_id if repo_id is not None else UNSET)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("project")
def delete_project(project_id: str = Argument(...), json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Delete a project"""
    client = _sdk_client()
    resp = delete_project_sync(client=client, project_id=project_id if project_id is not None else UNSET)
    show(resp, raw_json=json, raw_yaml=yaml_)

