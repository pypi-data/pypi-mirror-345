#!/usr/bin/env python3
from __future__ import annotations

import sys

if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources
datapath = resources.files("module_qc_tools") / "data"

__all__ = ("datapath",)
