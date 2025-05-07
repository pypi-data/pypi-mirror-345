"""The 'maybe' function returns the first received argument that is not
None. Thus it provides a None-aware filter. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

try:
  from typing import TYPE_CHECKING
except ImportError:
  TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any


def maybe(*args: Any) -> Any:
  """The 'maybe' function returns the first received argument that is not
  None. Thus, it provides a None-aware filter.

  Args:
      *args: The arguments to filter.

  Returns:
      The first argument that is not None.
  """
  for arg in args:
    if arg is not None:
      return arg


def maybeType(type_: type, *args) -> Any:
  """The 'maybeType' function returns the first received argument that is not
  None and is of the specified type. Thus, it provides a None-aware filter
  with type checking.

  Args:
      type_: The type to check against.
      *args: The arguments to filter.

  Returns:
      The first argument that is not None and is of the specified type.
  """
  for arg in args:
    if isinstance(arg, type_):
      return arg


def maybeTypes(type_: type, *args) -> Any:
  """The 'maybeTypes' function returns the first received argument that is
  not
  None and is of the specified type. Thus, it provides a None-aware filter
  with type checking.

  Args:
      type_: The type to check against.
      *args: The arguments to filter.

  Returns:
      The first argument that is not None and is of the specified type.
  """
  typeArgs = []
  for arg in args:
    if isinstance(arg, type_):
      typeArgs.append(arg)
  return (*typeArgs,)
