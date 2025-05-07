"""KeeNum provides a baseclass for enumerations."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import MetaNum
from ..waitaminute import ReadOnlyError

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Never
  from worktoy.mcls import FunctionType as Func


def _root(func: Func) -> Func:
  """Decorator to mark a function as a root function."""
  setattr(func, '__is_root__', True)
  return func


class KeeNum(metaclass=MetaNum):
  """KeeNum provides a baseclass for enumerations."""

  __slots__ = ('name', 'value', 'index')

  @_root
  def __init__(self, name: str, value: Any, index: int) -> None:
    """Initialize the KeeNum instance."""
    self.name = name
    self.value = value
    self.index = index

  @_root
  def __bool__(self, ) -> bool:
    """Return True if the value is not 0."""
    return False if self is type(self).NULL else True

  @_root
  def __str__(self, ) -> str:
    """Return the string representation of the KeeNum instance."""
    clsName = type(self).__name__
    return """%s.%s""" % (clsName, self.name.upper(),)

  @_root
  def __repr__(self, ) -> str:
    """Return the string representation of the KeeNum instance."""
    return """%s(%s, %s)""" % (type(self).__name__, self.name, self.value,)

  @_root
  def __eq__(self, other: object) -> bool:
    """Return True if the value is equal to the other value."""
    if not isinstance(other, KeeNum):
      return True if self.value == other else False
    return True if self is other else False

  @_root
  def __get__(self, instance: object, owner: type) -> KeeNum:
    """Return the KeeNum instance."""
    return self

  @_root
  def __set__(self, instance: object, value: object) -> Never:
    """Set the KeeNum instance."""
    raise ReadOnlyError(instance, self, value)

  @_root
  def __delete__(self, instance: object) -> Never:
    """Delete the KeeNum instance."""
    raise ReadOnlyError(instance, self, None)
