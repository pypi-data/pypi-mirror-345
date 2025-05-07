"""DispatchException provides a custom exception raised when an instance
of OverloadDispatcher fails to resolve the correct function from the
given arguments. Because the overload protocol relies on type matching,
this exception subclasses TypeError such that it can be caught by external
error handlers. """
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
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
  from worktoy.static import Dispatch

  from typing import Self


class DispatchException(TypeError):
  """DispatchException provides a custom exception raised when an instance
  of OverloadDispatcher fails to resolve the correct function from the
  given arguments. Because the overload protocol relies on type matching,
  this exception subclasses TypeError such that it can be caught by external
  error handlers. """

  dispatchObject = _Attribute()
  receivedArguments = _Attribute()
  receivedTypes = _Attribute()

  def __init__(self, dispatch: Dispatch, *args) -> None:
    self.dispatchObject = dispatch
    self.receivedArguments = args
    self.receivedTypes = [type(arg) for arg in args]

    ownerName = dispatch.getFieldOwner().__name__
    fieldName = dispatch.getFieldName()
    clsName = type(dispatch).__name__
    header = '%s object at %s.%s' % (clsName, ownerName, fieldName)
    typeArgs = [type(arg).__name__ for arg in args]
    argStr = '%s' % ', '.join(typeArgs)
    typeSigs = dispatch.getTypeSigs()
    typeSigStr = [str(sig) for sig in typeSigs]
    sigStr = '<br><tab>'.join(typeSigStr)

    infoSpec = """%s received arguments with signature: <br><tab>%s
    <br>which does not match any of the expected signatures:<br><tab>%s"""
    info = infoSpec % (header, argStr, sigStr)
    TypeError.__init__(self, info)

  def _resolveOther(self, other: object) -> Self:
    """Resolve the other object."""
    cls = type(self)
    if isinstance(other, cls):
      return other
    if isinstance(other, (list, tuple)):
      try:
        return cls(*other)
      except TypeError:
        return NotImplemented
    return NotImplemented

  def __eq__(self, other: object) -> bool:
    """Check if two DispatchExceptions are equal."""
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    if self is other:
      return True
    if self.dispatchObject != other.dispatchObject:
      return False
    if self.receivedArguments != other.receivedArguments:
      return False
    if self.receivedTypes != other.receivedTypes:
      return False
    return True
