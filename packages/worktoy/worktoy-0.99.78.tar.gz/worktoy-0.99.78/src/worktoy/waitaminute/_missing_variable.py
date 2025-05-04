"""MissingVariable exception should be raised when a variable is missing
and requires initialization. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import _Attribute
from ..text import joinWords

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Self


class MissingVariable(Exception):
  """MissingVariable exception should be raised when a variable is missing
  and requires initialization. """

  varName = _Attribute()
  varType = _Attribute()

  def __init__(self, name: str, *types) -> None:
    """Initialize the MissingVariable object."""
    self.varName = name
    self.varType = types
    if not types:
      info = """Missing variable at name: '%s'!%s"""
      typeStr = ''
    elif len(types) == 1:
      info = """Missing variable '%s' of type '%s'"""
      typeStr = types[0].__name__
    else:
      info = """Missing variable '%s' of any of the following types: %s"""
      typeNames = [type_.__name__ for type_ in types]
      typeStr = joinWords(*typeNames, sep='or')
    Exception.__init__(self, info % (name, typeStr))

  def _resolveOther(self, other: object) -> Self:
    """Resolve the other object."""
    cls = type(self)
    if isinstance(other, cls):
      return other
    if isinstance(other, (tuple, list)):
      try:
        return cls(*other)
      except TypeError:
        return NotImplemented
    return NotImplemented

  def __eq__(self, other: object) -> bool:
    """Compare the MissingVariable object with another object."""
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    cls = type(self)
    if isinstance(other, cls):
      if self.varName != other.varName:
        return False
      if len(self.varType) != len(other.varType):
        return False
      for selfType, otherType in zip(self.varType, other.varType):
        if selfType != otherType:
          return False
      return True
    return False
