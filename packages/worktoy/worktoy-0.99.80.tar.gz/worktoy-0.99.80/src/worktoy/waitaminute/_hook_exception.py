"""HookException is raised from the AbstractNamespace class to wrap
exceptions raised by __getitem__ hooks. This is necessary to avoid
confusion with the expected KeyError exception in the metacall system."""
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
  from worktoy.mcls import AbstractNamespace
  from worktoy.mcls.hooks import AbstractHook

  from typing import Any, Callable, TypeAlias, Self


class HookException(Exception):
  """
  This custom exception allows get item hooks to interrupt calls to
  __getitem__. Because the metacall system requires the __getitem__ to
  specifically raise a KeyError in certain situations, an exception raised
  by a hook might be confused for the KeyError. Instead,
  the AbstractNamespace class will catch exceptions raised by hooks and
  raise them from this exception:
  For example:

  try:
    hook(self, key, val)
  except Exception as exception:
    raise HookException(exception) from exception
  """

  initialException = _Attribute()
  namespaceObject = _Attribute()
  itemKey = _Attribute()
  errorValue = _Attribute()
  hookFunction = _Attribute()

  def __init__(
      self,
      exception: Exception,
      namespace: AbstractNamespace,
      key: str,
      val: object,
      hook: AbstractHook,
  ) -> None:
    self.initialException = exception
    self.namespaceObject = namespace
    self.itemKey = key
    self.errorValue = val
    self.hookFunction = hook
    Exception.__init__(self, str(exception))

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
    """Compare the exception to another object."""
    cls = type(self)
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    if isinstance(other, cls):
      if self.initialException != other.initialException:
        return False
      if self.namespaceObject != other.namespaceObject:
        return False
      if self.itemKey != other.itemKey:
        return False
      if self.errorValue != other.errorValue:
        return False
      if self.hookFunction != other.hookFunction:
        return False
      return True
    return False
