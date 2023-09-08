# Processing

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
whatever you want with the config (we hope!).

## Why a flat dict?

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

## Processing order

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
* if it checkss a property on a value: 15 < order < 25
* if it deletes other key(s) but you want to trigger the tags before: 25 < order < 35
* final check/modification after all processings: order > 35

Note: a pre-merge order should not be greater than 1000, the order of the default
processing `ProcessCheckTags` that raise an error if tags still exist at the end
of the pre-merge step.

## Create basic processing

### Processing that modify a single value

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

### Pre-merge/post-merge processing that protect a property from being modified

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
create_processing_keep_property(type, regex=".*", premerge_order=15.0,
                                postmerge_order=15.0, endbuild_order=15.0)
```

A processing that protect parameters tagged with @protect from being changed:

```python
create_processing_keep_property(lambda x: x, tag_name="protect",
                                premerge_order=15.0, postmerge_order=15.0,
                                endbuild_order=15.0)
```

Each time you choose the order `15.0` because it is a good value for processing that
made checks on the values. Indeed, processings that change the values such as
`ProcessCopy` have an order that is generally $\leq$ 10.0.

It is also possible to pass the flat config as a second argument to the function
similarly to `create_processing_value`.

## Create your processing classes (Advanced)

To create your own processing classes and unlock more possibilities, you simply
need to overload the methods of the Processing class to modify the config at the
desired timings. To do so, you often need to manipulate tags.

### Manipulate the tags

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

### Merge, save or load configs in processing

The key concept is that as long as we deal with processings, the elementary operations
on the config are not actually to merge, save, and load a config, but rather:

* Applying pre-merge processing, then merging, then applying post-merge processing.
* Applying pres-ave processing and then saving a config.
* Loading a config and then applying post-load processing.

These three operations are in `cliconfig.process_routines` and called
`merge_processing`, `save_processing`, and `load_processing`, respectively. They
take as input a Config object that contains as we see the list of processing.

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

### Change processing list in processing (Still more advanced)

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
