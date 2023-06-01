# Quick start

Create a default configuration that can be split across multiple files that will
be merged in sequence. There is no depth limit for the
configuration parameters.

```yaml
# default1.yaml
param1: 1
param2: 0
letters:
  letter1: a
  letter2: b

# default2.yaml
param1: 1
param2: 2  # will override param2 from default1.yaml
letters.letter3: c  # add a new parameter
```

Now you can write these following lines in your python program to use this config
with `make_config`:

```python
# main.py
from cliconfig import load_config, make_config, show_config, save_config

config = make_config('default1.yaml', 'default2.yaml')
show_config(config)  # print the config to check it

config.dict  # the configuration as a native python dict
print('letter 1:', config.letters.letter1)  # access a parameter (you can also set it or delete it)

# Save the config as a yaml file
save_config(config, 'myconfig.yaml')
# Load the config and merge with the default configs if any (useful if default configs were updated)
config = load_config('myconfig.yaml', default_config_paths=['default1.yaml', 'default2.yaml'])
```

Then you can add one or multiple additional config files that will be passed on
command line and that will override the default values.

```yaml
# first.yaml
letters:
  letter3: C  # equivalent to "letters.letter3: 'C'"

# second.yaml
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
letter 1: A
```

Note that the configurations is stored as native python dict at each step of the process.
The config object is just a wrapper around this dict that allows to access the parameters
via dots (and containing the list of processings, see
[*Processing*](https://cliconfig.readthedocs.io/en/stable/processing.html)
section of the documentation for details.)

You can also use multiple documents in a single YAML file with the `---` separator. In
this case, the documents are merged in sequence and the file is interpreted as a single
additional config file containing this merged configuration.

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
  (using "Union" or "|"), optional values, nested list, and nested dict.
  For instance: `@type:List[Dict[str, int|float]]`.
* `@select`: This tag select sub-config(s) to keep and delete the other
  sub-configs in the same parent config
* `@delete`: This tag deletes the key from the config before merging.
* `@new`: This tag allows to add new key(s) to the config that are not already
  present in the default config(s). It can be used for single parameter or a
  sub-config. Disclaimer: it is preferable to have exhaustive default config(s)
  instead of abusing this tag for readability and for security concerning typos.

The tags are applied in the following order: `@merge`, `@select`, `@copy`, `@type`
and then `@delete`.

Please note that the tags serve as triggers for internal processing and will be
automatically removed from the key after processing.

It is also possible to combine multiple tags. For example:

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

Note that can also use YAML tags separated with "@" (like `key: !tag@tag2 value`)
to add tags instead of putting them in the parameter name (like `key@tag@tag2: value`).

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
(`config1.param` can also be None) and changing `config2.param` will also update
`config1.param` accordingly (which is protected by direct update).

These side effects are not visible in the config but stored on processing classes.
They are objects that find the tags, remove them from config and apply a modification.
These processing are powerful tools that can be used to highly customize the
configuration at each step of the process.

You can easily create your own processing (associated to a tag or not).
The way to do it and a further explanation of them is available in the
[*Processing*](https://cliconfig.readthedocs.io/en/latest/processing.html) section
of the documentation.
