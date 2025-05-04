"""EZData leverages the 'worktoy' library to provide a dataclass."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..mcls import FunctionType
from . import EZMeta

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False


def _root(callMeMaybe: FunctionType) -> FunctionType:
  """Root decorator for the EZData class."""
  setattr(callMeMaybe, '_root', True)
  return callMeMaybe


class EZData(metaclass=EZMeta):
  """EZData is a dataclass that provides a simple way to define data
  structures with validation and serialization capabilities. """

  if TYPE_CHECKING:
    def __iter__(self): pass

    def __next__(self): pass

    def __init__(self, *args, **kwargs): pass

    def __getitem__(self, key): pass

    def __setitem__(self, key, value): pass
