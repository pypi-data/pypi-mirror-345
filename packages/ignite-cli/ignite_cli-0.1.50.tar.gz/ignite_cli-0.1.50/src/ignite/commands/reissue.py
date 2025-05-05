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

from igniteops_sdk.api.personal_access_tokens.reissue_pat import sync as reissue_pat_sync

app = Typer(help="Reissue commands.")


@app.command("pat")
def reissue_pat(pat_id: str = Argument(...), json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Re-issue a Personal Access Token (generate a new secret)"""
    client = _sdk_client()
    resp = reissue_pat_sync(client=client, pat_id=pat_id if pat_id is not None else UNSET)
    show(resp, raw_json=json, raw_yaml=yaml_)

