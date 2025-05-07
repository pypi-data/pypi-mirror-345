<!--
SPDX-FileCopyrightText: 2025 Sofía Aritz <sofiaritz@fsfe.org>

SPDX-License-Identifier: AGPL-3.0-only
-->

# MP Scrape Bundestag

Part of the [MP Scrape](https://git.fsfe.org/mp-scrape/mp-scrape) project.

Filter rows based on the value of a column

## Where to get it

You can get it through the [Python Package Index (PyPI)](https://pypi.org/project/mp_scrape_filter/):

```sh
$ pip3 install mp_scrape_filter
```

## Arguments

- `check_col` Column to check.
- `expect` Expected value of the column. If this value matches the value of the column on a given row, it will be kept.