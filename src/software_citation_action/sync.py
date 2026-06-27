# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

from software_citation_action.cff import (
    apply_citation_metadata,
    create_citation,
    load_citation,
    render_citation_bibtex,
    validate_with_cffconvert,
    write_citation,
)
from software_citation_action.config import CheckResult, CitationConfig, ProjectMetadata
from software_citation_action.readme import bibtex_reference, readme_block_matches, write_readme_block


def check(config: CitationConfig) -> CheckResult:
    errors = [*validate_with_cffconvert(config.citation_path)]
    bibtex = render_readme_bibtex(config)
    if not readme_block_matches(config.readme_path, config.version, bibtex):
        errors.append(f"{config.readme_path} citation block is out of date")
    return CheckResult(tuple(errors))


def write_citation_metadata(config: CitationConfig, project_metadata: ProjectMetadata | None = None) -> bool:
    if config.citation_path.exists():
        data = load_citation(config.citation_path)
    else:
        if project_metadata is None:
            msg = f"{config.citation_path} does not exist and project metadata was not provided"
            raise FileNotFoundError(msg)
        data = create_citation(project_metadata)
    apply_citation_metadata(data, config)
    return write_citation(config.citation_path, data)


def render_readme_bibtex(config: CitationConfig) -> str:
    data = load_citation(config.citation_path)
    return render_citation_bibtex(
        data,
        bibtex_reference(str(data["title"]), config.version),
    )


def write_readme(config: CitationConfig) -> bool:
    bibtex = render_readme_bibtex(config)
    return write_readme_block(config.readme_path, config.version, bibtex)
