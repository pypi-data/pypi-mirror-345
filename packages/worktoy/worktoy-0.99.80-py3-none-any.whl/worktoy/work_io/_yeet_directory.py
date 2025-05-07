"""The 'yeetDirectory' function removes a directory with all contents.
Effectively the same as: 'rm -rf <directory>'."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os

from ..text import monoSpace

from ..waitaminute import PathSyntaxException

from . import validateExistingDirectory

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Optional, Union, Self, Callable, TypeAlias


def yeetDirectory(dirPath: str, **kwargs) -> None:
  """
  Removes a directory with all contents. Effectively the same as: 'rm -rf
  <directory>'.

  Args:
    dirPath (str): The path to the directory to remove.

  Returns:
    str: The path of the removed directory.

  Raises:
    FileNotFoundError: If the directory does not exist.
    NotADirectoryError: If the path is not a directory.
    PathSyntaxException: If the path is not absolute.
  """
  try:
    validateExistingDirectory(dirPath)
  except FileNotFoundError as fileNotFoundError:
    if kwargs.get('strict', True):
      raise fileNotFoundError
  except NotADirectoryError as notADirectoryError:
    infoSpec = """The path received by 'yeetDirectory': '%s' is not a 
    directory!"""
    info = monoSpace(infoSpec % dirPath)
    raise NotADirectoryError(info) from notADirectoryError
  else:
    for root, dirs, files in os.walk(dirPath, topdown=False):
      for name in files:
        os.remove(os.path.join(root, name))
      for name in dirs:
        os.rmdir(os.path.join(root, name))
    os.rmdir(dirPath)
  finally:
    if os.path.exists(dirPath):
      infoSpec = """The directory '%s' was not removed!"""
      info = monoSpace(infoSpec % dirPath)
      raise OSError(info)
