"""ReservedNameHook protects reserved names. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ...waitaminute import ReservedName
from . import AbstractHook, ReservedNames

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from worktoy.mcls import AbstractNamespace as ASpace


class ReservedNameHook(AbstractHook):
  """ReservedNameHook protects reserved names."""

  reservedNames = ReservedNames()

  def setItemHook(
      self,
      space: ASpace,
      key: str,
      value: object,
      oldValue: object
  ) -> bool:
    """The setItemHook method is called when an item is set in the
    namespace."""
    if key in self.reservedNames:
      if key not in space:
        dict.__setitem__(space, key, value)
        return True
      raise ReservedName(key)
    return False
