# Manipulate configs

You are encouraged to use the routines provided by `cliconfig` to manipulate configs
and even create your own config builder to replace `make_config`. You can use:

- `merge_config` and `merge_config_file` to merge your configs
- `parse_cli` to parse CLI arguments on config files and additional parameters
- `flat_config` and `unflat_config` to flatten and unflatten your configs
- `clean_pre_flat` to clean conflicting keys before flattening

You can also save, load and display configs with `save_config`,
`load_config` and `show_config` functions.

Note that theses functions are aimed to be use with configs but can be used with
any python dict.

See the API documentation for more details on routines.
