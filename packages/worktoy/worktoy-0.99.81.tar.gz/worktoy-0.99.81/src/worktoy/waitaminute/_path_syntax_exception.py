"""PathSyntaxException provides a custom exception raised to indicate that
a 'str' object is not a valid absolute path. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os

from worktoy.text import monoSpace

from . import _Attribute

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Optional, Union, Self, Callable, TypeAlias


class PathSyntaxException(ValueError):
  """
  PathSyntaxException provides a custom exception raised to indicate that
  a 'str' object is not a valid absolute path.
  """

  badPath = _Attribute()

  def __init__(self, path: str) -> None:
    """
    Initialize the PathSyntaxException with the invalid path.

    Args:
      path (str): The invalid path.
    """
    self.badPath = path
    infoSpec = """The path '%s' is not a valid, absolute path!"""
    info = monoSpace(infoSpec % path)
    ValueError.__init__(self, info)

  def _resolveOther(self, other: Any) -> Self:
    """
    Resolve the other object to a PathSyntaxException.

    Args:
      other (Any): The other object to resolve.

    Returns:
      Self: The resolved PathSyntaxException.
    """
    cls = type(self)
    if isinstance(other, cls):
      return other
    try:
      out = cls(other)
    except (TypeError, IndexError, ValueError):
      return NotImplemented
    else:
      return out
    finally:
      if TYPE_CHECKING:  # pycharm, please!
        pycharmPlease = 69420
        assert isinstance(pycharmPlease, cls)
        return pycharmPlease
      else:
        pass

  def __eq__(self, other: Any) -> bool:
    """
    Check if the PathSyntaxException is equal to another object.

    Args:
      other (Any): The other object to compare.

    Returns:
      bool: True if equal, False otherwise.
    """
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    if self.badPath != other.badPath:
      return False
    return True
