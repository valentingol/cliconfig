# CLI Config

Lightweight library to merge your configs (optionally nested) and set parameters
from command line.

[![PyPI version](https://badge.fury.io/py/cliconfig.svg)](https://badge.fury.io/py/cliconfig)
![PythonVersion](https://img.shields.io/badge/python-3.7%20%7E%203.11-informational)
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

In a new virtual environment, install the package with:

```bash
pip install cliconfig
```

## Quick start

First create a default config that can be split in multiple files that will be merged
(from left to right in `make_config` function):

```yaml
# default1.yaml
param1: 1
param2: 0
letters:
  letter1: a
  letter2: b
```

```yaml
# default2.yaml
param1: 1
param2: 2  # will override param2 from default1.yaml
letters.letter3: c  # add a new parameter
```

Now you can set up your program to use the config:

```python
# main.py
from cliconfig import make_config, show_config

config = make_config('default1.yaml', 'default2.yaml')
show_config(config)
```

Then add one or multiple additional config files that will override the default values.
**Be careful, the additional config files cannot bring new parameters by default**.
If you want to add new parameters (not advised for retro-compatibility, readability
and security), you can add `allow_new_keys=True` in `make_config` function.

```yaml
# exp1.yaml
letters:
  letter3: C
```

```yaml
# exp2.yaml
param1: -1
letters.letter1: A
```

Now you can launch the program with additional configurations and parameters.
The additional configurations are indicated with `--config` (separate with comma,
without space) and the parameters with `--<param_name>`. The default configuration
will be merged with the additional configurations (from left to right), then the
parameters will be set.

```bash
python main.py --config exp1.yaml,exp2.yaml --param2=-2 --letters.letter2='B'
```

Will show:

```text
[CONFIG] Merge 2 default configs, 2 additional configs and 2 CLI parameter(s).

Config:
    param1: -1
    param2: -2
    letters:
        letter1: A
        letter2: B
        letter3: C
```

Note that the configurations are native python dicts.

## Manipulate configs

To merge configs, you can use `cliconfig.merge` function.
It supports unflatten (or nested) dicts like `{'a': {'b': 1, 'c': 2}}`,
flatten dicts like `{'a.b': 1, 'a.c': 2}`, and a mix of both. The dicts will be flatten
before merging. Sometimes you can have conflicts in flatten operation for instance with
`{'a.b': 1, 'a': {'b': 2}}` that have two different values for `a.b`. That's why you
can use a `priority` parameter to choose which value to keep before merging.

You can also save, load and display configs with `cliconfig.save_config`,
`cliconfig.load_config` and `cliconfig.show_config` functions.

## How to contribute

For **development**, install the package dynamically and dev requirements with:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Everyone can contribute to CLI Config, and we value everyone’s contributions.
Please see our [contributing guidelines](CONTRIBUTING.md) for more information 🤗

### Todo

To do:

- [ ] add json and ini support
- [ ] avoid changing keys order in merge

## License

Copyright (C) 2023  Valentin Goldité

This program is free software: you can redistribute it and/or modify it under the
terms of the [MIT License](LICENSE). This program is distributed in the hope that
it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

This project is free to use for COMMERCIAL USE, MODIFICATION, DISTRIBUTION and
PRIVATE USE as long as the original license is include as well as this copy
right notice at the top of the modified files.
