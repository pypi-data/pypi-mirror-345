"""QuestionableSyntax is raised when a name is encountered that is likely
a typo, such as '__set_item__' instead of '__setitem__' or '__setname__'
instead of '__set_name__'.
This is a"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import _Attribute
from ..text import monoSpace

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Callable, Self


class QuestionableSyntax(SyntaxError):
  """QuestionableSyntax is raised when a name is encountered that is likely
  a typo, such as '__set_item__' instead of '__setitem__' or '__setname__'
  instead of '__set_name__'.
  This is a subclass of SyntaxError and should be used to indicate that
  the code is likely to be incorrect. """

  derpName = _Attribute()
  realName = _Attribute()

  def __init__(self, derpName: str, realName: str) -> None:
    self.__derp_name__ = derpName
    self.__real_name__ = realName
    info = """Received name: '%s' which is similar enough to '%s' to be a 
    likely typo. """
    SyntaxError.__init__(self, monoSpace(info % (derpName, realName)))

  def _resolveOther(self, other: object) -> Any:
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
    """Compare the QuestionableSyntax object with another object."""
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    cls = type(self)
    if isinstance(other, cls):
      if self.derpName != other.derpName:
        return False
      if self.realName != other.realName:
        return False
      return True
    return False
