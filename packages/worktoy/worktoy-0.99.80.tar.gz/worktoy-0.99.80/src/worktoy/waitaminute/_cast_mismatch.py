"""CastMismatch should be raised to indicate that the fast static
system of the TypeSig class did not match."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..text import monoSpace
from . import _Attribute

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Self, Any


class CastMismatch(TypeError):
  """CastMismatch should be raised to indicate that the fast static
  system of the TypeSig class did not match."""

  expType = _Attribute()
  actObj = _Attribute()
  actType = _Attribute()

  def __init__(self, type_: type, obj: object) -> None:
    """Initialize the CastMismatch object."""
    self.expType = type_
    self.actObj = obj
    self.actType = type(obj)
    typeName = type_.__name__
    objStr = str(obj)
    objType = type(obj).__name__
    infoSpec = """Unable to cast object: '%s' of type '%s' to type '%s'!"""
    info = monoSpace(infoSpec % (objStr, objType, typeName))
    TypeError.__init__(self, info)

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
    if isinstance(other, dict):
      type_ = other.get('__expected_type__', None)
      obj = other.get('__actual_object__', None)
      if type_ is not None and obj is not None:
        if isinstance(type_, type):
          return cls(type_, obj)
    return NotImplemented

  def __eq__(self, other: object) -> bool:
    """Check if the exception is equal to another object."""
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    if self.expType != other.expType:
      return False
    if self.actObj != other.actObj:
      return False
    if self.actType != other.actType:
      return False
    return True
