# pylegendtestdata

[![PyPI](https://img.shields.io/pypi/v/pylegendtestdata?logo=pypi)](https://pypi.org/project/pylegendtestdata/)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/legend-exp/pylegendtestdata?logo=git)
[![GitHub Workflow Status](https://img.shields.io/github/checks-status/legend-exp/pylegendtestdata/main?label=main%20branch&logo=github)](https://github.com/legend-exp/pylegendtestdata/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub issues](https://img.shields.io/github/issues/legend-exp/pylegendtestdata?logo=github)
![GitHub pull requests](https://img.shields.io/github/issues-pr/legend-exp/pylegendtestdata?logo=github)
![License](https://img.shields.io/github/license/legend-exp/pylegendtestdata)

Tiny Python package to access [LEGEND test data](https://github.com/legend-exp/legend-testdata).

Install (with pip):
```console
$ python -m pip install pylegendtestdata
```

Usage:

```pycon
>>> from legendtestdata import LegendTestData
>>> ldata = LegendTestData()  # clone legend-exp/legend-testdata below /tmp
>>> ldata.checkout("968c9ba")  # optionally checkout a specific version
>>> ldata.get_path("orca/fc/L200-comm-20220519-phy-geds.orca")  # get absolute path to test file
'/tmp/legend-testdata-gipert/data/orca/fc/L200-comm-20220519-phy-geds.orca'
>>> ldata.reset()  # checkout default branch (main)
```

<sub>*This Python package layout is based on [pyproject-template](https://github.com/gipert/pyproject-template).*</sub>
