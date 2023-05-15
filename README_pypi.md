# CLI Config

</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/valentingol/cliconfig/main/docs/_static/logo_extend.png" />
</p>

*CLI Config*: Lightweight library that provides routines to merge nested configs
and set parameters from command line. It is also provide processing functions
that can change the whole configuration before and after each config merge, config
saving and config loading. It also contains many routines to manipulate the config as
flatten or nested dicts.

## Documentation: [here](https://cliconfig.readthedocs.io/en/stable)

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

## Installation

In a new virtual environment, simply install the package with:

```bash
pip install cliconfig
```

This package is OS independent and supported on Linux, macOS and Windows.

## Minimal usage

Make default config file(s) in your project (configs are merged from left to right):

```python
# main.py
from cliconfig import make_config

config = make_config('default1.yaml', 'default2.yaml')
config_dict = config.dict  # native python dict
```

Then launch your script with additional config(s) file(s) and parameters by command line.
The additional configs are merge on the default ones then the parameters are set.

```bash
python main.py --config first.yaml,second.yaml --param2=-2 --letters.letter2='B'
```

**By default, these additional configs cannot add new parameters to the default config
(for security and retro-compatibility reasons).**

See [*Quick Start*](https://cliconfig.readthedocs.io/en/stable/quick_start.html) section
of the documentation for more details.

## With processing

The library provide powerfull tools to modify the configuration called "processings".
One of the possibility they add is to merge multiple configurations,
copy a parameter on another, enforce type and more. To do so, simply adding the
corresponding tags to your parameter names (on config files or CLI parameters).

For instance with these config files:

```yaml
# main.yaml
path_1@merge_add: sub1.yaml
path_2@merge_add: sub2.yaml
config3.select@select: config3.param1

# sub1.yaml
config1:
  param@copy@type:int: config2.param
  param2@type:int: 1

# sub2.yaml
config2.param@type:None|int: 2
config3:
  param1: 0
  param2: 1
```

Here `main.yaml` is interpreted like:

```yaml
path_1: sub1.yaml
path_2: sub2.yaml
config1:
  param: 2  # the value of config2.param
  param2: 1
config2:
  param: 2
config3:
  select: config3.param1
  param1: 0
  # param2 is deleted because it is not in the selection
```

Then, all the parameters in `config1` and `config2` have enforced types
(`config2.param` can also be None) and changing `config2.param` will also update
`config1.param` accordingly (which is protected by direct update).

See [*Processing*](https://cliconfig.readthedocs.io/en/stable/processing.html) section
of the documentation for details on processing and how to create your own.

## How to contribute

For **development**, install the package dynamically and dev requirements with:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Everyone can contribute to CLI Config, and we value everyone’s contributions.
Please see our [contributing guidelines](CONTRIBUTING.md) for more information 🤗

## License

Copyright (C) 2023  Valentin Goldité

This program is free software: you can redistribute it and/or modify it under the
terms of the [MIT License](LICENSE). This program is distributed in the hope that
it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

This project is free to use for COMMERCIAL USE, MODIFICATION, DISTRIBUTION and
PRIVATE USE as long as the original license is include as well as this copy
right notice at the top of the modified files.
