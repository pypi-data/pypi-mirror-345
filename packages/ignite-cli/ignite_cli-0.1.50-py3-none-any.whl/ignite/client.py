"""Lightweight API client wrapping requests with auth and retries."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from pydantic import BaseModel
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_BASE = os.getenv("IGNITE_API", "https://api.igniteops.io")
TOKEN_FILE = Path.home() / ".ignite_token"


class APIError(Exception):
    """Raised on non-2xx responses."""

    def __init__(self, status_code: int, message: str):
        super().__init__(f"APIError {status_code}: {message}")
        self.status_code = status_code
        self.message = message


class Client:
    """Simple HTTP client with bearer auth and automatic retries."""

    def __init__(self, token: Optional[str] = None):
        self._session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        self._session.mount("https://", HTTPAdapter(max_retries=retries))

        self.token = token or self._load_token()

    # ---------------------------------------------------------------------
    # Token helpers
    # ---------------------------------------------------------------------
    def _load_token(self) -> Optional[str]:
        if TOKEN_FILE.exists():
            return TOKEN_FILE.read_text().strip()
        return None

    def save_token(self, token: str) -> None:
        TOKEN_FILE.write_text(token)
        TOKEN_FILE.chmod(0o600)
        self.token = token

    # ---------------------------------------------------------------------
    # Request wrappers
    # ---------------------------------------------------------------------
    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{API_BASE}{path}"
        headers = kwargs.pop("headers", {})
        if self.token:
            if self.token.startswith("PAT "):
                headers["Authorization"] = self.token
            else:
                headers["Authorization"] = f"Bearer {self.token}"
        headers.setdefault("Accept", "application/json")
        if "json" in kwargs:
            headers.setdefault("Content-Type", "application/json")
        resp = self._session.request(method, url, headers=headers, timeout=30, **kwargs)
        if resp.status_code == 401:
            from rich.console import Console
            console = Console()
            console.print("[bold red]Error:[/bold red] Unauthorized or expired token. Please run 'ignite login' to refresh credentials.")
            sys.exit(1)
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("message")
            except Exception:
                detail = resp.text
            raise APIError(resp.status_code, detail)
        if resp.headers.get("Content-Type", "").startswith("application/json"):
            return resp.json()
        return resp.text

    def get(self, path: str, **kwargs: Any):
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any):
        return self._request("POST", path, **kwargs)

    def delete(self, path: str, **kwargs: Any):
        return self._request("DELETE", path, **kwargs)
