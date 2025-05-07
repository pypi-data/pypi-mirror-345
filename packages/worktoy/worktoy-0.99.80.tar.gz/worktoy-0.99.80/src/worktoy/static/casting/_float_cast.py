"""FloatCast converts from str, int, bool and complex to float."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ...waitaminute import CastMismatch
from . import AbstractCast

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Callable


class FloatCast(AbstractCast):
  """FloatCast converts from str, int, bool and complex to float."""

  def getTargetType(self, **kwargs) -> type:
    """Get the target type of the cast. Subclasses must implement this
    method to return the target type."""
    return float

  def _cast(self, *args, **kwargs) -> float:
    """Cast the arguments to the target type."""
    if len(args) - 1:
      e = """%s expects exactly one argument, but received %d: \n%s"""
      clsName = type(self).__name__
      nArgs = len(args)
      fmt = lambda arg: '  %s of type: %s' % (str(arg), type(arg).__name__)
      listArgs = '\n'.join([fmt(arg) for arg in args])
      raise TypeError(e % (clsName, nArgs, listArgs))
    arg = args[0]
    if isinstance(arg, float):
      return arg
    if isinstance(arg, bool):
      return 1.0 if arg else 0.0
    if isinstance(arg, int):
      return float(arg)
    if isinstance(arg, complex):
      if arg.imag:
        raise CastMismatch(float, arg)
      return float(arg.real)
    try:
      return float(arg)
    except Exception as exception:
      raise CastMismatch(float, arg) from exception

  def __get__(self, instance: object, owner: type) -> Callable:
    """Get the FloatCast object."""
    return self
