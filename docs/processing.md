# Processing

Processing are powerful tools to modify the config at each steps of the life of a
configuration. More precisely, you can use processing to modify the full configuration
before and after each merge, after loading and before saving the config.

The processing are applied with a processing class that herits from
`cliconfig.processing.Processing`. They implement premerge, postmerge, postload and
presave methods. Each function have the signature:

```python
def premerge(self, flat_dict: Dict[str, Any], processing_list: List[Processing]) -> Dict[str, Any]:
    ...
```

They takes a flat dict as input (a dict of depth 1 with dot-separated keys), the list
of processing (not always needed but useful for more advanced processing,
it is discussed in an advanced section below) and return the modified flat dict
(and keep it flat). You can write your own processing objects and add them to the
`processing_list` argument of `make_config` function to apply it automatically.
You will see how they work and how to create them in this section.

## Why a flat dict?

The idea is that is that when we build a config, we manipulate dict with both nested
sub-dicts and flat keys in the same time.To simplify this, the dicts are flatten
systematically before a merge. It make things mre simple and prevent from duplicated
key in a same configuration like:

```python
config = {'a': {'b': 1}, 'a.b': 2}
```

More generally ALL config modifications are done with flat dicts during config building
and so it is the case fot the processing too.

Of course, after building your config, it will be unflattened to a normal nested config.

## Processing order

The order of the processing to trigger is actually important because they modify
the config and so the behavior of the the next processing. That is why
the Processing classes have 4 float attributes that are the order of the 4 processing
methods (premerge, postmerge, postload and presave).

An example to illustrate the importance of the order:

```yaml
--- # config.yaml
param1@type:int@copy: 'param2'
param2@type:int: 1
```

Here, we decide to force the type of the parameters. The `param1` is also the copy
of `param2` and naturally have the same type.

On pre-merge, the processing will remove the tags and get the information of the
forced types and the copy. Then, we make a merge (considering to simplify that none of
our params are modified at this point), the the post-merge processing will be applied.

What happen if the type processing triggers before copy processing? It will check the
value, that is `"param2"` and raise an error because it is not an int. However, if
the copy processing trigger before the type processing, it will copy the value of
`param2` to `param1` (so `1`) and then the type processing not raises an error.

Fortunately, the post-merge orders are `20.0` for the type processing and `10.0` for
the copy processing so the copy triggers first. Take care of the order when you
create your own processing!

## Create basic processing

### Pre-merge processing to pass a single value to a function and eventually modify it

The pre-merge processing is kindly the most useful processing because it allows
to modify the input config written bu the user to create the resulting python dict that
store the config of your experiment. It is like the interface between the user config
and the final config.

To do so, you need sometimes to modify the parameters for which the key follows a
pattern (i.e contains a tag or a particular prefix or suffix) depending on the
current value.

To do so, we provide the function `cliconfig.create_processing_value` to create such a
processing quickly. It takes a regex or a tag name (in the latter case, the tag is
removed after processing), the function to apply on the value to modify it
and eventually the order of the processing. Finally, it takes a `persistent` bool
parameter that indicates if encountering the tag (if you have a tag) once will trigger
the process on all the following keys with the same name even if the tag is absent.

The function return a Processing class that can be directly used in your list
of processing.

For instance:

```python
proc = create_processing_value(lambda x: str(x), tag='convert_str', persistent=True)
config, _ = make_config(default_config, processing_list=[proc])
```

Now, parameters like `{"subconfig.param@convert_str": 1}` will be converted to:
`{"subconfig.param": "1"}` and the keys `"subconfig.param"` will be converted
to string forever before every merge.

Note that you can also use function that make side effect without changing the value
(to check if a condition is met for instance).

## Create your processing classes

To create your own processing classes and unlock more possibilities, you simply need to
overload the methods of the `Processing` class to modify the config on the timings
you want. To do so, you often need to manipulate tags.

### Manipulate the tags

Tags are useful to trigger a processing as we have seen. However, we need to take care
because tagging a key modify its name and can make conflicts when you use several
in a same key. That is why we provide tags routines to manipulate the tags safely,
available in `cliconfig.tag_routines`. There are:

* `clean_tag` that remove a tag (with the exact name in input) from a key
* `clean_all_tags` that remove all tags from a key. It is convenient to store the
  actual key name to process it later.
* `clean_dict_tags` that remove all tags from a dict and return the cleaned dict and
  the list of keys containing tags.

With these tools, we can write for instance a processing that look for a tag "@keep"
and that restore the value of a parameter after the merge if it was updated.

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
```

If you not reset `self.keep_vals`, the internal state of the processing will be
kept and you are able to protect a key forever if it is tagged with
"@keep" once (in default config for instance). This can be an useful processing!

**Note: Always clean the tag after (or before) using it! If some tags are still present
after all pre-merge operations, it will trigger a security processing that raise
an error (for security reasons).**

### Manage the list of processing to create complex processing (Advanced)

The key concept is that the elementary operations on the config are not actually
merge, save and load but actually:

* apply premerge processing on two configs, merge the two configs then apply
  postmerge processing to the output
* apply presave processing then save a config
* load a config then apply postload processing

Theses three operations are `cliconfig.merge_processing`, `cliconfig.save_processing`
and `cliconfig.load_processing` and they naturally take the list of processing as
input and return the modified list of processing (to keep the internal values
of the processing).

Now the trick is that sometimes we want to apply these operations on processing
themselves, particularly when we want to modify a part of the configuration instead
of only one parameter (typically by merging two configurations). That is why we sometimes
need the list of processing in input of the processing.

An example with the tag "@merge_add", a processing that is triggered
before merging and that merge the config loaded from a path (the value)
to the current config. We want to see what happens if we merge a config that
has also a "@merge_add" tag in it.

```yaml
--- # main.yaml
config_path1@merge_add: path1.yaml
--- # path1.yaml
param1: 1
config_path2@merge_add: path2.yaml
--- # path2.yaml
param2: 2
```

Now, considering that we want to merge the config `main.yaml` with another config.
The pre-merge processing will be applied and find the tag `@merge_add`.
It will remove the tag, merge the config found at `path1.yaml` to the config `main.yaml`.
But it is not a simple merge, it is a merge *with processing*!
So before merging `path1.yaml`, it will trigger the pre-merge processing on the config,
find the key `config_path2@merge_add` and merge the config `path2.yaml` to `path1.yaml`.
Then, it will merge `path1.yaml` to `main.yaml`. Finally, the configuration `main.yaml`
is interpreted as:

```python
{'param1': 1, 'param2': 2, 'config_path1': 'path1.yaml', 'config_path2': 'path2.yaml'}
```

before being merged itself with another config. Note that is not only a processing that allows
to organize the configuration on multiple files. In fact, it also allows you to choose a
particular configuration among several ones by setting the path as value of the tagged
key.

**Important:**
To create a processing that merge, save or load a config, it is also necessary to
update the list of processing after and before each operation to be sure that you use
the good internal states of the processing. To pass the list of processing to other
processing, simply make and update a `processing_list` attribute
in your processing class. You have an example in `processing.builtin.ProcessMerge`.

### Change processing list in processing (Still more advanced)

Note that as the processing functions get the list of processing object at input
and update it in attribute, it also possible to modify manually this list to
change internal variables, add or remove processing. This allows you to make more
complex things but this may have unwanted behavior if you do not know exactly what
you are doing.

A simple example of use is to make a processing that trigger only once and that adds
a list of processing to the processing list to avoid passing the full list in
`make_config`:

```python
class AddProcessList(Processing):
    def __init__(self):
        super().__init__()
        self.processing_list = self.processing_list.extend(
            [processing1, processing2, processing3, ...]
        )

make_config("main.yaml", processing_list=[AddProcess()])
```

You can then create named spaces of processing to organize them.
