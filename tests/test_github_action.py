# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

from pathlib import Path

import pytest
import requests_mock

from software_citation_action import github_action

SPDX_COPYRIGHT_NONE = "# SPDX-FileCopyrightText: NONE"
SPDX_LICENSE_CC0 = "# SPDX-License-" + "Identifier: CC0-1.0"
SAVE_URL = (
    "https://archive.softwareheritage.org/api/1/origin/save/git/url/https%3A%2F%2Fgithub.com%2Farcangelo7%2Framose/"
)
REQUEST_URL = "https://archive.softwareheritage.org/api/1/origin/save/2373061/"
SNAPSHOT_SWHID = "swh:1:snp:fc0b501f594531b2b8f694469cc38aed15897bbe"
SWH_URL = f"https://archive.softwareheritage.org/{SNAPSHOT_SWHID};origin=https://github.com/arcangelo7/ramose"


def mock_software_heritage_archive(requests_mock: requests_mock.Mocker) -> None:
    requests_mock.post(
        SAVE_URL,
        json={
            "request_url": REQUEST_URL,
            "save_task_status": "scheduled",
            "snapshot_swhid": "",
        },
    )
    requests_mock.get(
        REQUEST_URL,
        json={
            "request_url": REQUEST_URL,
            "save_task_status": "succeeded",
            "snapshot_swhid": SNAPSHOT_SWHID,
        },
    )


def test_action_updates_files_archives_and_sets_changed_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    requests_mock: requests_mock.Mocker,
) -> None:
    citation_path = tmp_path / "CITATION.cff"
    readme_path = tmp_path / "README.md"
    output_path = tmp_path / "github-output"
    citation_path.write_text(
        "\n".join(
            [
                SPDX_COPYRIGHT_NONE,
                SPDX_LICENSE_CC0,
                "",
                "cff-version: 1.2.0",
                "message: If you use this software, please cite it using these metadata.",
                "title: RAMOSE",
                "authors:",
                "  - family-names: Massari",
                "    given-names: Arcangelo",
                "",
            ],
        ),
        encoding="utf-8",
    )
    readme_path.write_text("# RAMOSE\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "ramose"\nversion = "2.8.0"\n', encoding="utf-8")
    mock_software_heritage_archive(requests_mock)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(github_action, "_current_date", lambda: "2026-06-25")
    monkeypatch.setattr(github_action, "ARCHIVE_POLL_INTERVAL_SECONDS", 0)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_REPOSITORY", "arcangelo7/ramose")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output_path))

    github_action.main()

    assert output_path.read_text(encoding="utf-8") == "\n".join(
        [
            "changed=true",
            "",
        ],
    )
    assert citation_path.read_text(encoding="utf-8") == "\n".join(
        [
            SPDX_COPYRIGHT_NONE,
            SPDX_LICENSE_CC0,
            "",
            "cff-version: 1.2.0",
            "message: If you use this software, please cite it using these metadata.",
            "title: RAMOSE",
            "authors:",
            "  - family-names: Massari",
            "    given-names: Arcangelo",
            "version: 2.8.0",
            "date-released: '2026-06-25'",
            f"url: {SWH_URL}",
            "",
        ],
    )
    assert readme_path.read_text(encoding="utf-8") == "\n".join(
        [
            "# RAMOSE",
            "",
            "<!-- software-citation-action:start -->",
            "To cite the latest version of this software (2.8.0), use this BibTeX entry:",
            "",
            "```bibtex",
            "@software{RAMOSE-2.8.0,",
            "author = {Massari, Arcangelo},",
            "title = {RAMOSE},",
            f"url = {{{SWH_URL}}},",
            "version = {2.8.0},",
            "year = {2026}",
            "}",
            "```",
            "<!-- software-citation-action:end -->",
            "",
        ],
    )


def test_action_creates_missing_citation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    requests_mock: requests_mock.Mocker,
) -> None:
    citation_path = tmp_path / "CITATION.cff"
    readme_path = tmp_path / "README.md"
    output_path = tmp_path / "github-output"
    readme_path.write_text("# RAMOSE\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        "\n".join(
            [
                "[project]",
                'name = "ramose"',
                'version = "2.8.0"',
                'authors = [{ name = "Arcangelo Massari", email = "github@a.arcangelomassari.com" }]',
                "",
            ],
        ),
        encoding="utf-8",
    )
    mock_software_heritage_archive(requests_mock)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(github_action, "_current_date", lambda: "2026-06-25")
    monkeypatch.setattr(github_action, "ARCHIVE_POLL_INTERVAL_SECONDS", 0)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_REPOSITORY", "arcangelo7/ramose")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output_path))

    github_action.main()

    assert output_path.read_text(encoding="utf-8") == "\n".join(
        [
            "changed=true",
            "",
        ],
    )
    assert citation_path.read_text(encoding="utf-8") == "\n".join(
        [
            "cff-version: 1.2.0",
            "message: If you use this software, please cite it using these metadata.",
            "title: ramose",
            "authors:",
            "  - name: Arcangelo Massari",
            "version: 2.8.0",
            "date-released: '2026-06-25'",
            f"url: {SWH_URL}",
            "",
        ],
    )
    assert readme_path.read_text(encoding="utf-8") == "\n".join(
        [
            "# RAMOSE",
            "",
            "<!-- software-citation-action:start -->",
            "To cite the latest version of this software (2.8.0), use this BibTeX entry:",
            "",
            "```bibtex",
            "@software{ramose-2.8.0,",
            "author = {Arcangelo Massari},",
            "title = {ramose},",
            f"url = {{{SWH_URL}}},",
            "version = {2.8.0},",
            "year = {2026}",
            "}",
            "```",
            "<!-- software-citation-action:end -->",
            "",
        ],
    )
