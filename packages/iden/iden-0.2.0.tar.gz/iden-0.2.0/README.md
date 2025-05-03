# iden

<p align="center">
    <a href="https://github.com/durandtibo/iden/actions">
        <img alt="CI" src="https://github.com/durandtibo/iden/workflows/CI/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/iden/actions">
        <img alt="Nightly Tests" src="https://github.com/durandtibo/iden/workflows/Nightly%20Tests/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/iden/actions">
        <img alt="Nightly Package Tests" src="https://github.com/durandtibo/iden/workflows/Nightly%20Package%20Tests/badge.svg">
    </a>
    <br/>
    <a href="https://durandtibo.github.io/iden/">
        <img alt="Documentation" src="https://github.com/durandtibo/iden/workflows/Documentation%20(stable)/badge.svg">
    </a>
    <a href="https://durandtibo.github.io/iden/">
        <img alt="Documentation" src="https://github.com/durandtibo/iden/workflows/Documentation%20(unstable)/badge.svg">
    </a>
    <br/>
    <a href="https://codecov.io/gh/durandtibo/iden">
        <img alt="Codecov" src="https://codecov.io/gh/durandtibo/iden/branch/main/graph/badge.svg">
    </a>
    <a href="https://codeclimate.com/github/durandtibo/iden/maintainability">
        <img src="https://api.codeclimate.com/v1/badges/e1d6a491463b53dde654/maintainability" />
    </a>
    <a href="https://codeclimate.com/github/durandtibo/iden/test_coverage">
        <img src="https://api.codeclimate.com/v1/badges/e1d6a491463b53dde654/test_coverage" />
    </a>
    <br/>
    <a href="https://github.com/psf/black">
        <img  alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
    </a>
    <a href="https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings">
        <img  alt="Doc style: google" src="https://img.shields.io/badge/%20style-google-3666d6.svg">
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;">
    </a>
    <a href="https://github.com/guilatrova/tryceratops">
        <img  alt="Doc style: google" src="https://img.shields.io/badge/try%2Fexcept%20style-tryceratops%20%F0%9F%A6%96%E2%9C%A8-black">
    </a>
    <br/>
    <a href="https://pypi.org/project/iden/">
        <img alt="PYPI version" src="https://img.shields.io/pypi/v/iden">
    </a>
    <a href="https://pypi.org/project/iden/">
        <img alt="Python" src="https://img.shields.io/pypi/pyversions/iden.svg">
    </a>
    <a href="https://opensource.org/licenses/BSD-3-Clause">
        <img alt="BSD-3-Clause" src="https://img.shields.io/pypi/l/iden">
    </a>
    <br/>
    <a href="https://pepy.tech/project/iden">
        <img  alt="Downloads" src="https://static.pepy.tech/badge/iden">
    </a>
    <a href="https://pepy.tech/project/iden">
        <img  alt="Monthly downloads" src="https://static.pepy.tech/badge/iden/month">
    </a>
    <br/>
</p>

## Overview

`iden` is a simple Python library to manage a dataset of shards when training a machine learning
model.
`iden` uses a lazy loading approach to load the shard's data, so it is easy to manage shards without
loading their data.
`iden` supports different format to store shards on disk.

## Installation

We highly recommend installing
a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).
`iden` can be installed from pip using the following command:

```shell
pip install iden
```

To make the package as slim as possible, only the minimal packages required to use `iden` are
installed.
To include all the dependencies, you can use the following command:

```shell
pip install iden[all]
```

Please check the [get started page](https://durandtibo.github.io/iden/get_started) to see how to
install only some specific dependencies or other alternatives to install the library.
The following is the corresponding `iden` versions and tested dependencies.

| `iden`  | `coola`        | `objectory`  | `numpy`<sup>*</sup> | `pyyaml`<sup>*</sup> | `safetensors`<sup>*</sup> | `torch`<sup>*</sup> | `python`      |
|---------|----------------|--------------|---------------------|----------------------|---------------------------|---------------------|---------------|
| `main`  | `>=0.8.4,<1.0` | `>=0.2,<1.0` | `>=1.22,<2.0`       | `>=6.0,<7.0`         | `>=0.4,<1.0`              | `>=2.0,<3.0`        | `>=3.9,<3.14` |
| `0.2.0` | `>=0.8.4,<1.0` | `>=0.2,<1.0` | `>=1.22,<2.0`       | `>=6.0,<7.0`         | `>=0.4,<1.0`              | `>=2.0,<3.0`        | `>=3.9,<3.14` |
| `0.1.0` | `>=0.8.4,<1.0` | `>=0.2,<1.0` | `>=1.22,<2.0`       | `>=6.0,<7.0`         | `>=0.4,<1.0`              | `>=2.0,<3.0`        | `>=3.9,<3.14` |
| `0.0.4` | `>=0.3,<1.0`   | `>=0.1,<1.0` | `>=1.22,<2.0`       | `>=6.0,<7.0`         | `>=0.4,<1.0`              | `>=2.0,<3.0`        | `>=3.9,<3.13` |
| `0.0.3` | `>=0.3,<1.0`   | `>=0.1,<1.0` | `>=1.22,<2.0`       | `>=6.0,<7.0`         | `>=0.4,<1.0`              | `>=2.0,<3.0`        | `>=3.9,<3.12` |
| `0.0.2` | `>=0.4,<1.0`   | `>=0.1,<1.0` | `>=1.22,<2.0`       | `>=6.0,<7.0`         | `>=0.4,<1.0`              | `>=2.0,<2.1`        | `>=3.9,<3.12` |
| `0.0.1` | `>=0.4,<1.0`   | `>=0.1,<1.0` | `>=1.22,<2.0`       | `>=6.0,<7.0`         | `>=0.4,<1.0`              | `>=2.0,<2.1`        | `>=3.9,<3.12` |

| `iden` | `cloudpickle`<sup>*</sup> | `joblib`<sup>*</sup> |
|--------|---------------------------|----------------------|
| `main` | `>=3.0,<4.0`              | `>=1.3,<2.0`         |

<sup>*</sup> indicates an optional dependency

## Contributing

Please check the instructions in [CONTRIBUTING.md](.github/CONTRIBUTING.md).

## Suggestions and Communication

Everyone is welcome to contribute to the community.
If you have any questions or suggestions, you can
submit [Github Issues](https://github.com/durandtibo/iden/issues).
We will reply to you as soon as possible. Thank you very much.

## API stability

:warning: While `iden` is in development stage, no API is guaranteed to be stable from one
release to the next.
In fact, it is very likely that the API will change multiple times before a stable 1.0.0 release.
In practice, this means that upgrading `iden` to a new version will possibly break any code that
was using the old version of `iden`.

## License

`iden` is licensed under BSD 3-Clause "New" or "Revised" license available in [LICENSE](LICENSE)
file.
