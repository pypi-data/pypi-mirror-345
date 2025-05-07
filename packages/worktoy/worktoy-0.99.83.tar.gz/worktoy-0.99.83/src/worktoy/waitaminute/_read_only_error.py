"""ReadOnlyError is raised when an attempt is made to modify a read-only
attribute. This is a subclass of TypeError and should be used to indicate
that the attribute is read-only. """
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


class _ReadOnlyError(TypeError):
  """ReadOnlyError is raised when an attempt is made to modify a read-only
  attribute. This is a subclass of TypeError and should be used to indicate
  that the attribute is read-only. """

  def __init__(self, instance: object, desc: object, value: object) -> None:
    fieldName = getattr(desc, '__field_name__', None)
    if fieldName is None:
      TypeError.__init__(self, "Cannot modify read-only attribute.")
    else:
      owner = type(instance)
      ownerName = getattr(owner, '__name__', )
      cls = type(desc)
      clsName = getattr(cls, '__name__', )
      descName = '%s.%s' % (ownerName, fieldName)
      valueStr = repr(value)
      info = """Attempted to set value of read-only attribute: '%s' of 
      descriptor class: '%s' to: '%s'!""" % (descName, clsName, valueStr)
      TypeError.__init__(self, info)


class ReadOnlyError(TypeError):
  """ReadOnlyError is raised when an attempt is made to modify a read-only
  attribute. This is a subclass of TypeError and should be used to indicate
  that the attribute is read-only. """

  owningInstance = _Attribute()
  descriptorObject = _Attribute()
  existingValue = _Attribute()
  newValue = _Attribute()

  def __init__(self, instance: Any, desc: Any, *values) -> None:
    """Initialize the ReadOnlyError."""
    self.owningInstance = instance
    self.descriptorObject = desc
    self.existingValue, self.newValue = [*values, None, None][:2]
    header = """Attempted to overwrite read-only attribute '%s.%s'"""
    if self.existingValue is not None:
      valStr = """%s having value: '%s'""" % (header, self.existingValue)
      if self.newValue is not None:
        valStr = """%s with new value: '%s'""" % (valStr, self.newValue)
    else:
      valStr = header
    TypeError.__init__(self, valStr)

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
    """Compare the ReadOnlyError object with another object."""
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    cls = type(self)
    if isinstance(other, cls):
      if self.owningInstance != other.owningInstance:
        return False
      if self.descriptorObject != other.descriptorObject:
        return False
      if self.existingValue != other.existingValue:
        return False
      if self.newValue != other.newValue:
        return False
      return True
    return False
