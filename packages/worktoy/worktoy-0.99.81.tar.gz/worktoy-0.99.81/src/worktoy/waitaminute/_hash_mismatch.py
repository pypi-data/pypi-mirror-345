"""HashMismatch is raised by the dispatcher system to indicate a hash
based mismatch between a type signature and a tuple of arguments. """
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
  from worktoy.static import TypeSig

  from typing import Self


class HashMismatch(Exception):
  """HashMismatch is raised by the dispatcher system to indicate a hash
  based mismatch between a type signature and a tuple of arguments. """

  typeSig = _Attribute()
  posArgs = _Attribute()

  def __init__(self, typeSig: TypeSig, *args) -> None:
    """HashMismatch is raised by the dispatcher system to indicate a hash
    based mismatch between a type signature and a tuple of arguments. """

    self.typeSig = typeSig
    self.posArgs = args

    sigStr = str(typeSig)
    argTypes = [type(arg).__name__ for arg in args]
    argStr = """(%s)""" % ', '.join(argTypes)
    sigHash = hash(typeSig)
    if isinstance(args, list):
      argHash = hash((*args,))
    argHash = hash(args)

    infoSpec = """Unable to match type signature: <br><tab>%s<br>with
    signature of arguments:<br><tab>%s<br>Received hashes: %d != %d"""
    info = infoSpec % (sigStr, argStr, sigHash, argHash)
    Exception.__init__(self, info)

  def _resolveOther(self, other: object) -> Self:
    """Resolve the other object."""
    cls = type(self)
    if isinstance(other, cls):
      return other
    if isinstance(other, TypeSig):
      return cls(other, *self.posArgs)
    if isinstance(other, (tuple, list)):
      try:
        return cls(*other)
      except TypeError:
        return NotImplemented
    return NotImplemented

  def __eq__(self, other: object) -> bool:
    """Check if two HashMismatch objects are equal."""
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    if self.typeSig != other.typeSig:
      return False
    if self.posArgs != other.posArgs:
      return False
    return True
