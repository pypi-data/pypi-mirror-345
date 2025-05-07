"""VariableNotNone should be raised when a variable is unexpectedly not
None."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..text import monoSpace

from . import _Attribute

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Optional, Self


class VariableNotNone(Exception):
  """VariableNotNone should be raised when a variable is unexpectedly not
  None."""

  varName = _Attribute(None)

  def __init__(self, variableName: str = None) -> None:
    """Initialize the VariableNotNone object."""
    if variableName is None:
      Exception.__init__(self, 'Expected variable to be None')
    else:
      self.varName = variableName
      infoSpec = """Expected variable '%s' to be None"""
      Exception.__init__(self, monoSpace(infoSpec % variableName))
