# Manipulate configs

To merge configs, you can use `cliconfig.merge_config` function.
It supports unflatten (or nested) dicts like `{'a': {'b': 1, 'c': 2}}`,
flatten dicts like `{'a.b': 1, 'a.c': 2}`, and a mix of both. The dicts will be flatten
before merging. Sometimes you can have conflicts in flatten operation for instance with
`{'a.b': 1, 'a': {'b': 2}}` that have two different values for `a.b`. That's why you
can use a `priority` parameter to choose which value to keep before merging.

You can also save, load and display configs with `cliconfig.save_config`,
`cliconfig.load_config` and `cliconfig.show_config` functions.

## How to contribute

For **development**, install the package dynamically and dev requirements with:

```bash
pip install -e .
pip install -r requirements-dev.txt
```

Everyone can contribute to CLI Config, and we value everyone’s contributions.
Please see our
[contributing guidelines](https://github.com/valentingol/cliconfig/blob/main/CONTRIBUTING.md)
for more information 🤗
