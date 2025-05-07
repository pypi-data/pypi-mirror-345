"""DataField represents an entry in the EZData classes. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False


class DataField:
  """DataField represents an entry in the EZData classes. """
  __slots__ = ('key', 'type_', 'val')

  def __init__(self, key: str, type_: type, val: object) -> None:
    """Initialize the DataField object."""
    self.key = key
    self.type_ = type_
    self.val = val
