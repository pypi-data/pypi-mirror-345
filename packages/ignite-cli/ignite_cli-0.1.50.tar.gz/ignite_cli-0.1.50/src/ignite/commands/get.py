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

from igniteops_sdk.api.integrations.get_repositories import sync as get_repositories_sync
from igniteops_sdk.api.misc.get_mock_auth import sync as get_mock_auth_sync
from igniteops_sdk.api.misc.get_open_api_spec import sync as get_open_api_spec_sync
from igniteops_sdk.api.misc.get_status import sync as get_status_sync
from igniteops_sdk.api.projects.get_project import sync as get_project_sync
from igniteops_sdk.api.projects.get_project_activity import sync as get_project_activity_sync
from igniteops_sdk.api.projects.get_projects import sync as get_projects_sync
from igniteops_sdk.api.subscriptions.get_payment_method import sync as get_payment_method_sync
from igniteops_sdk.api.subscriptions.get_subscription import sync as get_subscription_sync
from igniteops_sdk.api.subscriptions.get_subscription_plans import sync as get_subscription_plans_sync

app = Typer(help="Get commands.")


@app.command("repositories")
def get_repositories(json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Get user's repository integrations"""
    client = _sdk_client()
    resp = get_repositories_sync(client=client)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("mock-auth")
def get_mock_auth(json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Authenticated mock endpoint"""
    client = _sdk_client()
    resp = get_mock_auth_sync(client=client)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("open-api-spec")
def get_open_api_spec(json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Download the public OpenAPI specification"""
    client = _sdk_client()
    resp = get_open_api_spec_sync(client=client)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("status")
def get_status(json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Returns API status"""
    client = _sdk_client()
    resp = get_status_sync(client=client)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("project")
def get_project(project_id: str = Argument(...), json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Get a project"""
    client = _sdk_client()
    resp = get_project_sync(client=client, project_id=project_id if project_id is not None else UNSET)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("project-activity")
def get_project_activity(project_id: str = Argument(...), limit: str = Option(None), next_token: str = Option(None), json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Get activity for a project"""
    client = _sdk_client()
    resp = get_project_activity_sync(client=client, project_id=project_id if project_id is not None else UNSET, limit=limit if limit is not None else UNSET, next_token=next_token if next_token is not None else UNSET)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("projects")
def get_projects(limit: str = Option(None), next_token: str = Option(None), language: str = Option(None), sort_by: str = Option(None), sort_order: str = Option(None), favs: str = Option(None), json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Get user's projects"""
    client = _sdk_client()
    resp = get_projects_sync(client=client, limit=limit if limit is not None else UNSET, next_token=next_token if next_token is not None else UNSET, language=language if language is not None else UNSET, sort_by=sort_by if sort_by is not None else UNSET, sort_order=sort_order if sort_order is not None else UNSET, favs=favs if favs is not None else UNSET)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("payment-method")
def get_payment_method(json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Get user's payment method"""
    client = _sdk_client()
    resp = get_payment_method_sync(client=client)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("subscription")
def get_subscription(json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Get user's active subscription"""
    client = _sdk_client()
    resp = get_subscription_sync(client=client)
    show(resp, raw_json=json, raw_yaml=yaml_)


@app.command("subscription-plans")
def get_subscription_plans(json: bool = Option(False, '--json'), yaml_: bool = Option(False, '--yaml', help='Raw YAML')):
    """Gets available subscription plans"""
    client = _sdk_client()
    resp = get_subscription_plans_sync(client=client)
    show(resp, raw_json=json, raw_yaml=yaml_)

