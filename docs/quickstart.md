# Quick start

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

* `@merge_add`, `@merge_before` and `@merge_after` to merge the dict loaded from the
  value (should be a yaml path!) to the current configuration. `@merge_add` allow
  only new keys and is useful to split sub-configurations in multiple files.
  `@merge_before` will merge the current dict on the loaded one and `@merge_after`
  will merge the loaded dict on the current one. With theses tags, you can dynamically
  merge configurations depending on the paths you set as values.
* `@copy` Copy a parameter from another key. The value should be a string containing
  this flatten key
* `@type:<my type>` To check if the key is of the type `<my type>` at each update
  even if the tag is no longer present. It supports basic type (except tuple and sets
  that are not handled by yaml) as well as union (with "Union" or "|"), optional,
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
config1.param@copy@type:int: config1.param2
config1.param2@type:int: 1
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

The point is that you can easily create your own processing associated to your own tags.
They provide a large number of possibilities to customize the configuration process
and are describe in the
[*Processing*](https://cliconfig.readthedocs.io/en/latest/processing.html) section
of the documentation.
