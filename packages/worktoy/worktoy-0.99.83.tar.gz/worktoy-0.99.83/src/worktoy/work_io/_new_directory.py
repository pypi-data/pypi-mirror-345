"""The 'newDirectory' function creates a new directory at the specified
path. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os

from worktoy.text import monoSpace

from worktoy.waitaminute import PathSyntaxException

from . import validateAvailablePath

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Optional, Union, Self, Callable, TypeAlias


def newDirectory(path: str) -> str:
  """
  Creates a new directory at the specified path.

  Args:
    path (str): The path where the new directory will be created.

  Returns:
    str: The path of the newly created directory.

  Raises:
    FileExistsError: If the directory already exists.
    NotADirectoryError: If the path is not a directory.
    PathSyntaxException: If the path is not absolute.
  """
  validateAvailablePath(path)
  os.makedirs(path, exist_ok=True)
  return os.path.normpath(path)
