# Processing

Processings are powerful tools to modify the config at each step of the lifecycle of
a configuration. More precisely, you can use processings to modify the full
configuration before and after each merge, after loading, and before saving the config.

The processings are applied via a processing object that have four methods
(called "processing" to simplify): `premerge`, `postmerge`, `postload` and `presave`.
These names correspond to the timing they are applied. Each processing have
the signature:

```python
def premerge(self, flat_config: Config) -> Config:
    ...
```

Where `Config` is a simple dataclass containing only two fields: `dict` that is the
configuration dict and `process_list`, the list of processing objects
(we discuss about this in a section below). Note that it is
also the class of the object returned by the `make_config` function.

They only take a flat config as input i.e a config containing a dict of depth 1 with
dot-separated keys and return the modified flat dict (and keep it flat!).

In this section, you will learn how they work and how to create your own to make
whatever you want with the config (we hope!).

## Why a flat dict?

The idea is that when we construct a config, we manipulate dictionaries that contain
both nested sub-dicts and flat keys simultaneously. To simplify this process, the
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

## Processing order

The order in which the processings are triggered is crucial because they modify
the config and consequently affect the behavior of subsequent processings.
To manage this order, the processing class have four float attributes representing
the order of the four processing methods: premerge, postmerge, postload, and presave.

Here's a basic example to illustrate the significance of the order:

```yaml
--- # config.yaml
param1@type:int@copy: 'param2'
param2@type:int: 1
```

In this example, we want to enforce the types of the parameters. Additionally, `param1`
is intended to be a copy of `param2` and naturally, it is forced to have the same type.

During the pre-merge processing, the tags are removed, and information about the
enforced types and the copy operation is gathered on processing attributes.
Then, a merge is performed (assuming no modifications to our parameters at
this point to simplify), followed by the post-merge processing.

Now, what happens if the type post-merge processing triggers before the
copy post-merge processing? It will check the value, which is `"param2"`,
and raise an error because it is not an integer (the forced type got during pre-merge).
However, if the copy processing triggers before the type processing, it will copy the
value of `param2` (which is `1`) to `param1`, and then the type processing will not
encounter a wrong value.

Fortunately, the post-merge orders are set as follows: `20.0` for the type processing
and `10.0` for the copy processing. As a result, the copy processing triggers first.
Therefore, it is crucial to carefully manage the order when creating your own
processings!

## Create basic processing

### Pre-merge processing dealing with a single value at a time

The pre-merge processing is particularly useful as it allows you to modify the input
config provided by the user and create the resulting Python dictionary that stores the
configuration for your experiment. It serves as the interface between the user config
and the final config.

In a lot of cases, you may need to get parameters which names match a certain
patterns (e.g a prefix or a suffix) or contain a specific tag and modify their values
depending on their current ones.

To simplify this process, we provide the `cliconfig.create_processing_value` function.
This function allows you to quickly create a processing that matches a regular
expression or a specific tag name (in which case the tag is removed after pre-merging).
You specify the function to be applied on the value to modify it, and optionally,
the order of the processing. Additionally, there is a `persistent` argument, which is
a boolean value indicating whether encountering the tag (if a tag is used) once in
a parameter name will continue to trigger the processing for this parameter
even after the tag is removed.

Here's an example to illustrate:

```python
proc = create_processing_value(lambda x: str(x), tag='convert_str', persistent=True)
config = make_config(default_config, process_list=[proc])
```

In this example, the config `{"subconfig.param@convert_str": 1}` will
be converted to `{"subconfig.param": "1"}`. Moreover, the keys `subconfig.param`
will be permanently converted to strings before every merge.

It's worth noting that you can also use functions that have side effects without
necessarily changing the value itself. For example, you can use a function to
check if a certain condition is met by the value.

## Create your processing classes (Advanced)

To create your own processing classes and unlock more possibilities, you simply
need to overload the methods of the Processing class to modify the config at the
desired timings. To do so, you often need to manipulate tags.

### Manipulate the tags

Tags are useful for triggering a processing, as we have seen. However, we need
to be cautious because tagging a key modifies its name and can lead to conflicts
when using processing. To address this issue, we provide tag routines in
`cliconfig.tag_routines`. These routines include:

* `is_tag_in`: Checks if a tag is in a key. It look for the exact tag name.
  If `full_key` is True, it looks for all the fkat key, including sub-configs
  (default: False)
* `clean_tag`: Removes a specific tag (based on its exact name) from a key.
  It is helpful to remove the tag after pre-merging.
* `clean_all_tags`: Removes all tags from a key. This is helpful each time you
  need the true parameter name.
* `clean_dict_tags`: Removes all tags from a dictionary and returns the cleaned
  dict along with a list of keys that contained tags. This is helpful to get all
  the parameter names of a full dict with tags.

With these tools, we can write a processing, for example, that searches for the
tag `"@protect"` and restores the value of a parameter after every merge.
In other words, the value is protected from being changed by the user.

```python
class ProcessProtect(Processing):
    """Prevent a value from being changed after merging."""

    def __init__(self) -> None:
        super().__init__()
        self.protected_params: Dict[str, Any] = {}

    # NOTE: process_list will not be used here
    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing."""
        # Browse a freeze version of the dict
        items = list(flat_config.dict.items())
        for flat_key, value in items:
            if is_tag_in(flat_key, "protect"):
                # Remove the tag and update the dict
                new_key = clean_tag(flat_key, "protect")
                del flat_config.dict[flat_key]
                flat_config.dict[new_key] = value
                # Store the value
                clean_key = clean_all_tags(key)  # remove all tags = true parameter name
                self.protected_params[clean_key] = value
        return flat_config

    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing."""
        # Restore the values and print a warning if they were modified
        for key, value in self.protected_params.items():
            # (`if key in flat_dict:` is important: the dicts seen by the processing
            # not necessarily contains all the same keys)
            if key in flat_config.dict:
                if flat_config.dict[key] != value:
                    print(f"WARNING: protected key {key} was modified by the merge")
                flat_config.dict[key] = value
        return flat_config


# Use it:
config = make_config("main.yaml", process_list=[ProcessProtect()])
```

**Important note**: After all pre-merge processings, the config should no longer contains
tags as they should be removed by pre-merge processings. Otherwise, a security
processing raises an error. It is then not necessary to take care on tags on post-merge,
and pre-save.

### Merge, save or load configs in processing

The key concept is that as long as we deal with processings, the elementary operations
on the config are not actually to merge, save, and load a config, but rather:

* Applying pre-merge processing, then merging, then applying post-merge processing.
* Applying pres-ave processing and then saving a config.
* Loading a config and then applying post-load processing.

These three operations are in `cliconfig.process_routines` and called
`merge_processing`, `save_processing`, and `load_processing`, respectively. They
takes as input a Config object that contains as we see the list of processing.

Now, the trick is that sometimes we want to apply these operations to the processing
themselves, particularly when we want to modify a part of the configuration instead
of just a single parameter (such as merging two configurations). This is why it is
particularly useful to have an access to the full Config object and not only the
dict.

For example, consider the tag "@merge_add," which triggers a processing before
merging and merges the config loaded from a specified path (the value) into the
current config. We may want to see what happens if we merge a config that also
contains an "@merge_add" tag within it:

```yaml
--- # main.yaml
config_path1@merge_add: path1.yaml
--- # path1.yaml
param1: 1
config_path2@merge_add: path2.yaml
--- # path2.yaml
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

### Change processing list in processing (Still more advanced)

Note that the processing functions receive the list of processing objects as an
input and update as an attribute of the processing object. This means that it
is possible to manually modify this list in processing functions to change internal
variables, add or remove processing.

One simple example is creating a processing that triggers only once and adds a
list of processing to the processing list. This avoids the need to pass the entire
list in the make_config function.

```python
class AddProcessList(Processing):
    def __init__(self):
        super().__init__()
        self.process_list = [Process1(), Process2(), ...]
        self.already_added = False
        # Ensure that the processing trigger before all processing of the list:
        self.premerge_order = -100.0

    def premerge(self, flat_config: Config) -> Config:
        if not self.already_added:
            self.already_added = True
            # NOTE: the order of the process list has no importance
            flat_config.process_list += self.process_list
        return flat_config

config = make_config("main.yaml", process_list=[AddProcessList()])
```

This way you can then even create named spaces of processing to organize them.
The processing list is dynamic, use it as you want for more advanced use cases as
long as you know what you are doing!
