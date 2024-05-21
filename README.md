# nextline-schedule

[![PyPI - Version](https://img.shields.io/pypi/v/nextline-schedule.svg)](https://pypi.org/project/nextline-schedule)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nextline-schedule.svg)](https://pypi.org/project/nextline-schedule)

[![Test Status](https://github.com/simonsobs/nextline-schedule/actions/workflows/unit-test.yml/badge.svg)](https://github.com/simonsobs/nextline-schedule/actions/workflows/unit-test.yml)
[![Test Status](https://github.com/simonsobs/nextline-schedule/actions/workflows/type-check.yml/badge.svg)](https://github.com/simonsobs/nextline-schedule/actions/workflows/type-check.yml)
[![codecov](https://codecov.io/gh/simonsobs/nextline-schedule/branch/main/graph/badge.svg)](https://codecov.io/gh/simonsobs/nextline-schedule)

A plugin for [nextline-graphql](https://github.com/simonsobs/nextline-graphql).
An interface to the [SO scheduler](https://github.com/simonsobs/scheduler).

## Installation

```console
pip install nextline-schedule
```

## Configuration

| Environment variable                | Default value                                          | Description                                                                                           |
| ----------------------------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| `NEXTLINE_SCHEDULE__API`            | `https://scheduler-uobd.onrender.com/api/v1/schedule/` | The [schedule API URL](https://github.com/simonsobs/scheduler-server?tab=readme-ov-file#schedule-api) |
| `NEXTLINE_SCHEDULE__LENGTH_MINUTES` | 1                                                      |                                                                                                       |
| `NEXTLINE_SCHEDULE__POLICY`         | `dummy`                                                |                                                                                                       |
