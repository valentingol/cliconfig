"""CLI Config: build your configuration from CLI by merging with processing.

Copyright (C) 2023  Valentin Goldité

    This program is free software: you can redistribute it and/or modify
    it under the terms of the MIT License.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    This project is free to use for COMMERCIAL USE, MODIFICATION,
    DISTRIBUTION and PRIVATE USE as long as the original license is
    include as well as this copy right notice.
"""
# pylint: disable=wrong-import-position
from cliconfig._version import __version__, __version_tuple__
from cliconfig.build_config import make_config
from cliconfig.cli_parser import parse_cli
from cliconfig.dict_routines import (
    clean_pre_flat,
    flatten,
    load_dict,
    merge_flat,
    merge_flat_paths,
    save_dict,
    show_dict,
    unflatten,
)
from cliconfig.process_routines import (
    load_processing,
    merge_flat_paths_processing,
    merge_flat_processing,
    save_processing,
)

__all__ = [
    "__version__",
    "__version_tuple__",
    "clean_pre_flat",
    "flatten",
    "load_dict",
    "load_processing",
    "make_config",
    "merge_flat",
    "merge_flat_paths",
    "merge_flat_paths_processing",
    "merge_flat_processing",
    "parse_cli",
    "save_dict",
    "save_processing",
    "show_dict",
    "unflatten",
]
