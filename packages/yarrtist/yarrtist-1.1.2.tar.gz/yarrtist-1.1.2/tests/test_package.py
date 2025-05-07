from __future__ import annotations

import importlib.metadata

import yarrtist as m


def test_version():
    assert importlib.metadata.version("yarrtist") == m.__version__
