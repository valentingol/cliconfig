# Processing

Processings are powerful tools to modify the config at each step of the lifecycle of
a configuration. More precisely, you can use processings to modify the full
configuration before and after each merge, after loading, and before saving the config.

The processing are applied with a processing class that herits from
`cliconfig.processing.Processing`. They implement `premerge`, `postmerge`, `postload`
and `presave` methods. Each function have the signature:

```python
def premerge(self, flat_dict: Dict[str, Any], processing_list: List[Processing]) -> Dict[str, Any]:
    ...
```

They take a flat dict as input (a dict of depth 1 with dot-separated keys), the list
of processings (not always needed but useful for more advanced processing, as
discussed in an advanced section below), and return the modified flat dict (while
keeping it flat). You can write your own processing objects and add them to the
`processing_list` argument of the `make_config` function to apply them automatically.
In this section, you will learn how they work and how to create them.

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
during config construction, and the same applies to processings.

However, it's important to note that after building your config,
it will be unflattened to its normal nested configuration structure.

## Processing order

The order in which the processings are triggered is crucial because they modify
the config and consequently affect the behavior of subsequent processings.
To manage this order, the Processing classes have four float attributes representing
the order of the four processing methods: premerge, postmerge, postload, and presave.

Here's an example to illustrate the significance of the order:

```yaml
--- # config.yaml
param1@type:int@copy: 'param2'
param2@type:int: 1
```

In this example, we want to enforce the types of the parameters. Additionally, `param1`
is intended to be a copy of `param2` and naturally should have the same type.

During the pre-merge processing, the tags are removed, and information about the
enforced types and the copy operation is gathered. Then, a merge is performed (assuming
no modifications to our parameters at this point), followed by the post-merge processing.

Now, what happens if the type processing triggers before the copy processing? It will
check the value, which is `"param2"`, and raise an error because it is not an integer.
However, if the copy processing triggers before the type processing, it will copy the
value of `param2` (which is `1`) to `param1`, and then the type processing will not
encounter an error.

Fortunately, the post-merge orders are set as follows: `20.0` for the type processing
and `10.0` for the copy processing. As a result, the copy processing triggers first.
Therefore, it is crucial to carefully manage the order when creating your own processings.

Ensure you pay attention to the order of your processings to achieve the desired behavior.

## Create basic processing

### Pre-merge processing to pass a single value to a function and eventually modify it

The pre-merge processing is particularly useful as it allows you to modify the input
config provided by the user and create the resulting Python dictionary that stores the
configuration for your experiment. It serves as the interface between the user config
and the final config.

In a lot of cases, you may need to modify parameters based on certain patterns in their
keys, such as the presence of a specific tag, prefix, or suffix, depending on
their current values.

To simplify this process, we provide the `cliconfig.create_processing_value` function.
This function allows you to quickly create a processing that matches a regular
expression or a specific tag name (in which case the tag is removed after processing).
You can specify the function to be applied on the value to modify it, and optionally,
the order of the processing. Additionally, there is a persistent parameter, which is
a boolean value indicating whether encountering the tag (if a tag is used) once will
trigger the processing on all subsequent keys with the same name, even if the tag is
absent.

The create_processing_value function returns a Processing class that can be directly
used in your list of processings.

Here's an example to illustrate:

```python
proc = create_processing_value(lambda x: str(x), tag='convert_str', persistent=True)
config, _ = make_config(default_config, processing_list=[proc])
```

In this example, parameters with keys like `{"subconfig.param@convert_str": 1}` will
be converted to `{"subconfig.param": "1"}`. Moreover, the keys `"subconfig.param"`
 will be permanently converted to strings before every merge.

It's worth noting that you can also use functions that have side effects without
necessarily changing the value itself. For example, you can use a function to
check if a certain condition is met.

## Create your processing classes

To create your own processing classes and unlock more possibilities, you simply
need to overload the methods of the Processing class to modify the config at the
desired timings. To do so, you often need to manipulate tags.

### Manipulate the tags

Tags are useful for triggering a processing, as we have seen. However, we need
to be cautious because tagging a key modifies its name and can lead to conflicts
when using multiple tags within the same key. To address this issue, we provide
tag routines in `cliconfig.tag_routines`. These routines include:

* `clean_tag`: Removes a specific tag (based on its exact name) from a key.
* `clean_all_tags`: Removes all tags from a key. This is helpful for storing the
  actual key name to process it later.
* `clean_dict_tags`: Removes all tags from a dictionary and returns the cleaned
  dict along with a list of keys that contained tags.

With these tools, we can write a processing, for example, that searches for the
tag `"@keep"` and restores the value of a parameter after the merge if it was updated.

```python
class ProcessKeep(Processing):
    """Prevent a value from being changed after the merge."""

    def __init__(self) -> None:
        super().__init__()
        self.keep_vals: Dict[str, Any] = {}

    # NOTE: processing_list will not be used here
    def premerge(self, flat_dict: Dict[str, Any], processing_list: list) -> Dict[str, Any]:
        """Pre-merge processing."""
        # Browse a freeze version of the dict
        items = list(flat_dict.items())
        for flat_key, value in items:
            end_key = flat_key.split(".")[-1]  # parameter name
            if "@keep" in end_key:
                # Remove the tag and update the dict
                new_key = clean_tag(flat_key, "keep")
                del flat_dict[flat_key]
                flat_dict[new_key] = value
                # Store the value
                clean_key = clean_all_tags(key)  # remove all tags = true parameter name
                self.keep_vals[clean_key] = value
        return flat_dict

    def postmerge(self, flat_dict: Dict[str, Any], processing_list: list) -> Dict[str, Any]:
        """Post-merge processing."""
        # Restore the values and print a warning if they were modified
        for key, value in self.keep_vals.items():
            # (`if key in flat_dict:` is important: the dicts seen by the processing
            # not necessarily contains all the same keys)
            if key in flat_dict:
                if flat_dict[key] != value:
                    print(f"WARNING: protected key {key} was modified by the merge")
                flat_dict[key] = value
        self.keep_vals = {}  # reset the values
        return flat_dict


# Use it:
config, _ = make_config("main.yaml", processing_list=[ProcessKeep()])
```

If you don't reset `self.keep_vals`, the internal state of the processing will
be retained, allowing you to protect a key indefinitely if it has been tagged with
`"@keep"` before (for example, in the default config). This can be a useful processing!

Note: Always remember to clean the tag after (or before) using it! If any tags
remain present after all pre-merge operations, it will trigger a security processing
that raises an error (for security reasons).

### Manage the list of processings to create complex processing (Advanced)

The key concept is that the elementary operations on the config are not actually
limited to merge, save, and load, but rather:

* Applying premerge processing, merging and postmerge processing to the output.
* Applying presave processing and then saving a config.
* Loading a config and then applying postload processing.

These three operations are in `cliconfig.process_routines` and called
`merge_processing`, `save_processing`, and `load_processing`, respectively. They take
the list of processing as input and return the modified list of processing to
maintain the internal values of the processing.

Now, the trick is that sometimes we want to apply these operations to the processing
themselves, particularly when we want to modify a part of the configuration instead
of just a single parameter (such as merging two configurations). This is why we
sometimes need the list of processing as input for the processing.

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
allows to organize the configuration on multiple files. In fact, it also allows you to
choose a particular configuration among several ones by setting the path as value of
the tagged key.

**Important:**
To create a processing that performs merging, saving, or loading of a config, it is
necessary to update the list of processing before and after each operation. This
ensures that the correct internal states of the processing are used. In order to pass
the list of processing to other processing classes, you can create and update a
processing_list attribute within your processing class. An example of this can be
found in the `processing.builtin.ProcessMerge` class.

### Change processing list in processing (Still more advanced)

Note that the processing functions receive the list of processing objects as an
input and update as an attribute of the processing object. This means that it
is possible to manually modify this list in processing functions to change internal
variables, add or remove processing. While this flexibility allows for more complex
operations, it can lead to unintended behavior if not done carefully.

One simple example is creating a processing that triggers only once and adds a
list of processing to the processing list. This avoids the need to pass the entire
list in the make_config function.

```python
class AddProcessList(Processing):
    def __init__(self):
        super().__init__()
        self.processing_list = self.processing_list.extend(
            [processing1, processing2, processing3, ...]
        )

config, _ = make_config("main.yaml", processing_list=[AddProcess()])
```

This way you can then create named spaces of processing to organize them.
