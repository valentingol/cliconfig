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
from cliconfig._version import __version__, __version_tuple__
from cliconfig.build_config import load_config, make_config
from cliconfig.cli_parser import parse_cli
from cliconfig.process_routines import (
    merge_flat_paths_processing,
    merge_flat_processing,
    save_processing,
)
from cliconfig.processing.create import create_processing_value

__all__ = [
    "__version__",
    "__version_tuple__",
    "make_config",
    "parse_cli",
    "load_config",
    "merge_flat_paths_processing",
    "merge_flat_processing",
    "save_processing",
    "create_processing_value",
]
