"""Shared helpers for formatting CLI output."""
from __future__ import annotations

import json
import yaml
import datetime
from typing import Any

from rich.console import Console
from rich.pretty import pprint
from rich.table import Table

try:
    from igniteops_sdk.types import Unset, UNSET  # type: ignore
except ImportError:  # during bootstrap / tests
    class _Placeholder:
        pass

    Unset = _Placeholder  # type: ignore
    UNSET = _Placeholder  # type: ignore

console = Console()


def _to_serializable(obj: Any):
    """Recursively convert SDK models / complex objects to JSON-serialisable values."""

    # primitives
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # datetime
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()

    # ignite UNSET sentinel -> None
    if isinstance(obj, Unset):
        return None

    # mapping
    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items() if not isinstance(v, Unset)}

    # sequence
    if isinstance(obj, (list, tuple, set)):
        return [_to_serializable(i) for i in obj]

    # SDK / attrs model with to_dict
    if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
        return _to_serializable(obj.to_dict())

    # fallback to string repr
    return str(obj)


def show(data: Any, raw_json: bool = False, raw_yaml: bool = False):
    """Display *data* either as raw JSON or pretty rich output."""

    serializable = _to_serializable(data)

    if raw_yaml:
        console.print(yaml.safe_dump(serializable, sort_keys=False, width=120))
        return

    if raw_json:
        console.print_json(json.dumps(serializable, indent=2))
        return

    # Friendly human output
    if isinstance(serializable, dict):
        # unwrap items list pattern
        if "items" in serializable and isinstance(serializable["items"], list):
            show(serializable["items"], raw_json=raw_json, raw_yaml=raw_yaml)
            return

        # key/value listing
        table = Table(show_header=False, box=None, padding=(0,1))
        for k, v in serializable.items():
            table.add_row(str(k), str(v))
        console.print(table)
        return

    if isinstance(serializable, list):
        if not serializable:
            console.print("[dim]No items.[/dim]")
            return

        # list of dicts
        if len(serializable) == 1 and isinstance(serializable[0], dict):
            # show as key/value table for consistency
            show(serializable[0], raw_json=raw_json, raw_yaml=raw_yaml)
            return

        if all(isinstance(i, dict) for i in serializable):
            # determine if fits nicely in a table
            first_keys = list(serializable[0].keys())
            extra_keys = [k for item in serializable[1:] for k in item.keys() if k not in first_keys]
            columns = first_keys + extra_keys

            # heuristic: table okay if ≤10 columns and every cell len ≤30
            simple = len(columns) <= 10
            if simple:
                for item in serializable:
                    for col in columns:
                        val = str(item.get(col, ""))
                        if len(val) > 30:
                            simple = False
                            break
                    if not simple:
                        break

            if simple:
                table = Table(box=None, show_header=True, header_style="bold")
                for col in columns:
                    table.add_column(col, style="yellow", overflow="fold", no_wrap=False)

                for item in serializable:
                    row = [str(item.get(col, "")) for col in columns]
                    table.add_row(*row)
                console.print(table)
            else:
                # fallback YAML per item
                for item in serializable:
                    console.print("---")
                    console.print(yaml.safe_dump(item, sort_keys=False, width=120))
            return

        # list of scalars or models -> one per line
        for elem in serializable:
            console.print(f"- {elem}")
        return

    # fallback raw YAML for other structured data
    if isinstance(serializable, (dict, list)):
        console.print(yaml.safe_dump(serializable, sort_keys=False, width=120))
        return

    # fallback pretty print for scalars / models
    if hasattr(data, "to_dict"):
        pprint(data.to_dict())
    else:
        pprint(data)
