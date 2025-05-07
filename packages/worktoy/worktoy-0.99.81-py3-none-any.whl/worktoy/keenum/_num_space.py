"""NumSpace provides the namespace class for the enumerations."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..mcls import AbstractNamespace
from ..parse import maybe
from . import NumHook

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from worktoy.keenum import NUM


class NumSpace(AbstractNamespace):
  """NumSpace provides the namespace class for the enumerations."""

  __member_nums__ = None

  def getMemberNums(self, ) -> list[NUM]:
    """Get the member nums of the enumeration."""
    return maybe(self.__member_nums__, [])

  def addNum(self, key: str, num: NUM) -> bool:
    """Add a num to the enumeration."""
    existing = self.getMemberNums()
    num.key = key
    self.__member_nums__ = [*existing, num]
    return True

  numHook = NumHook()
