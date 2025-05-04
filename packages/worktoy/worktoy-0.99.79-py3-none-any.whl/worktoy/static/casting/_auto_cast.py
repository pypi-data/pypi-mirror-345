"""AutoCast subclasses AbstractCast and provides a general casting utility
for arbitrary types. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import AbstractCast

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any


class AutoCast(AbstractCast):
  """AutoCast subclasses AbstractCast and provides a general casting
  utility for arbitrary types. """

  __target_type__ = None

  def getTargetType(self, **kwargs) -> type:
    """Get the target type of the cast. Subclasses must implement this
    method to return the target type."""
    return self.__target_type__

  def _setTargetType(self, targetType: type) -> None:
    """Set the target type of the cast. This method is used to set the
    target type of the cast."""
    self.__target_type__ = targetType

  def _cast(self, *args, **kwargs) -> Any:
    """Cast the arguments to the target type."""
    if kwargs.get('_recursion', False):
      raise RecursionError
    cls = self.getTargetType()
    return cls(*args, **kwargs, _recursion=True)

  def __init__(self, targetType: type) -> None:
    """Initialize the AutoCast object."""
    self._setTargetType(targetType)
