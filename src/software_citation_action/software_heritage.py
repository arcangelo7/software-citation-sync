# SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import cast
from urllib.parse import quote

import requests

SAVE_API = "https://archive.softwareheritage.org/api/1/origin/save/"
SAVE_VISIT_TYPE = "git"
SWHID_ORIGIN_SAFE_CHARS = ":/?[]@!$&'()*+,="


def archive_origin(origin_url: str, timeout_seconds: int, poll_interval_seconds: int) -> str:
    session = requests.Session()
    save_request = _request_save(session, origin_url)
    deadline = time.monotonic() + timeout_seconds
    current = save_request
    while time.monotonic() <= deadline:
        task_status = _required_text(current, "save_task_status")
        if task_status == "succeeded":
            snapshot_swhid = _required_text(current, "snapshot_swhid")
            return _swh_url(snapshot_swhid, origin_url)
        if task_status == "failed":
            msg = f"Software Heritage save task failed for {origin_url}"
            raise RuntimeError(msg)
        time.sleep(poll_interval_seconds)
        current = _poll_save_request(session, current)
    msg = f"Software Heritage save task timed out for {origin_url}"
    raise TimeoutError(msg)


def _request_save(session: requests.Session, origin_url: str) -> Mapping[str, object]:
    response = session.post(_save_url(origin_url), headers={"Accept": "application/json"}, timeout=30)
    response.raise_for_status()
    return cast("Mapping[str, object]", response.json())


def _poll_save_request(
    session: requests.Session,
    current: Mapping[str, object],
) -> Mapping[str, object]:
    url = _required_text(current, "request_url")
    response = session.get(url, headers={"Accept": "application/json"}, timeout=30)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, list):
        return cast("Mapping[str, object]", data[0])
    return cast("Mapping[str, object]", data)


def _save_url(origin_url: str) -> str:
    return f"{SAVE_API}{SAVE_VISIT_TYPE}/url/{quote(origin_url, safe='')}/"


def _swh_url(snapshot_swhid: str, origin_url: str) -> str:
    encoded_origin = quote(origin_url, safe=SWHID_ORIGIN_SAFE_CHARS)
    return f"https://archive.softwareheritage.org/{snapshot_swhid};origin={encoded_origin}"


def _required_text(data: Mapping[str, object], key: str) -> str:
    return cast("str", data[key])
