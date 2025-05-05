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

from igniteops_sdk.api.integrations.create_repository import sync as create_repository_sync
from igniteops_sdk.api.personal_access_tokens.create_pat import sync as create_pat_sync
from igniteops_sdk.api.projects.create_project import sync as create_project_sync
from igniteops_sdk.api.subscriptions.create_subscription import sync as create_subscription_sync

app = Typer(help="Create commands.")


@app.command("repository")
def create_repository(body: str = Argument(...), json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Create a repository integration"""
    client = _sdk_client()
    resp = create_repository_sync(client=client, body=body if body is not None else UNSET)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("pat")
def create_pat(body: str = Argument(...), json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Create a Personal Access Token (PAT)"""
    client = _sdk_client()
    resp = create_pat_sync(client=client, body=body if body is not None else UNSET)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("project")
def create_project(body: str = Argument(...), json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Create a new project"""
    client = _sdk_client()
    resp = create_project_sync(client=client, body=body if body is not None else UNSET)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("subscription")
def create_subscription(body: str = Argument(...), json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Create a new subscription"""
    client = _sdk_client()
    resp = create_subscription_sync(client=client, body=body if body is not None else UNSET)
    show(resp, raw_json=json, raw_yaml=yaml_)

