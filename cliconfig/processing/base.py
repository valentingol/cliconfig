"""Base class for processing."""
from cliconfig.base import Config


class Processing():
    """Processing base class."""

    def __init__(self) -> None:
        self.premerge_order = 0.0
        self.postmerge_order = 0.0
        self.presave_order = 0.0
        self.postload_order = 0.0

    def premerge(self, flat_config: Config) -> Config:
        """Pre-merge processing.

        Function that can be applied to the flat config to modify it
        before merging . It takes a flat config and returns a flat config.
        """
        return flat_config

    def postmerge(self, flat_config: Config) -> Config:
        """Post-merge processing.

        Function that can be applied to the flat config to modify it
        after merging . It takes a flat config and returns a flat config.
        """
        return flat_config

    def presave(self, flat_config: Config) -> Config:
        """Pre-save processing.

        Function applied to the flat config to modify it before
        saving it. It takes a flat config and returns a flat config.
        """
        return flat_config

    def postload(self, flat_config: Config) -> Config:
        """Post-load processing.

        Function applied to the flat config to modify it after
        loading it. It takes a flat config and returns a flat config.
        """
        return flat_config

    def __eq__(self, __value: object) -> bool:
        """Equality operator.

        Two processing are equal if they are the same class and add the same
        attributes (get with __dict__).
        """
        equal = (
            isinstance(__value, self.__class__) and self.__dict__ == __value.__dict__
        )
        return equal
