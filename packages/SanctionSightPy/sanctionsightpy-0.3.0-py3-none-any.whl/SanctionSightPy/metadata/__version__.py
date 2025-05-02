"""
Module for retrieving the version of the 'datadock' package.

This module imports the `metadata` object from `datadock.utils._compact_` and uses it to get the version of the 'datadock' package.

Attributes:
    __version__ (str): The version of the 'datadock' package.

Usage:
    >>> from SanctionSightPy.metadata.__version__ import __version__
    >>> print(__version__)

"""

from SanctionSightPy.utility._compact_ import metadata


__version__ = metadata.version("SanctionSightPy")