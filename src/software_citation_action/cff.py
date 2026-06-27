# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

import copy
import subprocess
from io import StringIO
from pathlib import Path
from urllib.parse import quote

from cffconvert.citation import Citation  # type: ignore[reportMissingTypeStubs]
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from software_citation_action.config import CitationConfig


def load_citation(path: Path) -> CommentedMap:
    yaml = YAML()
    with path.open(encoding="utf-8") as file:
        data = yaml.load(file)
    if not isinstance(data, CommentedMap):
        msg = f"{path} must contain a YAML mapping"
        raise TypeError(msg)
    return data


def render_citation(data: CommentedMap) -> str:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 4096
    buffer = StringIO()
    yaml.dump(data, buffer)
    return buffer.getvalue()


def render_citation_bibtex(data: CommentedMap, reference: str, url: str) -> str:
    bibtex_data = copy.deepcopy(data)
    bibtex_data["url"] = url
    citation = Citation(render_citation(bibtex_data))
    return citation.as_bibtex(reference=reference).strip()


def write_citation(path: Path, data: CommentedMap) -> bool:
    old_content = path.read_text(encoding="utf-8")
    new_content = render_citation(data)
    if old_content == new_content:
        return False
    path.write_text(new_content, encoding="utf-8")
    return True


def apply_citation_metadata(data: CommentedMap, config: CitationConfig) -> None:
    data["version"] = config.version
    data["date-released"] = config.date_released
    data["repository-code"] = config.repository_code
    data["repository"] = origin_archive_url(config.repository_code)


def check_citation_metadata(data: CommentedMap, config: CitationConfig) -> tuple[str, ...]:
    errors = [
        f"CITATION.cff is missing `{key}`" for key in ("cff-version", "message", "title", "authors") if key not in data
    ]
    if "authors" in data and not isinstance(data["authors"], CommentedSeq):
        errors.append("CITATION.cff `authors` must be a sequence")
    _check_expected_value(errors, data, "version", config.version)
    _check_expected_value(errors, data, "date-released", config.date_released)
    _check_expected_value(errors, data, "repository-code", config.repository_code)
    _check_expected_value(errors, data, "repository", origin_archive_url(config.repository_code))
    return tuple(errors)


def validate_with_cffconvert(path: Path) -> tuple[str, ...]:
    command = ["cffconvert", "--validate", "-i", str(path)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return ()
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return (output or "cffconvert validation failed",)


def origin_archive_url(origin_url: str) -> str:
    return f"https://archive.softwareheritage.org/browse/origin/?origin_url={quote(origin_url, safe='')}"


def _check_expected_value(errors: list[str], data: CommentedMap, key: str, expected: str) -> None:
    actual = str(data[key]) if key in data else None
    if actual != expected:
        errors.append(f"CITATION.cff `{key}` is `{actual}`, expected `{expected}`")
