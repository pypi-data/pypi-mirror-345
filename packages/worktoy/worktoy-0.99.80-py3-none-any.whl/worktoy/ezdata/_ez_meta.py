"""EZMeta provides the metaclass for the EZData class."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..mcls import AbstractMetaclass, Base
from ..ezdata import EZSpace

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any


class _WhenReady:
  """WhenReady is a decorator that is used to mark a method as ready
  for use. """

  name = None
  bases = None
  space = None
  kwargs = None

  __wrapped__ = None

  def __init__(self, bases: tuple, **kwargs) -> None:
    """Initialize the WhenReady object."""
    self.bases = bases
    self.kwargs = kwargs

  def __set_name__(self, owner: type, name: str) -> None:
    self.name = name
    self.owner = owner
    space = EZSpace(EZMeta, name, self.bases, )
    for key, val in self.kwargs.items():
      space[key] = val
    space['__name__'] = name
    self.__wrapped__ = EZMeta(self.name, self.bases, space)

  def __get__(self, instance: object, owner: type) -> EZMeta:
    """Get the WhenReady object."""
    return self.__wrapped__


class EZMeta(AbstractMetaclass):
  """EZMeta provides the metaclass for the EZData class."""

  @classmethod
  def __prepare__(mcls, name: str, bases: Base, **kwargs: dict) -> EZSpace:
    """Prepare the class namespace."""
    return EZSpace(mcls, name, bases, **kwargs)

  def __call__(cls, *args: tuple, **kwargs: dict) -> Any:
    """Call the class."""
    if cls.__name__ == 'EZData':
      return _WhenReady((cls,), **kwargs)
    return AbstractMetaclass.__call__(cls, *args, **kwargs)
