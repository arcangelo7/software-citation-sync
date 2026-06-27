# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from software_citation_action.config import CitationConfig, ProjectMetadata
from software_citation_action.discovery import discover_project_metadata, discover_version
from software_citation_action.software_heritage import archive_origin
from software_citation_action.sync import (
    check,
    write_citation_metadata,
    write_readme,
)

CITATION_PATH = Path("CITATION.cff")
README_PATH = Path("README.md")
ARCHIVE_TIMEOUT_SECONDS = 300
ARCHIVE_POLL_INTERVAL_SECONDS = 10


def main() -> None:
    root = Path.cwd()
    version = _discover_required_version(root)
    date_released = _current_date()
    origin_url = _current_repository_url()
    software_heritage_url = archive_origin(
        origin_url,
        timeout_seconds=ARCHIVE_TIMEOUT_SECONDS,
        poll_interval_seconds=ARCHIVE_POLL_INTERVAL_SECONDS,
    )
    project_metadata = _discover_required_project_metadata(root) if not CITATION_PATH.exists() else None
    citation_config = CitationConfig(
        citation_path=CITATION_PATH,
        readme_path=README_PATH,
        version=version,
        date_released=date_released,
        software_heritage_url=software_heritage_url,
    )

    citation_changed = write_citation_metadata(citation_config, project_metadata)
    readme_changed = write_readme(citation_config)
    check_result = check(citation_config)
    for error in check_result.errors:
        print(error)
    if not check_result.ok:
        raise SystemExit(1)

    _set_output("changed", str(citation_changed or readme_changed).lower())


def _discover_required_version(root: Path) -> str:
    version = discover_version(root)
    if version is None:
        msg = "Software version not found in package.json or pyproject.toml"
        raise ValueError(msg)
    return version


def _discover_required_project_metadata(root: Path) -> ProjectMetadata:
    project_metadata = discover_project_metadata(root)
    if project_metadata is None:
        msg = "Project metadata not found in package.json or pyproject.toml"
        raise ValueError(msg)
    return project_metadata


def _current_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _current_repository_url() -> str:
    return f"{os.environ['GITHUB_SERVER_URL'].rstrip('/')}/{os.environ['GITHUB_REPOSITORY']}"


def _set_output(name: str, value: str) -> None:
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as file:
        file.write(f"{name}={value}\n")


if __name__ == "__main__":
    main()
