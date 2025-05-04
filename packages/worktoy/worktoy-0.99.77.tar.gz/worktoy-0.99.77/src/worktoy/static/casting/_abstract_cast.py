"""Cast provides a flexible casting utility used by the overload system. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from abc import abstractmethod
from typing import Any


class AbstractCast:
  """Cast provides a flexible casting utility used by the overload
  system. """

  @abstractmethod
  def getTargetType(self, **kwargs) -> type:
    """Get the target type of the cast. Subclasses must implement this
    method to return the target type."""

  @abstractmethod
  def _cast(self, *args, **kwargs) -> Any:
    """Cast the arguments to the target type."""

  def __call__(self, *args, **kwargs) -> Any:
    """Calling the Cast object will cast the arguments to the target type."""
    if kwargs.get('_recursion', False):
      raise RecursionError
    return self._cast(*args, **kwargs, _recursion=True)
