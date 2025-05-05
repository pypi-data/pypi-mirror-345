from importlib.metadata import PackageNotFoundError, version as _dist_version
from pathlib import Path
import re

def _get_version():
    try:
        return _dist_version("ignite-cli")
    except PackageNotFoundError:
        # fallback: read version from pyproject.toml
        py = Path(__file__).resolve().parents[2] / "pyproject.toml"
        if py.exists():
            text = py.read_text()
            m = re.search(r'^\s*version\s*=\s*"([^"]+)"', text, re.MULTILINE)
            if m:
                return m.group(1)
        return "0.0.0"

__version__ = _get_version()
