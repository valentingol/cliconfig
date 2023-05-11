# CLI Config

</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/valentingol/cliconfig/main/docs/_static/logo_extend.png" />
</p>

Lightweight library that provides routines to merge your configs (optionally nested)
and set parameters from command line. It is also provide processing functions
that can change the whole config before and after each config merge, before config
saving and after config loading. It also contains many routines to manipulate
the config as flatten or nested dicts.

## Documentation :memo: : [here](https://cliconfig.readthedocs.io/en/stable)

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

## Quick start

First create a default config that can be split in multiple files that will be merged
(from left to right in `make_config` function). There is no limit of depth for the
configuration parameters.

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

config, _ = make_config('default1.yaml', 'default2.yaml')
show_config(config)  # print the config to check it
```

Then add one or multiple additional config files that will be passed on command line
and that will override the default values.

```yaml
---  # first.yaml
letters:
  letter3: C

---  # second.yaml
param1: -1
letters.letter1: A
```

**Be careful, the additional config files cannot add new parameters that are
not in default configs**. It is intended to prevent typos in the config files
that would not be detected. It also improves the readability of the config
files and the retro-compatibility.

Now you can launch the program with additional configurations and parameters.
The additional configs will be merged to the default configs, then the parameters
will be merged.

For example:

```bash
python main.py --config first.yaml,second.yaml --param2=-2 --letters.letter2='B'
```

*Note*: the additional configs are detected with `--config` followed by space
and separated by a comma **without space**. It also possible to pass a list.
The parameters are detected with the pattern `--<param>=<value>` without spaces.

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

Note that the configurations are native python dicts at each step of the process.

## Use tags

By default, the package provides some "tags" that are strings starting with `@`
and placed at the end of a key containing a parameter. It will change the way
the configuration is processed.

The default tags are:

* `@merge_add`, `@merge_before` and `@merge_after` to merge the dict loaded
  from the value (should be a yaml path!) to the current configuration.
  `@merge_add` allow only new keys and is useful to split sub-configurations
  in multiple files. `@merge_before` will merge the current dict on the loaded
  one and `@merge_after` will merge the loaded dict on the current one. With
  theses tags, you can dynamically merge configurations depending on the paths
  you set as values.
* `@copy` Copy a parameter from another key. The value should be a string containing
  this flatten key
* `@type:<my type>` To check if the key is of the type `<my type>` at each update
  even if the tag is no longer present. It supports basic type (except tuple and
  sets that are not handled by yaml) as well as union (with "Union" or "|"), optional,
  lists and dicts.

The tags are applied in this order: `@merge`, `@copy` then `@type`.

Note that the tags are only used to trigger internal processing and will be
automatically removed from the key after the processing.

You can also combine the tags, example:

```yaml
---  # main.yaml
path_1@merge_add: sub1.yaml
path_2@merge_add: sub2.yaml
--- # sub1.yaml
config1:
  param@copy@type:int: config1.param2
  param2@type:int: 1
--- # sub2.yaml
config2.param@type:None|int: 2
```

Here `main.yaml` is interpreted like:

```yaml
path_1: sub1.yaml
path_2: sub2.yaml
config1:
    param: 1
    param2: 1
config2:
    param: 2
```

and now, all the parameters have a forced type.

The point is that you can easily create your own processing associated to your
own tags. They provide a large number of possibilities to customize the
configuration process and are describe in the
[*Processing*](https://cliconfig.readthedocs.io/en/latest/processing.html) section
of the documentation.

## Edge cases

**Be careful, tuples and sets are not supported by YAML and cannot be used in
yaml files.**
Use lists instead if possible.

`None` is not recognized as a None object by YAML but as a string, you may use `null`
or `Null` instead if you want to set a None object.

Dicts are considered as sub-configs and so you may not be able to change
the keys in the additional configs. If you want to modify or add dict keys, you should
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

## How to contribute

For **development**, install the package dynamically and dev requirements with:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Everyone can contribute to CLI Config, and we value everyone’s contributions.
Please see our [contributing guidelines](CONTRIBUTING.md) for more information 🤗

## Todo

Priority:

* [x] allow passing new arguments by CLI (with warning and no actual merge)
* [ ] add a routine to check if a tag is in a key and robust to all other
  possible tags
* [ ] add an integration test with all built-in processing (and more)

Secondary:

* [ ] add `make_processing_keep_status` to make a processing that keep the
  status of a parameter across merged configs. The status is any python object
  returned by a function that takes the parameter as input
* [ ] add `ProcessSelect` (with tag "@select") to select a subconfig (or parameter)
  and delete the others configs at the same level (to cure the resulting config)
* [ ] allow nested types in `ProcessTyping`
* [ ] add DefaultProcessing that add default processing to list of processing

## License

Copyright (C) 2023  Valentin Goldité

This program is free software: you can redistribute it and/or modify it under the
terms of the [MIT License](LICENSE). This program is distributed in the hope that
it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

This project is free to use for COMMERCIAL USE, MODIFICATION, DISTRIBUTION and
PRIVATE USE as long as the original license is include as well as this copy
right notice at the top of the modified files.
