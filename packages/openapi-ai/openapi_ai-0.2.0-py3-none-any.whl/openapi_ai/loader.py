"""
Loader for OpenAPI specifications and naming utilities.

This module provides functions to load an OpenAPI JSON specification from a URL or file path,
and to convert strings to snake_case naming convention.
"""
from __future__ import annotations

import json
import re

from pathlib import Path
from typing import Any, Dict

import requests

def load_spec(src: str | Path) -> Dict[str, Any]:
    """
    Loads an OpenAPI JSON specification from a given source.

    The source may be a URL, in which case the specification is loaded over HTTP.
    Alternatively, the source may be a file path, in which case the specification is loaded from the file.

    Args:
        src: The source to load the specification from.

    Returns:
        The loaded OpenAPI specification.
    """

    source = str(src)
    if not source.endswith("/"):
        source += "/"
    if not source.endswith("/openapi.json"):
        source += "openapi.json"

    if source.startswith('http'):
        response = requests.get(source, timeout=30)
        response.raise_for_status()
        return response.json()
    with open(source, 'r', encoding="utf-8") as f:
        return json.load(f)


def to_snake(name: str, remove_prefix: str = '') -> str:
    """
    Converts a given string to snake_case.

    Args:
        name (str): The input string to be converted.
        remove_prefix (str, optional): A prefix to remove from the input string if present.

    Returns:
        str: The converted snake_case string.
    """

    if remove_prefix and name.startswith(remove_prefix):
        name = name[len(remove_prefix):]

    name = name.strip('/')
    name = re.sub(r'\{[^}]*\}', '', name)
    s = re.sub(r'[^0-9a-zA-Z]+', '_', name)
    return s.strip('_').lower()
