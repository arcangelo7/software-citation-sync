# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

import copy

from software_citation_action.cff import (
    apply_citation_metadata,
    check_citation_metadata,
    load_citation,
    render_citation_bibtex,
    validate_with_cffconvert,
    write_citation,
)
from software_citation_action.config import CheckResult, CitationConfig
from software_citation_action.readme import bibtex_reference, readme_block_matches, write_readme_block


def check_citation(config: CitationConfig) -> CheckResult:
    data = load_citation(config.citation_path)
    errors = [*check_citation_metadata(data, config), *validate_with_cffconvert(config.citation_path)]
    return CheckResult(tuple(errors))


def check(config: CitationConfig, swh_url: str) -> CheckResult:
    data = load_citation(config.citation_path)
    errors = [*check_citation_metadata(data, config), *validate_with_cffconvert(config.citation_path)]
    bibtex = render_readme_bibtex(config, swh_url)
    if not readme_block_matches(config.readme_path, config.version, bibtex):
        errors.append(f"{config.readme_path} citation block is out of date")
    return CheckResult(tuple(errors))


def write_citation_metadata(config: CitationConfig) -> bool:
    data = load_citation(config.citation_path)
    apply_citation_metadata(data, config)
    return write_citation(config.citation_path, data)


def render_readme_bibtex(config: CitationConfig, swh_url: str) -> str:
    data = load_citation(config.citation_path)
    expected_data = copy.deepcopy(data)
    apply_citation_metadata(expected_data, config)
    return render_citation_bibtex(expected_data, bibtex_reference(config.repository_code, config.version), swh_url)


def write_readme(config: CitationConfig, swh_url: str) -> bool:
    bibtex = render_readme_bibtex(config, swh_url)
    return write_readme_block(config.readme_path, config.version, bibtex)
