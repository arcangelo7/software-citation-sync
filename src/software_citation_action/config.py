# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CitationConfig:
    citation_path: Path
    readme_path: Path
    version: str
    date_released: str
    repository_code: str


@dataclass(frozen=True)
class CheckResult:
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors
