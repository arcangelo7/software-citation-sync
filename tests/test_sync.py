# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

from pathlib import Path

import pytest

from software_citation_action.config import CitationConfig, ProjectMetadata
from software_citation_action.readme import write_readme_block
from software_citation_action.sync import check, write_citation_metadata, write_readme

SPDX_COPYRIGHT_NONE = "# SPDX-FileCopyrightText: NONE"
SPDX_LICENSE_CC0 = "# SPDX-License-" + "Identifier: CC0-1.0"
SWH_URL = (
    "https://archive.softwareheritage.org/swh:1:snp:fc0b501f594531b2b8f694469cc38aed15897bbe"
    ";origin=https://github.com/arcangelo7/ramose"
)


def test_write_updates_citation_and_readme(tmp_path: Path) -> None:
    citation_path = tmp_path / "CITATION.cff"
    readme_path = tmp_path / "README.md"
    # REUSE-IgnoreStart
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
                "version: 2.0.0",
                "date-released: '2026-04-03'",
                "",
            ],
        ),
        encoding="utf-8",
    )
    # REUSE-IgnoreEnd
    readme_path.write_text("# RAMOSE\n", encoding="utf-8")

    config = CitationConfig(
        citation_path=citation_path,
        readme_path=readme_path,
        version="2.8.0",
        date_released="2026-06-25",
        software_heritage_url=SWH_URL,
    )
    citation_changed = write_citation_metadata(config)
    readme_changed = write_readme(config)

    assert citation_changed is True
    assert readme_changed is True
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


def test_write_creates_missing_citation(tmp_path: Path) -> None:
    citation_path = tmp_path / "CITATION.cff"

    citation_changed = write_citation_metadata(
        CitationConfig(
            citation_path=citation_path,
            readme_path=tmp_path / "README.md",
            version="2.8.0",
            date_released="2026-06-25",
            software_heritage_url=SWH_URL,
        ),
        ProjectMetadata(
            title="ramose",
            authors=("Arcangelo Massari",),
        ),
    )

    assert citation_changed is True
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


def test_check_reports_readme_block_error(tmp_path: Path) -> None:
    citation_path = tmp_path / "CITATION.cff"
    readme_path = tmp_path / "README.md"
    # REUSE-IgnoreStart
    citation_path.write_text(
        "\n".join(
            [
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
        ),
        encoding="utf-8",
    )
    # REUSE-IgnoreEnd
    readme_path.write_text("# RAMOSE\n", encoding="utf-8")

    result = check(
        CitationConfig(
            citation_path=citation_path,
            readme_path=readme_path,
            version="2.8.0",
            date_released="2026-06-25",
            software_heritage_url=SWH_URL,
        ),
    )

    assert result.errors == (f"{readme_path} citation block is out of date",)


def test_write_readme_rejects_incomplete_markers(tmp_path: Path) -> None:
    readme_path = tmp_path / "README.md"
    readme_path.write_text("# RAMOSE\n\n<!-- software-citation-action:start -->\n", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match=r"^README citation block markers are incomplete or out of order$",
    ) as exc_info:
        write_readme_block(readme_path, "2.8.0", "@software{RAMOSE-2.8.0}")

    assert str(exc_info.value) == "README citation block markers are incomplete or out of order"
