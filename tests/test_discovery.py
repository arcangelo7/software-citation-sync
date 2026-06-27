# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

from pathlib import Path

import pytest

from software_citation_action.discovery import discover_version


def test_discover_version_requires_package_json_version(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "ramose"}', encoding="utf-8")

    with pytest.raises(KeyError) as exc_info:
        discover_version(tmp_path)

    assert exc_info.value.args == ("version",)
