# CLI Config

## *Build your experiment configurations for complex projects with robustness, flexibility and simplicity*

<p align="center">
  <img src="docs/_static/logo_extend.png" />
</p>

*CLI Config*: Lightweight library that provides routines to merge nested configs
and set parameters from command line. It is also provide processing functions
that can change the whole configuration before and after each config merge, config
saving, config loading and at the end of config building. It also contains many
routines to manipulate the config as flatten or nested dictionaries.

The package is initially designed for machine learning experiments where the
number of parameters is huge and a lot of them have to be set by the user between
each experiment. If your project matches this description, this package is for you!

## Documentation :memo: [here](https://cliconfig.readthedocs.io/en/latest)

## Pypi :package: [here](https://pypi.org/project/cliconfig/)

[![Release](https://img.shields.io/github/v/tag/valentingol/cliconfig?label=Pypi&logo=pypi&logoColor=yellow)](https://pypi.org/project/cliconfig/)
![PythonVersion](https://img.shields.io/badge/Python-3.7%20%7E%203.11-informational)
[![License](https://img.shields.io/github/license/valentingol/cliconfig?color=999)](https://stringfixer.com/fr/MIT_license)

[![Ruff_logo](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)
[![Black_logo](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![Ruff](https://github.com/valentingol/cliconfig/actions/workflows/ruff.yaml/badge.svg)](https://github.com/valentingol/cliconfig/actions/workflows/ruff.yaml)
[![Flake8](https://github.com/valentingol/cliconfig/actions/workflows/flake.yaml/badge.svg)](https://github.com/valentingol/cliconfig/actions/workflows/flake.yaml)
[![Pydocstyle](https://github.com/valentingol/cliconfig/actions/workflows/pydocstyle.yaml/badge.svg)](https://github.com/valentingol/cliconfig/actions/workflows/pydocstyle.yaml)
[![MyPy](https://github.com/valentingol/cliconfig/actions/workflows/mypy.yaml/badge.svg)](https://github.com/valentingol/cliconfig/actions/workflows/mypy.yaml)
[![PyLint](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/valentingol/ab12676c87f0eaa715bef0f8ad31a604/raw/cliconfig_pylint.json)](https://github.com/valentingol/cliconfig/actions/workflows/pylint.yaml)

[![Tests](https://github.com/valentingol/cliconfig/actions/workflows/tests.yaml/badge.svg)](https://github.com/valentingol/cliconfig/actions/workflows/tests.yaml)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/valentingol/098e9c7c53be88779ee52ef2f2bc8803/raw/cliconfig_tests.json)](https://github.com/valentingol/cliconfig/actions/workflows/tests.yaml)
[![Documentation Status](https://readthedocs.org/projects/cliconfig/badge/?version=latest)](https://cliconfig.readthedocs.io/en/latest/?badge=latest)

Official badge :
[![Config](https://custom-icon-badges.demolab.com/badge/cliconfig-black?logo=cliconfig)](https://github.com/valentingol/cliconfig)

## Installation

In a new virtual environment, simply install the package with:

```bash
pip install cliconfig
```

This package is OS independent and supported on Linux, macOS and Windows.

## Quick start

See the [Quick start](https://cliconfig.readthedocs.io/en/latest/quickstart.html) section of
the documentation for a quick overview.

### Minimal example

Make default config yaml file(s) in your project (configs are merged from left to right):

```python
# main.py
from cliconfig import make_config
config = make_config('default1.yaml', 'default2.yaml')
```

Then launch your script with additional config file(s) and individual parameters by command line.
The additional configs are merged on the default one's then the parameters are set.

```bash
python main.py --config first.yaml,second.yaml --param1=1 --subconfig.param2='foo'
```

**By default, these additional configs cannot add new parameters to the default config
(for security and retro-compatibility reasons).**

See the [Edge cases](https://cliconfig.readthedocs.io/en/latest/edge_cases.html) section of
the documentation for some edge cases due to implementation.

### Some features

Default features include automatic configs merging after reading a config file (to organize
them on multiple files without needed to list them in the CLI), dynamically copy other parameters,
select a sub-config among multiple ones (and delete the others), protect parameters values
or one of their properties, specify the parameters type (as precisely as you want)
and more.

It is also easy to create your own features and possibilities are endless. The way to do
it are explained in the [*Processing*](https://cliconfig.readthedocs.io/en/latest/processing.html)
section of the documentation.

## How to contribute

For **development**, install the package dynamically and dev requirements with:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Everyone can contribute to CLI Config, and we value everyone’s contributions.
Please see our [contributing guidelines](CONTRIBUTING.md) for more information 🤗

## To-do

* [x] Add a parameter to change the type (pre-merge, post-merge, ...) of processings
  created by `create_processing_XXX`
* [x] Allow the flat config to be passed as a 2nd argument of the fonctions `func` used
  in `create_processing_XXX`
* [x] Correct grammar and syntax errors in the documentation with LTex
* [x] Add `no_cli` argument to `make_config` to avoid using CLI arguments

## License

Copyright © 2023 Valentin Goldité

This program is free software: you can redistribute it and/or modify it under the
terms of the [MIT License](LICENSE). This program is distributed in the hope that
it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

The project is free to use for COMMERCIAL USE, MODIFICATION, DISTRIBUTION and
PRIVATE USE as long as the original license is included as well as this copy
right notice at the top of the modified files.
