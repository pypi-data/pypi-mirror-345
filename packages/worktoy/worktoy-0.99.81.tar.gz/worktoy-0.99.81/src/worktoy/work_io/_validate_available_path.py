"""The 'validateExistingFile' function validates that a given 'str' object
is a valid file or directory path that does not already exist. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os

from worktoy.text import monoSpace

from worktoy.waitaminute import PathSyntaxException

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Optional, Union, Self, Callable, TypeAlias


def validateAvailablePath(path: str) -> str:
  """
  Validates that a given 'str' object is a valid file or directory path
  that does not already exist.

  Args:
    path (str): The path to validate.

  Returns:
    str: The validated path.

  Raises:
    FileExistsError: If the file or directory already exists.
    NotADirectoryError: If the path is not a directory.
  """
  if not os.path.isabs(path):
    raise PathSyntaxException(path)
  if os.path.exists(path):
    infoSpec = """The path '%s' already exists!"""
    info = monoSpace(infoSpec % path)
    raise FileExistsError(info)
  return os.path.normpath(path)
