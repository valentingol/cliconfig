# Quick start

Create yaml file(s) that contains your default configurations. All the parameters
should be listed (see later to organize them simply in case of big config files).

```yaml
# default1.yaml
param1: 1
param2: 1
letters:
  letter1: a
  letter2: b

# default2.yaml
param1: 1
param2: 2  # will override param2 from default1.yaml
letters.letter3: c  # add a new parameter
```

Get your config in your python code:

```python
# main.py
from cliconfig import make_config

config = make_config('default1.yaml', 'default2.yaml')
```

Add additional config file(s) that represent your experiments. They will override
the default values. Please note that new parameters that are not present in the
default configs are not allowed. This restriction is in place to prevent potential
typos in the config files from going unnoticed. It also enhances the readability
of the default config files and ensures retro-compatibility (see later to circumnavigate
it for particular cases). This restriction apart, the package allows a complete
liberty of config manipulation.

```yaml
# first.yaml
letters:
  letter3: C  # equivalent to "letters.letter3: 'C'"

# second.yaml
param1: -1
letters.letter1: A
```

Run your code with the additional config files AND eventually some other parameters
from command line. **Please respect the exact syntax for spaces and equal signs**.

```bash
python main.py --config first.yaml,second.yaml --param2=-2 --letters.letter2='B'
```

If you have multiple config files it is possible to pass a list with bracket.
Be careful, using ``--config=first.yaml`` will NOT be recognized as an additional config
file (space is important) but as a parameter called "config" with value "first.yaml"
(it then raises an error if no "config" parameter is on the default config).

```bash
Now the config look like this:

Config:
    param1: -1  # (overridden by second.yaml)
    param2: -2  # (overridden by command line args)
    letters:
        letter1: A  # (overridden by second.yaml)
        letter2: B  # (overridden by command line args)
        letter3: C  # (overridden by first.yaml)
```

You can also manipulate your config with the following functions:

```python
from cliconfig import load_config, save_config, show_config, update_config
show_config(config)  # print it
config.dict  # config as native dict
config.dict['letters']['letter1']  # access parameter via dict
config.letters.letter1  # access parameter via dots
config.letters.letter1 = 'G'  # modify parameter
del config.letters.letter1  # delete parameter
# Update config with a dict or another config
config = update_config(config, {'letters': {'letter1': 'H'}})
# Save the config as a yaml file
save_config(config, 'myconfig.yaml')
# Load the config and merge with the default configs if provided
# (useful if default configs were updated)
config = load_config('myconfig.yaml', default_config_paths=['default1.yaml', 'default2.yaml'])
```

The config object is just a wrapper around the config dict that allows to access the parameters
via dots (and containing the list of processings, see
[*Processing*](https://cliconfig.readthedocs.io/en/latest/processing.html)
section for details). That's all! Therefore, the config object is
very light and simple to use.

While the config object is simple, the possibilities to manipulate the config are endless.
See the next section for some default features. One of the core idea of this package is
to make it easy to add your own features for your specific needs.

## Use tags

By default, the package provides some "tags" represented as strings that start with
'@' and are placed at the end of a key containing a parameter. These tags change
the way the configuration is processed.

The default tags include:

* `@merge_add`, `@merge_before`, and `@merge_after`: These tags merge the dictionary
  loaded from the specified value (which should be a YAML path) into the current
  configuration. `@merge_add` allows only the merging of new keys and is useful for
  splitting non-overlapping sub-configurations into multiple files. `@merge_before` merges
  the current dictionary onto the loaded one, while `@merge_after` merges the loaded
  dictionary onto the current one. These tags are used to organize the config files simply.
* `@copy`: This tag copies a parameter from another key. The value should be a string
  that represents the flattened key. The copied value is then protected from further
  updates but will be updated if the copied key change during a merge.
* `@def`: This tag evaluate an expression to define the parameter value.
  The value associated to a parameter tagged with `@def` can contain any
  parameter name of the configuration. The most useful operators and built-in
  functions are supported, the random and math packages are also supported
  as well as some (safe) numpy, jax, tensorflow, pytorch functions.
  If/else statements and comprehension lists are also supported.
* `@type:<my type>`: This tag checks if the key matches the specified type `<my type>`
  after each update, even if the tag is no longer present. It tries to convert
  the type if it is not the good one. It supports basic types
  (except for tuples and sets, which are not handled by YAML) as well as unions
  (using "Union" or "|"), optional values, nested list, and nested dict.
  For instance: `@type:List[Dict[str, int|float]]`.
* `@select`: This tag select param/sub-config(s) to keep and delete the other
  param/sub-configs in the same parent config. The tagged key is not deleted if
  it is in the parent config.
* `@delete`: This tag deletes the param/sub-config from the config before merging.
  It is usefull to trigger a processing without keeping the key in the config.
* `@new`: This tag allows adding new key(s) to the config that are not already
  present in the default config(s). It can be used for single parameter or a
  sub-config. Disclaimer: it is preferable to have exhaustive default config(s)
  instead of abusing this tag for readability and for security concerning typos.
* `@dict`: This tag allows to have a dictionary object instead of a sub-config
  where you can modify the keys (see the
  [*Edge cases*](https://cliconfig.readthedocs.io/en/latest/edge_cases.html) section)

The tags are applied in a particular order that ensure no conflict between them.

Please note that the tags serve as triggers for internal processing and will be
automatically removed from the key after processing.

It is also possible to combine multiple tags. For example:

```yaml
# main.yaml
path_1@merge_add: sub1.yaml
path_2@merge_add: sub2.yaml
config3.selection@delete@select: config3.param1

# sub1.yaml
config1:
  param@copy@type:int: config2.param
  param2@type:float: 1  # wrong type -> converted to float

# sub2.yaml
config2.param: 2
config3:
  param1@def: "[(config1.param2 + config2.param) / 2] * 2 if config2.param else None"
  param2: 3
my_dict@dict:
  key1: 1
  key2: 2
```

Note that can also use YAML tags separated with "@" (like `key: !tag@tag2 value`)
to add tags instead of putting them in the parameter name (like `key@tag@tag2: value`).

Here `main.yaml` is interpreted like:

```yaml
path_1: sub1.yaml
path_2: sub2.yaml
config1:
  param: 2  # the value of config2.param
  param2: 1.0  # converted to float
config2:
  param: 2
config3:
  param1: [1.5, 1.5]
  # param2 is deleted because it is not in the selection
my_dict: {key1: 1, key2: 2}  # (changing the whole dict further is allowed)
```

Then, all the parameters in `config1` have enforced types, changing
`config2.param` will also update `config1.param` accordingly (which is
protected by direct update). Finally, changing `config1.param2` or `config2.param`
will update `config3.param1` accordingly until a new value is set for `config3.param1`.

These side effects are not visible in the config but stored on processing objects.
They are objects that find the tags, remove them from config and apply a modification.
These processing are powerful tools that can be used to highly customize the
configuration at each step of the process.

You can easily create your own processing (associated to a tag or not).
The way to do it and a further explanation of them is available in the
[*Processing*](https://cliconfig.readthedocs.io/en/latest/processing.html) section
of the documentation.
