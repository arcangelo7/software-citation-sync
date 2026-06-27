<!--
SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>

SPDX-License-Identifier: ISC
-->

# Software citation action

[![Test](https://github.com/arcangelo7/software-citation-action/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/arcangelo7/software-citation-action/actions/workflows/test.yml)
[![Pyright](https://github.com/arcangelo7/software-citation-action/actions/workflows/pyright.yml/badge.svg?branch=master)](https://github.com/arcangelo7/software-citation-action/actions/workflows/pyright.yml)
[![Ruff](https://github.com/arcangelo7/software-citation-action/actions/workflows/ruff.yml/badge.svg?branch=master)](https://github.com/arcangelo7/software-citation-action/actions/workflows/ruff.yml)
[![Coverage](https://arcangelo7.github.io/software-citation-action/coverage/coverage-badge.svg)](https://arcangelo7.github.io/software-citation-action/coverage/)
[![REUSE status](https://api.reuse.software/badge/github.com/arcangelo7/software-citation-action)](https://api.reuse.software/info/github.com/arcangelo7/software-citation-action)

GitHub Action for keeping software citation metadata aligned with releases and Software Heritage.

The action uses:

- `CITATION.cff` in the repository root.
- `README.md` in the repository root.
- the version from root `package.json`, or from root `pyproject.toml` when `package.json` is absent.
- the current UTC date as `date-released`.
- the repository where the workflow is running.

When `CITATION.cff` is absent, it creates one from project metadata in `package.json` or `pyproject.toml`.
It updates citation metadata, updates the marked README citation block, and validates `CITATION.cff`.
It also sends the repository URL to Software Heritage for archiving, waits for the archive job to finish, and uses the returned snapshot URL in `CITATION.cff` and in the README BibTeX entry.
The selected manifest must define a string `version`.

## GitHub action

```yaml
- uses: arcangelo7/software-citation-action@v1
```

The action exposes `changed`, which is `true` when `CITATION.cff` or `README.md` changed.

## README block

The action manages one marked block delimited by the `software-citation-action:start` and `software-citation-action:end` HTML comments.
The BibTeX entry is generated from the updated `CITATION.cff`.

<!-- software-citation-action:start -->
To cite the latest version of this software (1.1.1), use this BibTeX entry:

```bibtex
@software{software-citation-action-1.1.1,
author = {Arcangelo Massari},
title = {software-citation-action},
url = {https://archive.softwareheritage.org/swh:1:snp:4bcefc21f332cf45d28e39c02a55893a5fbb7f07;origin=https://github.com/arcangelo7/software-citation-action},
version = {1.1.1},
year = {2026}
}
```
<!-- software-citation-action:end -->
