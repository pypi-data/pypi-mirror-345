"""
Module: _compact_.py
---------------------------------
Module for handling metadata import based on Python version.

This module ensures compatibility with different Python versions by conditionally importing the `metadata` module from `importlib`.

Attributes:
    metadata (module): The imported `metadata` module, either from `importlib.metadata` or `importlib`.

Usage:
    >>> from SanctionSightPy.utility._compact_ import metadata
    >>> version = metadata.version('your_package_name')

Compatibility:
    - Python 3.8 and above: Uses `importlib.metadata`.
    - Below Python 3.8: Uses `importlib_metadata` backport.

"""

from __future__ import annotations
import sys


if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib.metadata as metadata


__all__ = ["metadata"]