# Copyright (c) 2023 Valentin Goldite. All Rights Reserved.
"""Base class for processing.

Used to make configuration object and run the routines in `cliconfig.process_routines`
and `cliconfig.config_routines`.
"""
from cliconfig.base import Config


class Processing:
    """Processing base class.

    Each processing classes contains pre-merge, post-merge, pre-save
    and post-load processing. They are used with routines that apply
    processing in `cliconfig.process_routines` and
    `cliconfig.config_routines`.

    That are applied in the order defined
    by the order attribute in case of multiple processing.
    """

    def __init__(self) -> None:
        self.premerge_order = 0.0
        self.postmerge_order = 0.0
        self.endbuild_order = 0.0
        self.presave_order = 0.0
        self.postload_order = 0.0

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing.

        Function applied to the flat config to modify it
        before merging. It takes a flat config and returns a flat config.
        """
        return flat_config

    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing.

        Function applied to the flat config to modify it
        after merging . It takes a flat config and returns a flat config.
        """
        return flat_config

    def endbuild(self, flat_config: Config) -> Config:
        """End-build processing.

        Function applied to the flat config to modify it at the end of
        a building process (typically `cliconfig.config_routines.make_config`
        or `cliconfig.config_routines.load_config`).
        It takes a flat config and returns a flat config.
        """
        return flat_config

    def presave(self, flat_config: Config) -> Config:
        """Pre-save processing.

        Function applied to the flat config to modify it before
        saving. It takes a flat config and returns a flat config.
        """
        return flat_config

    def postload(self, flat_config: Config) -> Config:
        """Post-load processing.

        Function applied to the flat config to modify it after
        loading. It takes a flat config and returns a flat config.
        """
        return flat_config

    def __repr__(self) -> str:
        """Representation of Processing object."""
        return f"{self.__class__.__name__}"

    def __eq__(self, __value: object) -> bool:
        """Equality operator.

        Two processing are equal if they are the same class and add the same
        attributes (accessed with `__dict__`).
        """
        equal = (
            isinstance(__value, self.__class__) and self.__dict__ == __value.__dict__
        )
        return equal
