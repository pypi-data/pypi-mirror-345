"""THIS is the token object indicating a class before it is created. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Never


class _MetaThis(type):
  """Metaclass ensuring the 'THIS' class never instantiates."""

  def __new__(mcls, *args, **kwargs) -> type:
    """Prevent instantiation of THIS class."""
    bases = (object,)
    name = "THIS"
    space = dict(__THIS__=True, )
    return type.__new__(mcls, name, bases, space)

  def __call__(cls, *args, **kwargs) -> Never:
    """Prevent instantiation of THIS class."""
    raise TypeError("THIS class cannot be instantiated.")

  def __str__(cls, ) -> str:
    """Return the string representation of THIS class."""
    info = """The '%s' class provides a placeholder for classes not yet 
    created. """
    return info % cls.__name__

  def __hash__(cls) -> int:
    """Return the hash of THIS class."""
    return 69420


class THIS(metaclass=_MetaThis):
  """THIS is the token object indicating a class before it is created. """
  pass
