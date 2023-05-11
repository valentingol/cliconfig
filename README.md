# CLI Config

<p align="center">
  <img src="docs/_static/logo_extend.png" />
</p>

Lightweight library that provides routines to merge your configs (optionally nested)
and set parameters from the command line. It also provides processing functions that
can modify the entire config before and after each config merge, before config saving,
and after config loading. Additionally, it contains many routines to manipulate the
config, such as flattening or nesting dicts.

## Documentation :memo: [here](https://cliconfig.readthedocs.io/en/stable)

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

Create a default configuration that can be split across multiple files that will
be merged in sequence. There is no depth limit for the configuration parameters.

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

Now you can write these following lines in your python program to use this config
with `make_config`:

```python
# main.py
from cliconfig import make_config, show_dict

config, _ = make_config('default1.yaml', 'default2.yaml')
show_dict(config)  # print the config to check it
```

Then you can add one or multiple additional config files that will be passed on
command line and that will override the default values.

```yaml
---  # first.yaml
letters:
  letter3: C

---  # second.yaml
param1: -1
letters.letter1: A
```

**Please note that the additional config files must not introduce new parameters that
are not in the default configs, as it will result in an error**. This
restriction is in place to prevent potential typos in the config files from
going unnoticed. It also enhances the readability of the default config files
and ensures retro-compatibility.

Now you can launch the program with additional configurations and also set
individual parameters. The additional configs will be merged to the default
configs, then the parameters will be merged.

For example:

```bash
python main.py --config first.yaml,second.yaml --param2=-2 --letters.letter2='B'
```

*Note*: the additional configs are detected with `--config` followed by space
and separated by comma(s) **without space**. It also possible to pass a list.
The parameters are detected with the pattern `--<param>=<value>` without spaces.

It will show:

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

Note that the configurations is a native python dict at each step of the process.

## Use tags

By default, the package provides some "tags" represented as strings that start with
'@' and are placed at the end of a key containing a parameter. These tags change
the way the configuration is processed.

The default tags include:

* `@merge_add`, `@merge_before`, and `@merge_after`: These tags merge the dictionary
  loaded from the specified value (which should be a YAML path) into the current
  configuration. `@merge_add` allows only the merging of new keys and is useful for
  splitting different sub-configurations into multiple files. `@merge_before` merges
  the current dictionary onto the loaded one, while `@merge_after` merges the loaded
  dictionary onto the current one. These tags enable dynamic configuration merging
  on the command line, depending on the specified paths. Note that when multiple
  `@merge_before` or `@merge_after` tags merge the *same key*, the order of merging
  is not guaranteed as it depends on the order of the tags in the configuration file.
* `@copy`: This tag copies a parameter from another key. The value should be a string
  that represents the flattened key. The copied value is then protected from further
  updates but will be updated if the copied key change during a merge.
* `@type:<my type>`: This tag checks if the key matches the specified type `<my type>`
   after each update, even if the tag is no longer present. It supports basic types
   (except for tuples and sets, which are not handled by YAML) as well as unions
   (using "Union" or "|"), optional values, lists, and dictionaries.

The tags are applied in the following order: `@merge`, `@copy`, and then `@type`.

Please note that the tags serve as triggers for internal processing and will be
automatically removed from the key after processing.

It is also possible to combine multiple tags. For example:

```yaml
---  # main.yaml
path_1@merge_add: sub1.yaml
path_2@merge_add: sub2.yaml
--- # sub1.yaml
config1:
  param@copy@type:int: config2.param2
  param2@type:int: 1
--- # sub2.yaml
config2.param@type:None|int: 2
```

Here `main.yaml` will be interpreted like:

```yaml
path_1: sub1.yaml
path_2: sub2.yaml
config1:
    param: 2  # the value of config2.param2
    param2: 1
config2:
    param: 2
```

Now, all the parameters have a forced type and `config1.param2` will be
update if `config2.param2` is updated during a merge. These side effects are not
visible in the config but stored on processing classes. They are objects that
catch the tags, remove them from config and apply a modification on the config.
These processing are powerful tools that can be used to highly customize the
configuration process.

You can easily create your own processing (associated to a tag or not).
The way to do it and a further explanation of them is available in the
[*Processing*](https://cliconfig.readthedocs.io/en/latest/processing.html) section
of the documentation.

## Edge cases

**Please note that YAML does not support tuples and sets**, and therefore they
cannot be used in YAML files. If possible, consider using lists instead.

Moreover, YAML does not recognize "None" as a None object, but interprets it as a
string. If you wish to set a None object, you can use "null" or "Null" instead.

In the context of this package, dictionaries are treated as sub-configurations,
which means that modifying or adding keys directly in the additional configs may
not be possible (because only the merge of default configuration allow adding new keys).
If you need to modify or add keys within a dictionary, consider enclosing it in a list.

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
