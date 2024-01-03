# Alternative ways to create a config

## From a python dict

```python
from cliconfig import Config
my_dict = {'param1': 1, 'param2': 2}
config = Config(my_dict)
```

You can also add built-in or custom processings:

```python
from cliconfig import Config, create_processing_value
from cliconfig.processing.builtin import ProcessCopy
my_dict = {'param1': 1, 'param2': 2}
my_proc = create_processing_value(lambda x: x+1, "premerge", tag_name='add1')
config = Config(my_dict, [my_proc, ProcessCopy()])
```

## From a yaml file without command line arguments (useful for notebooks)

```python

from cliconfig import make_config
config = make_config('my_yaml_file.yaml', no_cli=True)
```

You can merge multiple yaml files that will be considered as default configs
(new parameter names are allowed).

```python
from cliconfig import make_config
config = make_config('config1.yaml', 'config2.yaml', no_cli=True)
```

You can also pass a list of processing objects like usual.

## From a config (make a copy)

```python
from cliconfig.config_routines import copy_config
config2 = copy_config(config)
```

## From two dicts (or configs) to merge one into the other

```python
from cliconfig import Config, update_config
new_config = update_config(Config(config1), config2)  # if config1 is a dict
new_config = update_config(config1, config2)  # if config1 is a Config
```

These two lines work whether the config2 is a dict or a Config.
Note that the second config will override the first one.

## From a list of arguments

Assuming the arguments are under the format
`['--key1=value1', '--key2.key3=value2']`:

```python
from cliconfig import Config, unflatten_config
from cliconfig.cli_parser import parse_cli
my_args = ['--key1=value1', '--key2.key3=value2']
config = Config(parse_cli(my_args)[0])  # flat
config = unflatten_config(config)
```

## From a yaml formatted string

```python
from yaml import safe_load
from cliconfig import Config, unflatten_config
yaml_txt = """
a:
  d: [2, 3]
  b.c: {d: 4, e: 5}
"""
config = Config(safe_load(yaml_txt))  # mix flat and nested
config = unflatten_config(config)
```
