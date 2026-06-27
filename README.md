<!--
SPDX-FileCopyrightText: 2026 Arcangelo Massari <github@a.arcangelomassari.com>

SPDX-License-Identifier: ISC
-->

# Software citation action

[![Test](https://github.com/arcangelo7/software-citation-action/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/arcangelo7/software-citation-action/actions/workflows/test.yml)
[![Coverage](https://arcangelo7.github.io/software-citation-action/coverage/coverage-badge.svg)](https://arcangelo7.github.io/software-citation-action/coverage/)
[![REUSE status](https://api.reuse.software/badge/github.com/arcangelo7/software-citation-action)](https://api.reuse.software/info/github.com/arcangelo7/software-citation-action)

GitHub Action for keeping software citation metadata aligned with releases and Software Heritage.

The action uses:

- `CITATION.cff` in the repository root.
- `README.md` in the repository root.
- the version from root `package.json`, or from root `pyproject.toml` when `package.json` is absent.
- the current UTC date as `date-released`.
- the repository where the workflow is running.

It updates citation metadata, updates the marked README citation block, and validates `CITATION.cff`.
It also sends the repository URL to Software Heritage for archiving, waits for the archive job to finish, and uses the returned snapshot URL in the README BibTeX entry.
The selected manifest must define a string `version`.

## GitHub action

```yaml
- uses: arcangelo7/software-citation-action@v1
```

The action exposes `changed`, which is `true` when `CITATION.cff` or `README.md` changed.

## README block

The action manages only this marked block. The BibTeX entry is generated from the updated `CITATION.cff`.

````markdown
<!-- software-citation-action:start -->
To cite the latest version of this software (2.8.0), use this BibTeX entry:

```bibtex
@misc{ramose-2.8.0,
author = {Massari, Arcangelo},
title = {RAMOSE},
url = {https://archive.softwareheritage.org/swh:1:snp:fc0b501f594531b2b8f694469cc38aed15897bbe;origin=https://github.com/arcangelo7/ramose},
year = {2026}
}
```
<!-- software-citation-action:end -->
````
