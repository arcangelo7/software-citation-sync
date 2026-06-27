# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

import pytest
import requests_mock

from software_citation_action.software_heritage import archive_origin


def test_archive_origin_returns_swh_url(requests_mock: requests_mock.Mocker) -> None:
    origin = "https://github.com/arcangelo7/ramose"
    save_url = (
        "https://archive.softwareheritage.org/api/1/origin/save/git/url/https%3A%2F%2Fgithub.com%2Farcangelo7%2Framose/"
    )
    request_url = "https://archive.softwareheritage.org/api/1/origin/save/2373061/"
    requests_mock.post(
        save_url,
        json={
            "request_url": request_url,
            "save_task_status": "scheduled",
            "snapshot_swhid": "",
        },
    )
    requests_mock.get(
        request_url,
        json={
            "request_url": request_url,
            "save_task_status": "succeeded",
            "snapshot_swhid": "swh:1:snp:fc0b501f594531b2b8f694469cc38aed15897bbe",
        },
    )

    result = archive_origin(origin, timeout_seconds=30, poll_interval_seconds=0)

    assert (
        result == "https://archive.softwareheritage.org/swh:1:snp:fc0b501f594531b2b8f694469cc38aed15897bbe"
        ";origin=https://github.com/arcangelo7/ramose"
    )


def test_archive_origin_requires_poll_url(requests_mock: requests_mock.Mocker) -> None:
    origin = "https://github.com/arcangelo7/ramose"
    save_url = (
        "https://archive.softwareheritage.org/api/1/origin/save/git/url/https%3A%2F%2Fgithub.com%2Farcangelo7%2Framose/"
    )
    requests_mock.post(
        save_url,
        json={
            "save_task_status": "scheduled",
            "snapshot_swhid": "",
        },
    )

    with pytest.raises(KeyError) as exc_info:
        archive_origin(origin, timeout_seconds=30, poll_interval_seconds=0)

    assert exc_info.value.args == ("request_url",)
