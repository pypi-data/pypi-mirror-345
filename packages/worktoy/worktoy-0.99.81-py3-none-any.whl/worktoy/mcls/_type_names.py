"""This files provides common type names used by the mcls package. """
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from worktoy.mcls import AbstractNamespace

  Space = AbstractNamespace
  Spaces = tuple[AbstractNamespace, ...]
  Base = tuple[type, ...]
  Types = tuple[type, ...]

else:
  Space = object
  Spaces = tuple
  Base = tuple
  Types = tuple


def func() -> None:
  pass


FunctionType = type(func)
