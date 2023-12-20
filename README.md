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

## Tags

You can add tags `@<tag_name>` at the end of parameters name to activate some features. See the [Quick start](https://cliconfig.readthedocs.io/en/latest/quickstart.html)
section of the documentation for a quick overview.

The default tags include:

* `@merge_add`, `@merge_before`, and `@merge_after`: merge other yaml files
  indicating the path
* `@copy`: copy an other parameter
* `@def`: safely evaluate an expression to define the parameter value
* `@type:<my type>`: try to convert and check the type
* `@select`: target a sub-config and delete the sub-config in the parent config
* `@delete`: delete the key from the config
* `@new`: allow to add parameters that are not present in default config
* `@dict`: create a dict object that is not a sub-config (see the
  [*Edge cases*](https://cliconfig.readthedocs.io/en/latest/edge_cases.html) section)

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

## License, usage and distribution

This program is free software under the [MIT License](LICENSE).

It means that:

* If you use this package as a library without modifying it, there is no obligation
  regarding this license.
* If you modify the source code of this package, you must keep the original copyright
  in the source code and add your own. The LICENSE file must also contain the original
  copyright (and the original MIT license notice if not sublicensed).
* In any case, you can use this package in open source or closed source projects and for
  commercial or non-commercial purposes.

Copyright © 2023 Valentin Goldité
