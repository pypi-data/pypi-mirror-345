"""
The 'worktoy.parse' module provides the None-aware 'maybe' function
along with some related functions. The 'maybe' function implements the
only redeeming feature of javascript:

#  Javascript
const maybe = (value, fallback) => {
  return value ?? fallback;
}
console.log(maybe(null, 69, 420)); // 42
#  Python
maybe(None, 69, 420) # 42

Besides the 'maybe' function, the module also provides the 'maybeType'
and 'maybeTypes' functions. These functions add type filtering to the
maybe function.

maybeType(targetType: type, *args: Any) -> Any
maybeTypes(targetType: type, *args: Any) -> tuple[Any, ...]
The 'maybeType' function takes a target type and any number of arguments
and returns the first of the target type. The 'maybeTypes' function
returns all arguments matching the target type in a tuple.

For example:
>>> maybe(None, 0, 69, None)  # Returns 0, the first non-None value
>>> maybeType(int, None, 0, 69, None)  # Returns 0, the first int
>>> maybeTypes(int, None, 0, 69, None)  # Returns (0, 69), all ints
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._maybe import maybe, maybeType, maybeTypes

__all__ = [
    'maybe',
    'maybeType',
    'maybeTypes',
]
