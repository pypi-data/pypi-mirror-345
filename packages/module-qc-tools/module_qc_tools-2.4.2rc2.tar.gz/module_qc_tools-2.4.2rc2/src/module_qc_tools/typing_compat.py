"""
Typing helpers.
"""

from __future__ import annotations

import sys

if sys.version_info >= (3, 9):
    from typing import Annotated

else:
    from typing_extensions import Annotated

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

__all__ = (
    "Annotated",
    "TypeAlias",
)
