# Nextline Schedule

[![PyPI - Version](https://img.shields.io/pypi/v/nextline-schedule.svg)](https://pypi.org/project/nextline-schedule)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nextline-schedule.svg)](https://pypi.org/project/nextline-schedule)
[![Test Status](https://github.com/simonsobs/nextline-schedule/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline-schedule/actions/workflows/unit-test.yml)
[![Test Status](https://github.com/simonsobs/nextline-schedule/actions/workflows/type-check.yml/badge.svg)](https://github.com/simonsobs/nextline-schedule/actions/workflows/type-check.yml)
[![codecov](https://codecov.io/gh/simonsobs/nextline-schedule/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/nextline-schedule)

A plugin for [nextline-graphql](https://github.com/simonsobs/nextline-graphql).
An interface to the [SO scheduler](https://github.com/simonsobs/so-scheduler).

---

**Table of Contents**

- [Nextline Schedule](#nextline-schedule)
  - [Installation](#installation)
  - [License](#license)
  - [Contact](#contact)

## Installation

```console
pip install nextline-schedule
```

## Configuration

| Environment variable                | Default value                                          | Description                                                                                          |
| ----------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| `NEXTLINE_SCHEDULE__API`            | `https://scheduler-uobd.onrender.com/api/v1/schedule/` | The [schedule API URL](https://github.com/simonsobs/so-scheduler/blob/master/readme.md#schedule-api) |
| `NEXTLINE_SCHEDULE__LENGTH_MINUTES` | 1                                                      |                                                                                                      |
| `NEXTLINE_SCHEDULE__POLICY`         | `dummy`                                                |                                                                                                      |

## License

- _Nextline Schedule_ is licensed under the [MIT](https://spdx.org/licenses/MIT.html) license.

## Contact

- [Tai Sakuma](https://github.com/TaiSakuma) <span itemscope itemtype="https://schema.org/Person"><a itemprop="sameAs" content="https://orcid.org/0000-0003-3225-9861" href="https://orcid.org/0000-0003-3225-9861" target="orcid.widget" rel="me noopener noreferrer" style="vertical-align:text-top;"><img src="https://orcid.org/sites/default/files/images/orcid_16x16.png" style="width:1em;margin-right:.5em;" alt="ORCID iD icon"></a></span>
