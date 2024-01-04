# Copyright © 2023  Valentin Goldité
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the MIT License.
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#    This project is free to use for COMMERCIAL USE, MODIFICATION,
#    DISTRIBUTION and PRIVATE USE as long as the original license is
#    include as well as this copy right notice.
"""
.. include:: ../DOCUMENTATION.md

## License

Copyright © 2023 Valentin Goldité

This program is free software: you can redistribute it and/or modify it
under the terms of the `MIT License <LICENSE>`__. This program is
distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.

The project is free to use for COMMERCIAL USE, MODIFICATION,
DISTRIBUTION and PRIVATE USE as long as the original license is included
as well as this copy right notice at the top of the modified files.
"""

from cliconfig._version import __version__, __version_tuple__
from cliconfig.base import Config
from cliconfig.config_routines import (
    flatten_config,
    load_config,
    make_config,
    save_config,
    show_config,
    unflatten_config,
    update_config,
)
from cliconfig.dict_routines import flatten as flatten_dict
from cliconfig.dict_routines import unflatten as unflatten_dict
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
    "flatten_config",
    "flatten_dict",
    "make_config",
    "load_config",
    "merge_flat_paths_processing",
    "merge_flat_processing",
    "save_config",
    "show_config",
    "unflatten_config",
    "unflatten_dict",
    "update_config",
]
