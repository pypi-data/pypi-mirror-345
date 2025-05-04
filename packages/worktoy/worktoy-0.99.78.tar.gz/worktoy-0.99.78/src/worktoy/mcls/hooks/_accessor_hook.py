"""AccessorHook hooks into the namespace system and logs each call to
__getitem__ and __setitem__, but does not otherwise modify any behaviour. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ...waitaminute import MissingVariable
from . import AbstractHook

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Callable, Self
  from worktoy.mcls import AbstractNamespace as ASpace


class _Field:
  """Key is a descriptor that logs calls to __setitem__ on the
  namespace object. """

  __field_name__ = None
  __field_owner__ = None
  __private_name__ = None

  def __init__(self, *args) -> None:
    """Initialize the Key object."""
    if args:
      self.__private_name__ = args[0]

  def getFallbackValue(self) -> Any:
    """Get the fallback value."""

  def __set_name__(self, owner: type, name: str) -> None:
    """Set the name of the field and the owner of the field."""
    self.__field_name__ = name
    self.__field_owner__ = owner

  def _getFieldName(self, ) -> str:
    """Getter-function for the field name."""
    if self.__field_name__ is None:
      raise MissingVariable('__field_name__', str)
    return self.__field_name__

  def _getFieldOwner(self, ) -> type:
    """Getter-function for the field owner."""
    if self.__field_owner__ is None:
      raise MissingVariable('__field_owner__', type)
    return self.__field_owner__

  def _getPrivateName(self) -> str:
    """Getter-function for the private name."""
    fieldName = self._getFieldName()
    if self.__private_name__ is None:
      if fieldName.startswith('__') and fieldName.endswith('__'):
        return '_pvt_%s' % fieldName[2:-2]
      words = []
      word = []
      for char in fieldName:
        if char.isupper():
          if word:
            words.append(''.join(word))
            word = []
        word.append(char.lower())
      return '__%s__' % '_'.join(words)
    return self.__private_name__

  def __get__(self, instance: object, owner: type) -> Any:
    """Get the name of the function."""
    if instance is None:
      return self
    pvtName = self._getPrivateName()
    return getattr(instance, pvtName, self.getFallbackValue())


class _Key(_Field):
  """Key is a descriptor that logs calls to __getitem__ on the
  namespace object. """
  pass


class _Value(_Field):
  """Value is a descriptor that logs calls to __setitem__ on the
  namespace object. """
  pass


class _GetItem:
  """Represents a __getitem__ call. """

  __pvt_key__ = None
  __pvt_val__ = None
  __pvt_err__ = None

  key = _Key('__pvt_key__')
  value = _Value('__pvt_val__')
  err = _Value('__pvt_err__')

  def __init__(self, key: str, value: Any, ) -> None:
    """Initialize the __getitem__ call."""
    self.__pvt_key__ = key
    if isinstance(value, Exception):
      self.__pvt_err__ = value
    elif value is not None:
      self.__pvt_val__ = value


class _SetItem:
  """Represents a __setitem__ call. """

  __pvt_key__ = None
  __new_val__ = None
  __old_val__ = None

  key = _Key('__pvt_key__')
  new_val = _Value('__new_val__')
  old_val = _Value('__old_val__')

  def __init__(self, *args) -> None:
    _key, _new, _old = [*args, None, None, None][:3]
    if _key is not None:
      self.__pvt_key__ = _key
    if _new is not None:
      self.__new_val__ = _new
    if _old is not None:
      self.__old_val__ = _old


class AccessorHook(AbstractHook):
  """AccessorHook hooks into the namespace system and logs each call to
  __getitem__ and __setitem__, but does not otherwise modify any
  behaviour. """

  __log_name__ = '__accessor_lines__'

  def _getLogName(self, ) -> str:
    """Getter-function for log name."""
    if self.__log_name__ is None:
      raise MissingVariable('__log_name__', str)
    return self.__log_name__

  def getItemHook(self, space: ASpace, key: str, value: Any) -> bool:
    """Hook for getItem. This is called before the __getitem__ method of
    the namespace object is called. The default implementation does nothing
    and returns False. """
    pvtName = self._getLogName()
    item = _GetItem(key, value)
    instance = self.getOwningNamespace()
    setattr(instance, pvtName, item)
    return False

  def setItemHook(
      self,
      space: ASpace,
      key: str,
      value: object,
      oldValue: object
  ) -> bool:
    """Hook for setItem. This is called before the __setitem__ method of
    the namespace object is called. The default implementation does nothing
    and returns False. """
    pvtName = self._getLogName()
    item = _SetItem(key, value, oldValue)
    instance = self.getOwningNamespace()
    setattr(instance, pvtName, item)
    return False
