# CLI Config

Lightweight library that provides routines to merge your configs (optionally nested)
and set parameters from command line. It also prevents you from adding new parameters
if not desired. Finally, it provides helper routines to manage flatten dicts, unflatten
(= nested) dicts or a mix of both, save config, load, display, etc.

## Documentation :memo: [here](https://cliconfig.readthedocs.io/en/stable)

[![Release](https://img.shields.io/github/v/release/valentingol/cliconfig?include_prereleases)](https://pypi.org/project/cliconfig/)
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
(from left to right in `make_config` function). There is no limit of depth for the
configurations parameters.

```yaml
---  # default1.yaml
param1: 1
param2: 0
letters:
  letter1: a
  letter2: b

---  # default2.yaml
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
**By default the additional config files cannot bring new parameters**.
It is intended to prevent typos in the config files that would not be detected.
It also improves the readability of the config files and the retro-compatibility.
By the way, you can change this behavior with `allow_new_keys=True` in `make_config`
(be careful).

```yaml
---  # first.yaml
letters:
  letter3: C

---  # second.yaml
param1: -1
letters.letter1: A
```

Now you can launch the program with additional configurations and parameters.
The additional configurations are indicated with `--config` (separate with comma,
without space) and the parameters with `--<param_name>`. The default configuration
will be merged with the additional configurations (from left to right), then the
parameters will be set.

```bash
python main.py --config first.yaml,second.yaml --param2=-2 --letters.letter2='B'
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

## Edge cases

**Be careful, tuples and sets are not supported by YAML and cannot be used in configs.**
Use lists instead if possible

`None` is not recognized as a None object by YAML but as a string, you may use `null`
or `Null` instead if you want to
set a None object.

Dicts are considered as sub-configs and so you may not be able to change the keys if
`allow_new_keys=False` (default). If you want to modify a dict keys, you should
enclose it in a list.

For instance:

```yaml
--- default.yaml
logging:
  metrics: ['train loss', 'val loss']
  styles: [{'train loss': 'red', 'val loss': 'blue'}]
--- experiment.yaml
logging:
  metrics: ['train loss', 'val loss', 'val acc']
  styles: [{'train loss': 'red', 'val loss': 'blue', 'val acc': 'cyan'}]
```

## Manipulate configs

You are encouraged to use the routines provided by `cliconfig` to manipulate configs
and even create your own config builder to replace `make_config`. You can use:

- `merge_config` and `merge_config_file` to merge your configs
- `parse_cli` to parse CLI arguments on config files and additional parameters
- `flat_config` and `unflat_config` to flatten and unflatten your configs
- `clean_pre_flat` to clean conflicting keys before flattening

You can also save, load and display configs with `save_config`,
`load_config` and `show_config` functions.

Note that theses functions are aimed to be use with configs but can be used with
any python dict.

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

- [ ] log warning when `None` is used in CLI (considered as string a by PyYAML)

Done:

- [x] add `merge_config_file` to merge from path (= `merge_config` that includes
  config loading)
- [x] add `clean_pre_flat` to solve conflicting flatten and unflatten parameters
  before flattening the config
- [x] avoid changing keys order in merge_config

## License

Copyright (C) 2023  Valentin Goldité

This program is free software: you can redistribute it and/or modify it under the
terms of the [MIT License](LICENSE). This program is distributed in the hope that
it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

This project is free to use for COMMERCIAL USE, MODIFICATION, DISTRIBUTION and
PRIVATE USE as long as the original license is include as well as this copy
right notice at the top of the modified files.
