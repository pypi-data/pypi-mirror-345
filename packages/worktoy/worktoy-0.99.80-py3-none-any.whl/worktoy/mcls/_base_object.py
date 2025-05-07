"""BaseObject exposes the functionality of the custom metaclass
implementations in the 'worktoy' library. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import BaseMeta

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False


class BaseObject(metaclass=BaseMeta):
  """BaseObject exposes the functionality of the custom metaclass
  implementations in the 'worktoy' library. """

  def __init__(self, *args, **kwargs) -> None:
    """Why are we still here?"""

  def __init_subclass__(cls, *args, **kwargs) -> None:
    """Just to suffer?"""
