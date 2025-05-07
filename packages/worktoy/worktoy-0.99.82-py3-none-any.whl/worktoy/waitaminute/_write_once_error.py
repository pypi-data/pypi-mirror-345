"""WriteOnceError is a custom error class raised to indicate that a
variable was attempted to be written to more than once."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..text import monoSpace

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Self


class WriteOnceError(Exception):
  """WriteOnceError is a custom error class raised to indicate that a
  variable was attempted to be written to more than once."""

  __var_name__ = None
  __old_value__ = None
  __new_value__ = None

  def __init__(self, name: str, oldVal: Any, newVal: Any) -> None:
    """Initialize the WriteOnceError with a name, old value and new value."""
    self.__var_name__ = name
    self.__old_value__ = oldVal
    self.__new_value__ = newVal

    infoSpec = """Attempted to overwrite variable '%s' having value '%s' to 
    new value '%s'"""
    info = infoSpec % (name, str(oldVal), str(newVal))
    Exception.__init__(self, monoSpace(info))
