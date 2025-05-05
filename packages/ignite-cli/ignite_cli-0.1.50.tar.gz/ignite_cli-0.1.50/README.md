# IgniteOps CLI

A modern, *batteries-included* command-line interface for the [IgniteOps](https://igniteops.io) platform.

![PyPI](https://img.shields.io/pypi/v/ignite-cli.svg) ![License](https://img.shields.io/github/license/IgniteOps-io/cli)

IgniteOps CLI lets you create, validate, and manage your cloud-native applications entirely from the terminal – no web console required.

---

## Features

* 🔑 **Secure authentication** – browser-based or headless token flow
* 🚀 **Project lifecycle** – create, validate, deploy and monitor projects
* 📦 **First-class CI/CD** – integrate seamlessly into pipelines
* 🖇️ **Dynamic commands** – CLI is auto-generated from IgniteOps OpenAPI so it’s always in sync
* 🌈 **Rich UI** – colourful output, tables & spinners powered by `rich`

---

## Installation

```bash
# Install from PyPI (recommended)
pip install ignite-cli

# Or keep it isolated with pipx
pipx install ignite-cli
```

Requires **Python ≥ 3.8**.

---

## Quickstart

```bash
# 1. Authenticate (opens browser)
ignite login

# 2. List your projects
ignite get projects

# 3. Create a project in one go
ignite create project \
  --name MyApp \
  --language python \
  --framework fastapi

# 4. Validate project config before deployment
ignite validate project -f project.yaml --json
```

For the full command reference run:

```bash
ignite --help
```

---

## Authentication

The CLI stores a short-lived JWT in `~/.config/ignite/token.json` (macOS/Linux) or `%APPDATA%\Ignite\token.json` (Windows).

* **Interactive** (default): `ignite login` launches a browser and completes an OAuth PKCE flow.
* **Headless / CI**: supply a token directly
  ```bash
  ignite login --no-browser --token $IGNITE_TOKEN
  ```

---

## Documentation

Comprehensive docs & tutorials live at <https://igniteops.io/docs/cli>.

---

## License

This project is distributed under the MIT License – see `LICENSE` for full text.
