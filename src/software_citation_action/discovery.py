# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

import json
from pathlib import Path

import tomlkit
from tomlkit.items import Table


def discover_version(root: Path) -> str | None:
    package_json = root / "package.json"
    pyproject_toml = root / "pyproject.toml"
    if package_json.exists():
        data = json.loads(package_json.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            msg = "package.json must contain a JSON object"
            raise TypeError(msg)
        version = data["version"]
        if not isinstance(version, str):
            msg = "package.json `version` must be a string"
            raise TypeError(msg)
        return str(version)
    if pyproject_toml.exists():
        data = tomlkit.parse(pyproject_toml.read_text(encoding="utf-8"))
        project = data["project"]
        if not isinstance(project, Table):
            msg = "pyproject.toml `[project]` must be a table"
            raise TypeError(msg)
        version = project["version"]
        if not isinstance(version, str):
            msg = "pyproject.toml `project.version` must be a string"
            raise TypeError(msg)
        return str(version)
    return None
