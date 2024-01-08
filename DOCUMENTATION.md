<p align="center">
  <img
  src="https://raw.githubusercontent.com/valentingol/cliconfig/main/docs/_static/logo_extend_black.png"
  alt="CLI-Config-logo" width="100%" height="100%"
  />
</p>

*CLI Config* is a lightweight library that provides routines to merge nested configs
and set parameters from command line. It contains many routines to create and manipulate
the config as flatten or nested python dictionaries. It also provides processing functions
that can change the whole configuration before and after each config manipulation.

The package was initially designed for machine learning experiments where the
number of parameters is huge and a lot of them have to be set by the user between
each experiment. If your project matches this description, this package is for you!

[Documentation](https://valentingol.github.io/cliconfig)

[Pypi package](https://pypi.org/project/cliconfig/)

[Source code (Github)](https://github.com/valentingol/cliconfig/)

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
[![Documentation Status](https://github.com/valentingol/cliconfig/actions/workflows/pdoc.yaml/badge.svg)](https://valentingol.github.io/cliconfig)

Official badge :
[![Config](https://custom-icon-badges.demolab.com/badge/cliconfig-black?logo=cliconfig)](https://github.com/valentingol/cliconfig)

## Installation

In a new virtual environment, simply install the package via
[pypi](https://pypi.org/project/cliconfig/):

```bash
pip install cliconfig
```

This package is OS independent and supported on Linux, macOS and Windows.

## Quick start

Create yaml file(s) that contain your default configuration. All the parameters
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
the default values.

```yaml
# first.yaml
letters:
  letter3: C  # equivalent to "letters.letter3: 'C'"

# second.yaml
param1: -1
letters.letter1: A
```

Please note that new parameters that are not present in the
default configs are not allowed. This restriction is in place to prevent potential
typos in the config files from going unnoticed. It also enhances the readability
of the default config files and ensures retro-compatibility (see later to circumnavigate
it for particular cases). This restriction apart, the package allows a complete
liberty of config manipulation.

Run your code with the additional config files AND eventually some other parameters
from command line. **Please respect the exact syntax for spaces and equal signs**.

```bash
python main.py --config first.yaml,second.yaml --param2=-2 --letters.letter2='B'
```

If you have multiple config files it is possible to pass a list with brackets.
Be careful, using ``--config=first.yaml`` will NOT be recognized as an additional config
file (space is important) but as a parameter called "config" with value "first.yaml"
(it then raises an error if no "config" parameter is on the default config).

Now the config look like this:

```bash
Config:
    param1: -1  # overridden by second.yaml
    param2: -2  # overridden by command line args
    letters:
        letter1: A  # overridden by second.yaml
        letter2: B  # overridden by command line args
        letter3: C  # overridden by first.yaml
```

You can also manipulate your config with the following functions:

```python
from cliconfig import load_config, save_config, show_config, update_config
show_config(config)  # print config
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
via dots (and containing the list of processings, see the
[*Processing*](https://valentingol.github.io/cliconfig/cliconfig.html#processing)
section for details). That's all! Therefore, the config object is
very light and simple to use.

While the config object is simple, the possibilities to manipulate the config via
processings are endless. See the next section for some default features. One of the
core idea of this package is to make it easy to add your own config features for your
specific needs.

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
  dictionary onto the current one. These tags are used to organize multiple config files.
* `@copy`: This tag copies a parameter value from another parameter name. The value
  associated to the parameter with this tag should be a string
  that represents the flattened key. The copied value is then protected from further
  updates but will be dynamically updated if the copied key change during a merge.
* `@def`: This tag evaluate an expression to define the parameter value.
  The value associated to a parameter tagged with `@def` can contain any
  parameter name of the configuration. The most useful operators and built-in
  functions are supported, the `random` and `math` packages are also supported
  as well as some (safe) `numpy`, `jax`, `tensorflow`, `torch` functions.
  If/else statements and comprehension lists are also supported.
* `@type:<my type>`: This tag checks if the key matches the specified type `<my type>`
  after each update, even if the tag is no longer present. It tries to convert
  the type if it is not the good one. It supports basic types as well as unions
  (using either "Union" or "|"), optional values, nested list/set/tuple/dict.
  For instance: `my_param@type:List[Dict[str, int|float]]: [{"a": 0}]`.
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
  [*Edge cases*](https://valentingol.github.io/cliconfig/cliconfig.html#edge-cases) section)

The tags are applied in a particular order that ensure no conflict between them.

Please note that the tags serve as triggers for internal processing and will be
automatically removed from the key before you can use it. The tags are designed to
give instructions to python without being visible in the config.

It is also possible to combine multiple tags. For example:

```yaml
# main.yaml
path_1@merge_add: sub1.yaml
path_2@merge_add: sub2.yaml
config3.selection@delete@select: config3.param1

# sub1.yaml
config1:
  param@copy@type:int: config2.param
  param2@type:float: 1  # int: wrong type -> converted to float

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
[*Processing*](https://valentingol.github.io/cliconfig/cliconfig.html#processing)
section of the documentation.

## Edge cases

* **Please note that YAML does not support tuples and sets**, and therefore they
  cannot be used in YAML files. If possible, consider using lists instead.

* Moreover, YAML does not recognize "None" as a None object, but interprets it as a
  string. If you wish to set a None object, you can use "null" or "Null" instead.

* "@" is a special character used by the package to identify tags. You can't use it
  in your parameters names (but you can use it in your values). It will raise an error
  if you try to do so.

* "dict" and "process_list" are reserved names of attributes and should not be used
  as sub-config or parameter names. It can raise an error if you try to access them
  as config attributes (with dots).

In the context of this package, dictionaries are treated as sub-configurations,
which means that modifying or adding keys directly in the additional configs may
not be possible (because only the merge of default configuration allow adding new keys).
If you need to have a dictionary object where you can modify the keys, consider
using the `@dict` tag:

For instance:

```yaml
# default.yaml
logging:
  metrics: [train loss, val loss]
  styles@dict: {train_loss: red, val_loss: blue}
# additional.yaml
logging:
  metrics: [train loss, val acc]
  styles@dict: {train_loss: red, val_acc: cyan}
```

Like a sub-config, the dictionary can be accessed with the dot notation like this:
`config.logging.styles.val_acc` and will return "cyan".

## Processing

Processings are powerful tools to modify the config at each step of the lifecycle of
a configuration. More precisely, you can use processings to modify the full
configuration before and after each merge, after loading, and before saving the config.

The processings are applied via a processing object that have five methods
(called "processing" to simplify): `premerge`, `postmerge`, `endbuild`, `postload`
and `presave`. These names correspond to the timing they are applied. Each processing
has the signature:

```python
def premerge(self, flat_config: Config) -> Config:
    ...
    return flat_config
```

Where `Config` is a simple class containing only two attributes (and no methods):
`dict` that is the configuration dict and `process_list`, the list of processing objects
(we discuss this in a section below). Note that it is
also the class of the object returned by the `make_config` function.

They only take a flat config as input i.e a config containing a dict of depth 1 with
dot-separated keys and return the modified flat dict (and keep it flat!).

In this section, you will learn how they work and how to create your own to make
whatever you want with the config.

### Why a flat dict?

The idea is that when we construct a config, we manipulate dictionaries that contain
both nested sub-dictionaries and flat keys simultaneously. To simplify this process, the
dictionaries are systematically flattened before merging. This approach makes things
simpler and prevents duplicated keys within the same configuration, as shown in the
example:

```python
config = {'a': {'b': 1}, 'a.b': 2}
```

More generally, all config modifications are performed using flat dictionaries
during config construction, and the same applies to processings. For processings,
it is even more interesting as you can have access to the full sub-config names
to make your processing if needed.

However, it's important to note that after building your config with `make_config`,
the dict will be unflattened to its normal nested configuration structure.

### Processing order

The order in which the processings are triggered is crucial because they modify
the config and consequently affect the behavior of subsequent processings.
To manage this order, the processing class have five float attributes representing
the order of the five processing methods: premerge, postmerge, endbuild, postload,
and presave.

Here's a basic example to illustrate the significance of the order:

```yaml
# config1.yaml
merge@merge_add@delete: config2.yaml
param: 1
# config2.yaml
param2: 2
```

In this example, we want to build a global config using `config1.yaml`. This file contains only
half of the parameters, and the other half is in `config2.yaml`. Then, we add a key
with the name of our choice, here "merge", tagged with `@merge_add` to merge
`config2.yaml` before the global config update. We add the `@delete` tag to delete
the key "merge" before merging with the global config because in this case, there is
no key with the name "merge" in the global config, and it would raise an error as
it is not possible to ass new keys.

`@merge_add` and `@delete` has both only a pre-merge effect. Let's check the orders.
It is `-20.0` for merge and `30.0` for delete. So merge trigger first, add `param2` and
the "merge" key is deleted after it. If the orders were reversed, the key would have been
deleted before merge processing and so the `param2` would not have been updated with the
value of 2 and the resulting configuration would potentially not have been
the expected one at all.

Therefore, it is crucial to carefully manage the order when creating your own
processings!

Some useful ranges to choose your order:

* not important: order = 0 (default)
* if it checks/modifies the config before applying any processing: order < -25
* if it adds new parameters: -25 < order < -5
* if it updates a value based on itself: -5 < order < 5
* if it updates a value based on other keys: 5 < order < 15
* if it checks a property on a value: 15 < order < 25
* if it deletes other key(s) but you want to trigger the tags before: 25 < order < 35
* final check/modification after all processings: order > 35

Note: a pre-merge order should not be greater than 1000, the order of the default
processing `ProcessCheckTags` that raise an error if tags still exist at the end
of the pre-merge step.

### Create basic processing

#### Processing that modify a single value

One of the most useful kind of processing look for parameters which names match a certain
pattern (e.g a prefix or a suffix) or contain a specific tag and modify their values
depending on their current ones.

To simplify the creation of such a process, we provide the `cliconfig.create_processing_value` function.
This function allows you to quickly create a processing that matches a regular
expression or a specific tag name (in which case the tag is removed after pre-merging).
You specify the function to be applied on the value to modify it, and optionally,
the order of the processing. Additionally, there is a `persistent` argument, which is
a boolean value indicating whether encountering the tag (if a tag is used) once in
a parameter name will continue to trigger the processing for this parameter
even after the tag is removed. By default, it is `False`. Finally, you can set
the processing type (pre-merge, post-merge, etc.) at your convenience. Default is pre-merge.

Here's an example to illustrate:

```python
proc = create_processing_value(lambda x: str(x), 'premerge', tag_name='convert_str', persistent=True)
config = make_config(default_config, process_list=[proc])
```

In this example, the config `{"subconfig.param@convert_str": 1}` will
be converted to `{"subconfig.param": "1"}`. Moreover, the keys `subconfig.param`
will be permanently converted to strings before every merge.

It's worth noting that you can also use functions that have side effects without
necessarily changing the value itself. For example, you can use a function to
check if a certain condition is met by the value.

It is also possible to pass the flat config as a second argument to the function.
For example:

```yaml
# config.yaml
param: 1
param2@eval: "config.param + 1"
```

```python
proc = create_processing_value(
    lambda x, config: eval(x, {"config": config}),
    tag_name="eval",
    persistent=False,
)
# (Note that the `eval` function is not safe and the code above
# should not be used in case of untrusted config)
```

Here the value of `param2` will be evaluated to 2 at pre-merge step.

#### Pre-merge/post-merge processing that protect a property from being modified

Another useful kind of processing is a processing that ensure to keep a certain
property on the value. For this kind of processing, you can use
`cliconfig.create_processing_keep_property`. It takes a function that returns
the property from the value, the regex or the tag name like the previous function,
and the order of the pre-merge and the post-merge.

The pre-merge processing looks for keys that match the tag or the regex, apply
the function on the value and store the result (= the "property").
The post-merge and end-build processing will check that the property is the same as
the one stored during pre-merge. If not, it will raise an error.

Examples:

A processing that enforce the types of all the parameters to be constant
(equal to the type of the first value encountered):

```python
create_processing_keep_property(
    type,
    regex=".*",
    premerge_order=15.0,
    postmerge_order=15.0,
    endbuild_order=15.0
)
```

A processing that protect parameters tagged with @protect from being changed:

```python
create_processing_keep_property(
    lambda x: x,
    tag_name="protect",
    premerge_order=15.0,
    postmerge_order=15.0,
    endbuild_order=15.0
)
```

Each time you choose the order `15.0` because it is a good value for processing that
made checks on the values. Indeed, processings that change the values such as
`ProcessCopy` have an order that is generally $\leq$ 10.0.

It is also possible to pass the flat config as a second argument to the function
similarly to `create_processing_value`.

### Create your processing classes (Advanced)

To create your own processing classes and unlock more possibilities, you simply
need to overload the methods of the Processing class to modify the config at the
desired timings. To do so, you often need to manipulate tags.

#### Manipulate the tags

Tags are useful for triggering a processing, as we have seen. However, we need
to be cautious because tagging a key modifies its name and can lead to conflicts
when using processing. To address this issue, we provide tag routines in
`cliconfig.tag_routines`. These routines include:

* `is_tag_in`: Checks if a tag is in a key. It looks for the exact tag name.
  If `full_key` is True, it looks for all the flat key, including sub-configs
  (default: False)
* `clean_tag`: Removes a specific tag (based on its exact name) from a key.
  It is helpful to remove the tag after pre-merging.
* `clean_all_tags`: Removes all tags from a key. This is helpful each time you
  need the true parameter name.
* `clean_dict_tags`: Removes all tags from a dictionary and returns the cleaned
  dict along with a list of keys that contained tags. This is helpful to get all
  the parameter names of a full dict with tags.

With these tools, we can write a processing, for example, that searches for all
parameters with a tag `@look` ant that prints their sorted values at the end of
the post-merging.

```python
class ProcessPrintSorted(Processing):
    """Print the parameters tagged with "@look", sorted by value on post-merge."""

    def __init__(self) -> None:
        super().__init__()
        self.looked_keys: Set[str] = set()
        # Pre-merge just look for the tag so order is not important
        self.premerge_order = 0.0
        # Post-merge should be after the copy processing if we want the final values
        # on post-merge
        self.postmerge_order = 15.0

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        # Browse a freeze version of the dict (because we will modify it to remove tags)
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if is_tag_in(flat_key, "look"):  # Check if the key contains the tag
                # Remove the tag and update the dict
                new_key = clean_tag(flat_key, "look")
                flat_config.dict[new_key] = value
                del flat_config.dict[flat_key]
                # Store the key
                clean_key = clean_all_tags(key)  # remove all tags = true parameter name
                self.looked_keys.add(clean_key)
        return flat_config

    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing."""
        values = []
        for key in self.looked_keys:
            # IMPORTANT
            # ("if key in flat_config.dict:" is important in case of some keys were
            # removed or if multiple dicts with different parameters are seen by
            # the processing)
            if key in flat_config.dict:
                values.append(flat_config.dict[key])
        print("The sorted looked values are: ", sorted(values))
        # If we don't want to keep the looked keys for further print:
        self.looked_keys = set()

        return flat_config

# And to use it:
config = make_config("main.yaml", process_list=[ProcessPrintSorted()])
```

**Important note**: After all pre-merge processings, the config should no longer contains
tags as they should be removed by pre-merge processings. Otherwise, a security
processing raises an error. It is then not necessary to take care on tags on post-merge,
and pre-save.

#### Merge, save or load configs in processing

The key concept is that as long as we deal with processings, the elementary operations
on the config are not actually to merge, save, and load a config, but rather:

* Applying pre-merge processing, then merging, then applying post-merge processing.
* Applying end-build processing at the end of the config building.
* Applying pres-ave processing and then saving a config.
* Loading a config and then applying post-load processing.

These three operations are in `cliconfig.process_routines` and called
`merge_processing`, `end_build_processing`, `save_processing`, and `load_processing`,
respectively. They take as input a Config object that contains as we see the list of processing.

Now, the trick is that sometimes we want to apply these operations to the processing
themselves, particularly when we want to modify a part of the configuration instead
of just a single parameter (such as merging two configurations). This is why it is
particularly useful to have access to the full Config object and not only the
dict.

For example, consider the tag `@merge_add`, which triggers a processing before
merging and merges the config loaded from a specified path (the value) into the
current config. We may want to see what happens if we merge a config that also
contains a `@merge_add` tag within it:

```yaml
# main.yaml
config_path1@merge_add: path1.yaml
# path1.yaml
param1: 1
config_path2@merge_add: path2.yaml
# path2.yaml
param2: 2
```

Now, let's consider we want to merge the config `main.yaml` with another config.
During the pre-merge processing, we encounter the tag `@merge_add`. This tag is
removed, and the config found at `path1.yaml` will be merged into the `main.yaml`
config. However before this, it triggers the pre-merging.

Therefore, before the merge `path1.yaml`, the processing discovers the key
`config_path2@merge_add` and merges the config found at `path2.yaml` into `path1.yaml`.
Then, `path1.yaml` is merged into `main.yaml`. Finally, the resulting configuration
can be interpreted as follows:

```python
{'param1': 1, 'param2': 2, 'config_path1': 'path1.yaml', 'config_path2': 'path2.yaml'}
```

before being merged itself with another config. Note that is not only a processing that
allows to organize the configuration on multiple files. In fact, it also allows you for
instance to choose a particular configuration among several ones by setting the path
as value of the tagged key (as long as this config is on the default configs).

#### Change processing list in processing (Still more advanced)

Note that the processing functions receive the list of processing objects as an
input and update as an attribute of the processing object. This means that it
is possible to manually modify this list in processing functions.

**Warning**: The processing list to apply during pre/post-merge, pre-save and
post-load are determined before the first processing is applied. Therefore, you can't
add or remove processing and expect it to be effective during the current merge/save/load.
However, if you modify their internal variables it will be effective immediately.

Here an example of a processing that remove the type check of a parameter in
`ProcessTyping` processing. It is then possible for instance to force another
type (it is not possible otherwise).

```python
from cliconfig.processing.builtin import ProcessTyping

class ProcessBypassTyping(Processing):
    """Bypass type check of ProcessTyping for parameters tagged with "@bypass_typing".

    In pre-merge it looks for a parameter with the tag "@bypass_typing",
    removes it and change the internal ProcessTyping variables to avoid
    checking the type of the parameter with ProcessTyping.
    """

    def __init__(self) -> None:
        super().__init__()
        self.bypassed_forced_types: Dict[str, tuple] = {}
        # Before ProcessTyping pre-merge to let it change the type
        self.premerge_order = 1.0

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if is_tag_in(flat_key, "bypass_typing"):
                new_key = clean_tag(flat_key, "bypass_typing")
                flat_config.dict[new_key] = value
                del flat_config.dict[flat_key]
                clean_key = clean_all_tags(flat_key)
                for processing in flat_config.process_list:
                    if (isinstance(processing, ProcessTyping)
                            and clean_key in processing.forced_types):
                        forced_type = processing.forced_types.pop(clean_key)
                        self.bypassed_forced_types[clean_key] = forced_type
        return flat_config

# Without bypass:
config1 = Config({"a@type:int": 0}, [ProcessBypassTyping(), ProcessTyping()])
config2 = Config({"a@type:str": "a"}, [])
config = merge_flat_processing(config1, config2)
# > Error: try to change the forced type of "a" from int to str

# With bypass:
config1 = Config({"a@type:int": 0}, [ProcessBypassTyping(), ProcessTyping()])
config2 = Config({"a@bypass_typing@type:str": "a"}, [])
config = merge_flat_processing(config1, config2)
# > No error
```

## Alternative ways to create a config

### From a python dict

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

### From a yaml file without command line arguments (useful for notebooks)

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

### From a config (make a copy)

```python
from cliconfig.config_routines import copy_config
config2 = copy_config(config)
```

### From two dicts (or configs) to merge one into the other

```python
from cliconfig import Config, update_config
new_config = update_config(Config(config1), config2)  # if config1 is a dict
new_config = update_config(config1, config2)  # if config1 is a Config
```

These two lines work whether the config2 is a dict or a Config.
Note that the second config will override the first one.

### From a list of arguments

Assuming the arguments are under the format
`['--key1=value1', '--key2.key3=value2']`:

```python
from cliconfig import Config, unflatten_config
from cliconfig.cli_parser import parse_cli
my_args = ['--key1=value1', '--key2.key3=value2']
config = Config(parse_cli(my_args)[0])  # flat
config = unflatten_config(config)
```

### From a yaml formatted string

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

## Hyperparameter search with Weights&Biases

Making hyperparameter search easier and more effective with
[Weights&Biases sweeps](https://wandb.ai/site)! This example shows you how to combine them
with cliconfig supporting nested configuration:

```python
# main.py
from cliconfig.config_routines import update_config
from cliconfig.dict_routines import flatten
import wandb

def main() -> None:
    """Main function."""
    # Create a cliconfig based on CLI
    config = make_config('default.yaml')
    # Initialize wandb to create wandb.config eventually modified by sweep
    # Note that the config is flattened because wandb sweep does not support
    # nested config (yet)
    wandb.init(config=flatten(config.dict))
    # Sync the cliconfig with wandb.config
    config = update_config(config, wandb.config)
    # Now the config is eventually updated with the sweep,
    # unflattened and ready to be used

    run(config)

if __name__ == '__main__':
    main()
```

Now you can create your sweep configuration use wandb sweep either from CLI or
from python following the [wandb tutorial](https://docs.wandb.ai/guides/sweeps).

For instance with a configuration containing train and data sub-configurations:

```yaml
# sweep.yaml
program: main.py
method: bayes
metric:
  name: val_loss
  goal: minimize
parameters:
    train.learning_rate:
        distribution: log_uniform_values
        min: 0.0001
        max: 0.1
    train.optimizer.name:
        values: ["adam", "sgd"]
    data.batch_size:
        values: [32, 64, 128]
```

```bash
$ wandb sweep sweep.yaml
sweep_id: ...
$ wandb agent <sweep_id>
```

This makes a bayesian search over the learning rate, the optimizer and the batch size
to minimize the final validation loss.

## How to contribute

For **development**, install the package dynamically and dev requirements with:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Everyone can contribute to CLI Config, and we value everyone’s contributions. Please see our
[contributing guidelines](https://github.com/valentingol/cliconfig/blob/main/CONTRIBUTING.md)
for more information 🤗
