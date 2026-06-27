# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

import re
from pathlib import Path

START_MARKER = "<!-- software-citation-action:start -->"
END_MARKER = "<!-- software-citation-action:end -->"
BIBTEX_REFERENCE_PATTERN = re.compile(r"[^0-9A-Za-z_.:-]+")


def bibtex_reference(title: str, version: str) -> str:
    return BIBTEX_REFERENCE_PATTERN.sub("-", f"{title}-{version}").strip("-")


def expected_readme_block(version: str, bibtex: str) -> str:
    return "\n".join(
        [
            START_MARKER,
            f"To cite the latest version of this software ({version}), use this BibTeX entry:",
            "",
            "```bibtex",
            bibtex,
            "```",
            END_MARKER,
        ],
    )


def readme_block_matches(path: Path, version: str, bibtex: str) -> bool:
    content = path.read_text(encoding="utf-8")
    return _current_block(content) == expected_readme_block(version, bibtex)


def write_readme_block(path: Path, version: str, bibtex: str) -> bool:
    content = path.read_text(encoding="utf-8")
    block = expected_readme_block(version, bibtex)
    current_block = _current_block(content)
    if current_block == block:
        return False
    if current_block is None:
        new_content = content.rstrip() + "\n\n" + block + "\n"
    else:
        new_content = content.replace(current_block, block)
    path.write_text(new_content, encoding="utf-8")
    return True


def _current_block(content: str) -> str | None:
    start = content.find(START_MARKER)
    end = content.find(END_MARKER)
    if start == -1 and end == -1:
        return None
    if start == -1 or end == -1 or end < start:
        msg = "README citation block markers are incomplete or out of order"
        raise ValueError(msg)
    return content[start : end + len(END_MARKER)]
