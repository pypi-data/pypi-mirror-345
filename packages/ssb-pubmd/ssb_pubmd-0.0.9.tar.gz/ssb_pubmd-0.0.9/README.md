# SSB Pubmd

[![PyPI](https://img.shields.io/pypi/v/ssb-pubmd.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/ssb-pubmd.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/ssb-pubmd)][pypi status]
[![License](https://img.shields.io/pypi/l/ssb-pubmd)][license]

[![Documentation](https://github.com/statisticsnorway/ssb-pubmd/actions/workflows/docs.yml/badge.svg)][documentation]
[![Tests](https://github.com/statisticsnorway/ssb-pubmd/actions/workflows/tests.yml/badge.svg)][tests]
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=statisticsnorway_ssb-pubmd&metric=coverage)][sonarcov]
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=statisticsnorway_ssb-pubmd&metric=alert_status)][sonarquality]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)][poetry]

[pypi status]: https://pypi.org/project/ssb-pubmd/
[documentation]: https://statisticsnorway.github.io/ssb-pubmd
[tests]: https://github.com/statisticsnorway/ssb-pubmd/actions?workflow=Tests

[sonarcov]: https://sonarcloud.io/summary/overall?id=statisticsnorway_ssb-pubmd
[sonarquality]: https://sonarcloud.io/summary/overall?id=statisticsnorway_ssb-pubmd
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black
[poetry]: https://python-poetry.org/

## Features

- Helper library for syncing a Jupyter Notebook with a remote server (e.g. a CMS/publishing platform).
- Supports logging in through a popup browser window.

## Requirements

- This library uses [playwright](https://github.com/microsoft/playwright-python) to create a logged in browser context. This requires installing a [browser binary](https://playwright.dev/python/docs/browsers#install-browsers) and necessary [system dependencies](https://playwright.dev/python/docs/browsers#install-system-dependencies).

## Installation

You can install _SSB Pubmd_ via [pip] from [PyPI]:

```console
pip install ssb-pubmd
```

## Usage

Please see the [Reference Guide] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_SSB Pubmd_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [Statistics Norway]'s [SSB PyPI Template].

[statistics norway]: https://www.ssb.no/en
[pypi]: https://pypi.org/
[ssb pypi template]: https://github.com/statisticsnorway/ssb-pypitemplate
[file an issue]: https://github.com/statisticsnorway/ssb-pubmd/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/statisticsnorway/ssb-pubmd/blob/main/LICENSE
[contributor guide]: https://github.com/statisticsnorway/ssb-pubmd/blob/main/CONTRIBUTING.md
[reference guide]: https://statisticsnorway.github.io/ssb-pubmd/reference.html
