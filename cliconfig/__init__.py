"""CLI Config.

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
from cliconfig.config import load_config, make_config, merge, save_config
from cliconfig.show import show_config

__all__ = [
    "__version__",
    "__version_tuple__",
    "load_config",
    "make_config",
    "merge",
    "save_config",
    "show_config",
]
