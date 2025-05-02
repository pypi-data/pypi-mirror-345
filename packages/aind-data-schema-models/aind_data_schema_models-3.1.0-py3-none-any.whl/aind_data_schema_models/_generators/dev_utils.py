"""Dev utilities for constructing models from CSV files"""

import re


def to_class_name_underscored(name: str) -> str:
    """Convert a name to a class name by capitalizing and removing non-alphanumeric characters.

    Always prefixes the string with an underscore."""
    name = str(name)
    return "_" + re.sub(r"\W+", "_", name.title()).replace(" ", "")


def to_class_name(name: str) -> str:
    """Convert a name to a valid class name by capitalizing and removing non-alphanumeric characters.

    Replace any non alphanumeric characters at the beginning of the string with a single _."""
    name = str(name)
    return re.sub(r"\W|^(?=\d)", "_", name.title()).replace(" ", "")
