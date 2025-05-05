"""Authentication helpers for IgniteOps CLI.

Interactive login uses Cognito Hosted UI with PKCE.
"""
from __future__ import annotations

import base64
import hashlib
import http.server
import os
import secrets
import threading
import time
import urllib.parse as urlparse
import webbrowser
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests
from rich.console import Console

console = Console()

HOME_DIR = Path.home() / ".ignite"
CRED_FILE = HOME_DIR / "credentials.json"

AUTH_DOMAIN = os.getenv("IGNITE_AUTH_DOMAIN", "https://auth.igniteops.io")
CLIENT_ID = os.getenv("IGNITE_CLIENT_ID", "2h6uf9mubucn5kd6lr8hl4ea0q")  # must be configured
SCOPES = "openid email profile"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _generate_pkce_pair() -> Tuple[str, str]:
    verifier = _b64url(secrets.token_bytes(32))  # 43-128 chars
    challenge = _b64url(hashlib.sha256(verifier.encode()).digest())
    return verifier, challenge


class _CodeHandler(http.server.BaseHTTPRequestHandler):
    """Minimal handler that captures \"code\" and signals main thread."""

    server_version = "IgniteAuth/1.0"
    tokens: Dict[str, str] | None = None
    state_expected: str | None = None
    event: threading.Event | None = None

    def do_GET(self):  # noqa: N802
        query = urlparse.urlparse(self.path).query
        params = urlparse.parse_qs(query)
        if params.get("state", [None])[0] != _CodeHandler.state_expected:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid state")
            return
        code = params.get("code", [None])[0]
        if not code:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing code")
            return
        _CodeHandler.tokens = {"code": code}
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        html = (
            """
            <!DOCTYPE html>
            <html lang='en'>
              <head>
                <meta charset='utf-8'/>
                <title>IgniteOps CLI Login</title>
                <style>
                  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:#f4f4f4;color:#333;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
                  .card{background:#fff;padding:2rem 3rem;border-radius:8px;box-shadow:0 2px 6px rgba(0,0,0,.1);text-align:center}
                  h1{margin-top:0;color:#ff6600}
                </style>
              </head>
              <body>
                <div class='card'>
                  <h1>Login Successful 🎉</h1>
                  <p>You can return to your terminal.</p>
                </div>
              </body>
            </html>
            """
        )
        self.wfile.write(html.encode())
        if _CodeHandler.event:
            _CodeHandler.event.set()

    def log_message(self, format: str, *args):  # noqa: A002
        return  # silence


class BrowserAuthenticator:
    """Handles interactive browser-based login using PKCE."""

    def __init__(self, client_id: str | None = None):
        self.client_id = client_id or CLIENT_ID
        if not self.client_id:
            raise RuntimeError("Cognito Client ID is missing. Set IGNITE_CLIENT_ID env var or hard-code in auth module.")

    def login(self) -> Dict[str, str]:
        verifier, challenge = _generate_pkce_pair()
        state = secrets.token_urlsafe(16)

        FIXED_PORT = 53682
        try:
            server = http.server.HTTPServer(("localhost", FIXED_PORT), _CodeHandler)
            port = FIXED_PORT
        except OSError:
            # Fallback to an ephemeral port if the fixed one is occupied; user
            # must ensure additional callback URI is added if this happens.
            server = http.server.HTTPServer(("localhost", 0), _CodeHandler)
            port = server.server_port

        redirect_uri = f"http://localhost:{port}/callback"

        authorize_url = (
            f"{AUTH_DOMAIN}/oauth2/authorize?" + urlparse.urlencode(
                {
                    "client_id": self.client_id,
                    "response_type": "code",
                    "scope": SCOPES,
                    "redirect_uri": redirect_uri,
                    "code_challenge": challenge,
                    "code_challenge_method": "S256",
                    "state": state,
                }
            )
        )

        console.print("[cyan]Opening browser for login...[/cyan]")
        console.print(authorize_url)
        try:
            webbrowser.open(authorize_url, new=2)
        except Exception:
            console.print("Unable to open browser automatically. Please copy URL above.")

        _CodeHandler.state_expected = state
        event = threading.Event()
        _CodeHandler.event = event
        threading.Thread(target=server.serve_forever, daemon=True).start()

        # Wait for callback (max 180s)
        if not event.wait(180):
            server.shutdown()
            raise TimeoutError("Timed out waiting for browser login")
        server.shutdown()
        code = _CodeHandler.tokens["code"]  # type: ignore[index]

        # Exchange code for tokens
        token_resp = requests.post(
            f"{AUTH_DOMAIN}/oauth2/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "code": code,
                "redirect_uri": redirect_uri,
                "code_verifier": verifier,
            },
            timeout=30,
        )
        token_resp.raise_for_status()
        tokens = token_resp.json()
        self._save(tokens)
        # store id_token preferred, fallback to access_token.
        from ..client import Client

        bearer = tokens.get("id_token") or tokens.get("access_token", "")
        Client().save_token(bearer)
        console.print("[green]Login successful![/green]")
        return tokens

    # ------------------------------------------------------------------
    def _save(self, data: Dict[str, str]):
        HOME_DIR.mkdir(exist_ok=True)
        import json, time  # noqa: WPS433

        data["saved_at"] = int(time.time())
        CRED_FILE.write_text(json.dumps(data, indent=2))
        CRED_FILE.chmod(0o600)
