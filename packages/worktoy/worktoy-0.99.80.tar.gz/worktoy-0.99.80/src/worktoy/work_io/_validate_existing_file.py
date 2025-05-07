"""The 'validateExistingFile' function validates the existence of a file. """
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


def validateExistingFile(file: str) -> str:
  """
  Validates that a given 'str' object points to an existing file.

  Args:
    file (str): The file to validate.

  Returns:
    str: The validated file.

  Raises:
    FileNotFoundError: If the file does not exist.
    IsADirectoryError: If the path is a directory.
  """
  if not os.path.exists(file):
    infoSpec = """No file exists at: '%s'!"""
    info = monoSpace(infoSpec % file)
    raise FileNotFoundError(info)
  if not os.path.isfile(file):
    infoSpec = """The path '%s' is not a file!"""
    info = monoSpace(infoSpec % file)
    raise IsADirectoryError(info)
  return os.path.normpath(file)
