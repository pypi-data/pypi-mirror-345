"""ReservedNames provides a list of reserved names that are set
automatically by the interpreter. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ...text import monoSpace
from ...waitaminute import ReadOnlyError

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Self, Any, Callable


class _Meta(type):
  """Metaclass for ReservedNames."""

  __iter_contents__ = None

  __reserved_names__ = [
      '__dict__',
      '__weakref__',
      '__module__',
      '__annotations__',
      '__match_args__',
      '__doc__',
      '__name__',
      '__qualname__',
      '__firstlineno__',
      '__static_attributes__',
  ]

  def __iter__(cls) -> Self:
    """Iterate over the reserved names."""
    cls.__iter_contents__ = [*cls.__reserved_names__, ]
    return cls

  def __next__(cls) -> str:
    """Get the next reserved name."""
    if cls.__iter_contents__:
      return cls.__iter_contents__.pop(0)
    raise StopIteration

  def __call__(cls, *args, **kwargs) -> Self:
    """Call the metaclass."""
    return cls

  def __get__(cls, instance: object, owner: type) -> Self:
    """Get the reserved names."""
    return cls

  def __set__(cls, instance: object, value: Any) -> None:
    """Set the reserved names."""
    raise ReadOnlyError(instance, cls, value)

  def __delete__(cls, instance: object) -> None:
    """Delete the reserved names."""
    raise ReadOnlyError(instance, cls, None)

  def __contains__(cls, name: str) -> bool:
    """Check if the name is in the reserved names."""
    return True if name in [i for i in cls] else False

  def __str__(cls, ) -> str:
    """Get the string representation of the metaclass."""
    info = 'ReservedNames:\n%s'
    names = '<br><tab>'.join([name for name in cls])
    return monoSpace(info % names)

  __repr__ = __str__


class ReservedNames(metaclass=_Meta):
  """ReservedNames provides a list of reserved names that are set
  automatically by the interpreter."""
  pass
