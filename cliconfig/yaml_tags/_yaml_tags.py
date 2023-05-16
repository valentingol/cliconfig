"""Module to convert yaml tags in yaml file to python dict with  cliconfig tags."""

from typing import Any, Dict, Optional, Tuple

import yaml


class TaggedNode:
    """Node class for tagged tree (with yaml tags)."""

    def __init__(self, value: Any, tag: str, *, is_config: bool) -> None:
        self.tag = tag
        self.value = value
        self.is_config = is_config


def tagged_constructor(
    loader: yaml.SafeLoader, tag_suffix: str, node: yaml.Node
) -> Any:
    """Build a tagged tree node from yaml node."""
    if isinstance(node, yaml.ScalarNode):
        return TaggedNode(loader.construct_scalar(node), tag_suffix, is_config=False)
    if isinstance(node, yaml.SequenceNode):
        return TaggedNode(loader.construct_sequence(node), tag_suffix, is_config=False)
    return TaggedNode(
        loader.construct_mapping(node), tag_suffix, is_config=True  # type: ignore
    )


def get_yaml_loader() -> Any:
    """Return a yaml loader to parse tags and build tagged tree."""
    loader = yaml.SafeLoader
    loader.add_multi_constructor("", tagged_constructor)  # type: ignore
    return loader


def insert_tags(tagged_tree: Any) -> Tuple[Any, Optional[str]]:
    """Build dict with cliconfig tag from tagged tree (with yaml tags)."""
    if isinstance(tagged_tree, TaggedNode) and tagged_tree.is_config:
        tag = tagged_tree.tag
        if tag:
            tag = tag.replace("!", "")
        out_dict = build_tree_from_dict(tagged_tree.value)
        return out_dict, tag
    if isinstance(tagged_tree, dict):
        out_dict = build_tree_from_dict(tagged_tree)
        return out_dict, None
    if isinstance(tagged_tree, TaggedNode):
        tag = tagged_tree.tag
        if tag:
            tag = tag.replace("!", "")
        if isinstance(tagged_tree.value, str):
            value = yaml.safe_load(tagged_tree.value)
        else:
            value = tagged_tree.value
        return value, tag
    return tagged_tree, None


def build_tree_from_dict(in_dict: Dict) -> Dict[str, Any]:
    """Build a dict with cliconfig tag from a dict of tagged trees."""
    out_dict: Dict[str, Any] = {}
    for key, value in in_dict.items():
        tree, tag = insert_tags(value)
        if tag:
            subtag = tag.replace("!", "")
            key = f"{key}@{subtag}"
        out_dict[key] = tree
    return out_dict
