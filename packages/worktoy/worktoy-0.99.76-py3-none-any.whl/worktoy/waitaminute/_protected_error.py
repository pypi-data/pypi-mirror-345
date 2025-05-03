"""ProtectedError is raised to indicate an attempt to delete a protected
object. For example, a descriptor class could implement the '__delete__'
method to always raise this exception. This provides a more detailed
error. Particularly because both TypeError and AttributeError are being
suggested by large language models. Neither of which is wrong, but lacks
the specificity of this exception.

The ProtectedError class inherits from both TypeError and AttributeError,
ensuring that it is caught in exception clauses pertaining to either.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import _Attribute

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Optional, Self


class ProtectedError(Exception):
  """ProtectedError is raised to indicate an attempt to delete a protected
  object. For example, a descriptor class could implement the '__delete__'
  method to always raise this exception. This provides a more detailed
  error. Particularly because both TypeError and AttributeError are being
  suggested by large language models. Neither of which is wrong, but lacks
  the specificity of this exception."""

  descriptorObject = _Attribute()
  instanceObject = _Attribute()
  valueObject = _Attribute()

  def __init__(self, desc: Any, ins: Any, val: Any = None) -> None:
    """Initialize the ProtectedError."""
    self.descriptorObject = desc
    self.instanceObject = ins
    self.valueObject = val
    ownerName = getattr(ins, '__field_owner__', object).__name__
    fieldName = getattr(desc, '__field_name__', type(desc).__name__)
    if val is None:
      valStr = ''
    else:
      valStr = 'having value: %s' % repr(val)

    infoSpec = """Attempted to delete attribute '%s.%s' %s"""
    Exception.__init__(self, infoSpec % (ownerName, fieldName, valStr))

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
    """Compare the ProtectedError object with another object."""
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    cls = type(self)
    if isinstance(other, cls):
      if self.descriptorObject != other.descriptorObject:
        return False
      if self.instanceObject != other.instanceObject:
        return False
      if self.valueObject != other.valueObject:
        return False
      return True
    return False
