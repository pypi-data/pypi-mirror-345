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

from igniteops_sdk.api.projects.validate_project import sync as validate_project_sync

app = Typer(help="Validate commands.")


@app.command("project")
def validate_project(body: str = Argument(...), json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Validate project creation settings"""
    client = _sdk_client()
    resp = validate_project_sync(client=client, body=body if body is not None else UNSET)
    show(resp, raw_json=json, raw_yaml=yaml_)

