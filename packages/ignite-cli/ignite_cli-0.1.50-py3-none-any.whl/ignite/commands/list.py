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

from igniteops_sdk.api.personal_access_tokens.list_pats import sync as list_pats_sync

app = Typer(help="List commands.")


@app.command("pats")
def list_pats(json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """List PATs for the authenticated user"""
    client = _sdk_client()
    resp = list_pats_sync(client=client)
    show(resp, raw_json=json, raw_yaml=yaml_)

