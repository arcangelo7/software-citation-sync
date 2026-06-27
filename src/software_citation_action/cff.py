# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

import subprocess
from io import StringIO
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from software_citation_action.config import CitationConfig, ProjectMetadata


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


def render_citation_bibtex(data: CommentedMap, reference: str) -> str:
    return "\n".join(
        [
            f"@software{{{reference},",
            f"author = {{{_bibtex_authors(data['authors'])}}},",
            f"title = {{{data['title']}}},",
            f"url = {{{data['url']}}},",
            f"version = {{{data['version']}}},",
            f"year = {{{str(data['date-released'])[:4]}}}",
            "}",
        ],
    )


def create_citation(project_metadata: ProjectMetadata) -> CommentedMap:
    data = CommentedMap()
    data["cff-version"] = "1.2.0"
    data["message"] = "If you use this software, please cite it using these metadata."
    data["title"] = project_metadata.title
    authors = CommentedSeq()
    for author_name in project_metadata.authors:
        author = CommentedMap()
        author["name"] = author_name
        authors.append(author)
    data["authors"] = authors
    return data


def write_citation(path: Path, data: CommentedMap) -> bool:
    old_content = path.read_text(encoding="utf-8") if path.exists() else None
    new_content = render_citation(data)
    if old_content == new_content:
        return False
    path.write_text(new_content, encoding="utf-8")
    return True


def apply_citation_metadata(data: CommentedMap, config: CitationConfig) -> None:
    data["version"] = config.version
    data["date-released"] = config.date_released
    data["url"] = config.software_heritage_url


def validate_with_cffconvert(path: Path) -> tuple[str, ...]:
    command = ["cffconvert", "--validate", "-i", str(path)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return ()
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return (output or "cffconvert validation failed",)


def _bibtex_authors(authors: object) -> str:
    if not isinstance(authors, CommentedSeq):
        msg = "CITATION.cff `authors` must be a sequence"
        raise TypeError(msg)
    return " and ".join(_bibtex_author(author) for author in authors)


def _bibtex_author(author: object) -> str:
    if not isinstance(author, CommentedMap):
        msg = "CITATION.cff author entries must be mappings"
        raise TypeError(msg)
    if "family-names" in author and "given-names" in author:
        return f"{author['family-names']}, {author['given-names']}"
    return str(author["name"])
