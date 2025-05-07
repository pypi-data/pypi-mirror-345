"""Cast creates an AbstractCast subclass object appropriate to a given
type. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import Any

from . import AbstractCast, AutoCast, IntCast
from . import FloatCast, ComplexCast

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  pass


class Cast(AbstractCast):
  """Cast creates an AbstractCast subclass object appropriate to a given
  type. """

  def getTargetType(self, **kwargs) -> type:
    """This subclass should not be used directly. """
    e = """This subclass should not be used directly. """
    raise RuntimeError(e)

  def _cast(self, *args, **kwargs) -> Any:
    """This subclass should not be used directly. """
    e = """This subclass should not be used directly. """
    raise RuntimeError(e)

  def __new__(cls, targetType: type) -> AbstractCast:
    """Create a new Cast object."""
    if targetType is int:
      return IntCast()
    if targetType is float:
      return FloatCast()
    if targetType is complex:
      return ComplexCast()
    return AutoCast(targetType)
