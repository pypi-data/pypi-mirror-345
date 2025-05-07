"""UnrecognizedMember is raised when a KeeNum class is unabled to
recognize a given identifier."""
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
  from ..keenum import MetaNum
  from typing import Any


class UnrecognizedMember(Exception):
  """UnrecognizedMember is raised when a KeeNum class is unable to
  recognize a given identifier."""

  keenumCls = _Attribute()
  unrecognizedIdentifier = _Attribute()

  def __init__(self, cls: MetaNum, identifier: Any) -> None:
    """Initialize the UnrecognizedMember object."""
    self.keenumCls = cls
    self.unrecognizedIdentifier = identifier
    infoSpec = """KeeNum class '%s' could not recognize identifier '%s'!"""
    info = infoSpec % (cls.__name__, identifier)
    Exception.__init__(self, monoSpace(info))

  def _resolveOther(self, other: Any) -> UnrecognizedMember:
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
    """Compare the UnrecognizedMember object with another object."""
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    cls = type(self)
    if isinstance(other, cls):
      if self.keenumCls != other.keenumCls:
        return False
      if self.unrecognizedIdentifier != other.unrecognizedIdentifier:
        return False
      return True
    return False
