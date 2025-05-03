"""DeletedAttributeException is raised to indicate that an attribute
was previously deleted with a call to __delete__ but is now attempted to
be accessed. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import _Attribute
from ..text import joinWords, monoSpace

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Self, Any

  from ..attr import AbstractBox


class DeletedAttributeException(AttributeError):
  """DeletedAttributeException is raised to indicate that an attribute
  was previously deleted with a call to __delete__ but is now attempted to
  be accessed. """

  desc = _Attribute()
  instance = _Attribute()

  def __init__(self, desc: AbstractBox, instance: Any) -> None:
    """Initialize the DeletedAttributeException object."""
    self.desc = desc
    self.instance = instance
    fieldName = getattr(desc, '__field_name__', None)
    owner = type(instance)
    ownerName = owner.__name__
    clsName = type(desc).__name__
    infoSpec = """Tried accessing deleted attribute at: '%s.%s: %s' from 
    instance: '%s', but the attribute was already deleted!"""
    info = infoSpec % (ownerName, fieldName, clsName, repr(instance))
    AttributeError.__init__(self, monoSpace(info))

  def _resolveOther(self, other: Any) -> Self:
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
    """Compare the DeletedAttributeException object with another object."""
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    cls = type(self)
    if isinstance(other, cls):
      if self.desc != other.desc:
        return False
      if self.instance != other.instance:
        return False
      return True
    return False
