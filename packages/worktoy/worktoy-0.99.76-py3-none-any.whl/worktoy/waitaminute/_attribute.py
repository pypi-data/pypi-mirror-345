"""_Attribute provides a primitive descriptor protocol implementation. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import re

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  pass


class _Meta(type):
  """Metaclass simplifying the __str__ of classes. """

  def __str__(cls, ) -> str:
    """
    Return a string representation of the class.
    """
    clsName = cls.__name__
    metaName = type(cls).__name__
    infoSpec = """%s(metaclass=%s)""" % (clsName, metaName,)
    return infoSpec

  def __repr__(cls, ) -> str:
    """
    Return a string representation of the class.
    """
    clsName = cls.__name__
    metaName = type(cls).__name__
    baseNames = [base.__name__ for base in cls.__bases__]
    baseStr = ', '.join(baseNames)
    nameSpace = ['%s=%s' % (k, v) for k, v in cls.__dict__.items()]
    nameStr = ', '.join(nameSpace)
    infoSpec = """%s('%s', (%s), dict(%s)"""
    return infoSpec % (clsName, metaName, baseStr, nameStr,)


class _Attribute(metaclass=_Meta):
  """_Attribute provides a primitive descriptor protocol implementation.
  This is a base class for all attributes. It provides the basic
  functionality
  for getting and setting values, as well as the ability to define custom
  behavior for getting and setting values.
  """

  __field_name__ = None
  __field_owner__ = None

  __private_name__ = None
  __default_value__ = None

  def __set_name__(self, owner: type, name: str) -> None:
    """Set the name of the attribute."""
    self.__field_name__ = name
    self.__field_owner__ = owner

  def _getPrivateName(self) -> str:
    """Get the private name of the attribute."""
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return '__%s__' % pattern.sub('_', self.__field_name__).lower()

  def __init__(self, *args) -> None:
    """Initialize the attribute with a default value."""
    if args:
      if len(args) == 1:
        self.__default_value__ = args[0]
      else:
        self.__default_value__ = (*args,)

  def __get__(self, instance: object, owner: type) -> object:
    """Get the value of the attribute."""
    if instance is None:
      return self
    privateName = self._getPrivateName()
    return getattr(instance, privateName, self.__default_value__)

  def __set__(self, instance: object, value: object) -> None:
    """Set the value of the attribute."""
    privateName = self._getPrivateName()
    setattr(instance, privateName, value)

  def __delete__(self, instance: object) -> None:
    """Delete the value of the attribute."""
    privateName = self._getPrivateName()
    delattr(instance, privateName)

  def __str__(self, ) -> str:
    """
    Return a string representation of the attribute.
    """
    ownerName = self.__field_owner__.__name__
    fieldName = self.__field_name__
    clsName = type(self).__name__
    infoSpec = """%s(%s, %s)""" % (clsName, ownerName, fieldName,)
    return infoSpec

  def __repr__(self, ) -> str:
    """
    Return a string representation of the attribute.
    """
    ownerName = self.__field_owner__.__name__
    fieldName = self.__field_name__
    clsName = type(self).__name__
    infoSpec = """%s = %s(%s)"""
    if self.__default_value__ is None:
      defaultStr = ''
    defaultStr = repr(self.__default_value__)
    return infoSpec % (fieldName, clsName, defaultStr,)
