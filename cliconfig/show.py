"""Functions to show the configurations."""
from typing import Any, Dict


def show_config(config: Dict[str, Any]) -> None:
    """Show the configurations.

    Parameters
    ----------
    config : Dict[str, Any]
        The configuration to show.
    """
    def pretty_print(config: Dict[str, Any], indent: int = 1) -> None:
        """Pretty print the configuration recursively."""
        for key, value in config.items():
            print(f"{'    ' * indent}{key}: ", end='')
            if isinstance(value, dict):
                print()
                pretty_print(value, indent + 1)
            elif isinstance(value, str):
                print(f"\'{value}\'")
            else:
                print(value)
    print('Config:')
    # printer.pprint(config)
    pretty_print(config)
