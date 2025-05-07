from __future__ import annotations

import sys

from yarrtist._version import __version__

if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources
data = resources.files("yarrtist") / "data"

__all__ = ("__version__", "data")
