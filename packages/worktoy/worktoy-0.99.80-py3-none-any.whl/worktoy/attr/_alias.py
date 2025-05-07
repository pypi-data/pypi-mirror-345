"""Alias allows a subclass to set an alias for a given attribute inherited
from the parent class. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import Field
from ..mcls import BaseObject
from ..static import overload
from ..text import monoSpace

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any


class Alias(BaseObject):
  """Alias allows a subclass to set an alias for a given attribute inherited
  from the parent class. """

  __field_name__ = None  # new name
  __field_owner__ = None
  __attribute_name__ = None  # original name
  __parent_class__ = None  # original class

  def _getParentDesc(self, ) -> Field:
    """Get the parent descriptor."""
    parent = self.__parent_class__
    origName = self.__attribute_name__
    desc = getattr(parent, origName)
    return desc

  def __set_name__(self, owner: type, name: str) -> None:
    self.__field_owner__ = owner
    self.__field_name__ = name

  def __get__(self, instance: object, owner: type) -> Any:
    """Get the value of the attribute."""
    desc = self._getParentDesc()
    if instance is None:
      return desc
    return desc.__get__(instance, owner)

  def __set__(self, instance: object, value: Any) -> None:
    """Set the value of the attribute."""
    desc = self._getParentDesc()
    return desc.__set__(instance, value)

  def __delete__(self, instance: object) -> None:
    """Delete the value of the attribute."""
    desc = self._getParentDesc()
    return desc.__delete__(instance)

  def __str__(self) -> str:
    """Return the string representation of the Alias object."""
    parentName = self.__parent_class__.__name__
    fieldName = self.__field_name__
    origName = self.__attribute_name__
    ownerName = self.__field_owner__.__name__
    infoSpec = """Alias[new: %s.%s -> old: %s.%s]"""
    return infoSpec % (ownerName, fieldName, parentName, origName)

  def __repr__(self) -> str:
    """Return the string representation of the Alias object."""
    parentName = self.__parent_class__.__name__
    fieldName = self.__field_name__
    origName = self.__attribute_name__
    ownerName = self.__field_owner__.__name__
    infoSpec = """%s.%s = Alias(%s, %s)"""
    return infoSpec % (ownerName, fieldName, parentName, origName)

  @overload(type, str)
  def __init__(self, parent: type, name: str) -> None:
    """Initialize the Alias object."""
    self.__parent_class__ = parent
    self.__attribute_name__ = name

  @overload(str, str)
  def __init__(self, parent: str, name: str) -> None:
    """Initialize the Alias object."""
    cls = type(self)
    for parent in cls.__mro__:
      if parent.__name__ == parent:
        self.__parent_class__ = parent
        self.__attribute_name__ = name
        break
      if parent.__name__ == name:
        self.__parent_class__ = name
        self.__attribute_name__ = parent
        break
    else:
      e = """'%s.__init__' missing required argument: 'parent'!"""
      raise TypeError(monoSpace(e % cls.__name__))
