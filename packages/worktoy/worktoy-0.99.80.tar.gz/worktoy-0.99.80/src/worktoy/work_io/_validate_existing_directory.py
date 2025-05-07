"""The 'validateExistingDirectory' function validates that a given 'str'
object points to an existing directory. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os

from worktoy.text import monoSpace

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Optional, Union, Self, Callable, TypeAlias


def validateExistingDirectory(directory: str) -> str:
  """
  Validates that a given 'str' object points to an existing directory.

  Args:
    directory (str): The directory to validate.

  Returns:
    str: The validated directory.

  Raises:
    FileNotFoundError: If the directory does not exist.
    NotADirectoryError: If the path is not a directory.
  """
  if not os.path.exists(directory):
    infoSpec = """No directory exists at: '%s'!"""
    info = monoSpace(infoSpec % directory)
    raise FileNotFoundError(info)
  if not os.path.isdir(directory):
    infoSpec = """The path '%s' is not a directory!"""
    info = monoSpace(infoSpec % directory)
    raise NotADirectoryError(info)
  return os.path.normpath(directory)
