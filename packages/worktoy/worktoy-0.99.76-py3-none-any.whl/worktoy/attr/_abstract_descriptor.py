"""AbstractDescriptor provides a common abstract baseclass for all
descriptor classes. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from abc import abstractmethod

from ..waitaminute import MissingVariable

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any


class _MetaDescriptor(type):
  """MetaDescriptor is a metaclass for the AbstractDescriptor class."""

  def __getitem__(cls, fieldType: type) -> Any:
    """Get the field type."""
    self = cls()
    self._setFieldType(fieldType)
    return self


class AbstractDescriptor(metaclass=_MetaDescriptor):
  """AbstractDescriptor provides a common abstract baseclass for all
  descriptor classes. """

  __field_name__ = None
  __field_owner__ = None

  def __set_name__(self, owner: type, name: str) -> None:
    """Set the name of the field and the owner of the field."""
    self.__field_name__ = name
    self.__field_owner__ = owner

  def __get__(self, instance: object, owner: type) -> object:
    """Get the value of the descriptor."""
    if instance is None:
      return self
    return self._instanceGet(instance)

  def __set__(self, instance: object, value: object) -> None:
    """Set the value of the descriptor."""
    self._instanceSet(instance, value)

  def __delete__(self, instance: object) -> None:
    """Delete the value of the descriptor."""
    self._instanceDelete(instance)

  def getFieldName(self, ) -> str:
    """Getter-function for the field name."""
    if self.__field_name__ is None:
      raise MissingVariable('__field_name__', str)
    return self.__field_name__

  def getFieldOwner(self) -> type:
    """Getter-function for the field owner."""
    if self.__field_owner__ is None:
      raise MissingVariable('__field_owner__', type)
    return self.__field_owner__

  @abstractmethod
  def _instanceGet(self, instance: object, **kwargs) -> object:
    """Get the instance of the descriptor."""

  @abstractmethod
  def _instanceSet(self, instance: object, value: object, **kwargs) -> None:
    """Set the instance of the descriptor."""

  @abstractmethod
  def _instanceDelete(self, instance: object, **kwargs) -> None:
    """Delete the instance of the descriptor."""
