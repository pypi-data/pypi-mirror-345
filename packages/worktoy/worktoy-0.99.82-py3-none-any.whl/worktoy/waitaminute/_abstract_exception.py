"""AbstractException provides an abstract baseclass for custom exceptions
in the 'worktoy.waitaminute' module."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import logging
from abc import abstractmethod

from worktoy.parse import maybe
from worktoy.waitaminute import _Attribute

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Optional, Self


class AbstractException(Exception):
  """AbstractException provides an abstract baseclass for custom exceptions
  in the 'worktoy.waitaminute' module."""

  __class_attributes__ = None

  @classmethod
  def _getAttributes(cls) -> dict[str, _Attribute]:
    """Get the attributes of the class."""
    return maybe(cls.__class_attributes__, dict())

  def _resolveOther(self, other: Any) -> Self:
    """Resolve the other object to the same type as self."""
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
    """Compare the AbstractException object with another object."""
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    cls = type(self)
