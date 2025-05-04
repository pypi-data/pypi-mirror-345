"""ResolveException should be raised by classes that try to resolve
'other' objects in custom implementation of certain dunder methods. """
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
  from typing import Self, Any


class ResolveException(Exception):
  """ResolveException should be raised by classes that try to resolve
  'other' objects in custom implementation of certain dunder methods. """

  selfCls = _Attribute()
  otherObj = _Attribute()

  def __init__(self, self_: Any, other: Any) -> None:
    """Initialize the ResolveException object."""
    self.selfCls = type(self_)
    self.otherObj = other
    clsName = self.selfCls.__name__
    otherStr = repr(other)
    info = """Unable to resolve '%s' as an object of type: '%s'"""
    Exception.__init__(self, info % (otherStr, clsName))
