"""CLI Config: build your configuration from CLI by merging with processing.

Copyright © 2023  Valentin Goldité

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
from cliconfig.base import Config
from cliconfig.config_routines import load_config, make_config, save_config, show_config
from cliconfig.process_routines import (
    merge_flat_paths_processing,
    merge_flat_processing,
)
from cliconfig.processing.base import Processing
from cliconfig.processing.builtin import DefaultProcessings
from cliconfig.processing.create import (
    create_processing_keep_property,
    create_processing_value,
)

__all__ = [
    "__version__",
    "__version_tuple__",
    "Config",
    "DefaultProcessings",
    "Processing",
    "create_processing_keep_property",
    "create_processing_value",
    "make_config",
    "load_config",
    "merge_flat_paths_processing",
    "merge_flat_processing",
    "save_config",
    "show_config",
]
