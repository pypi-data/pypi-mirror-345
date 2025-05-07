"""AbstractField provides an implementation of the descriptor protocol
that allow the owning class to explicitly define the accessor methods.  """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..mcls import FunctionType as Func
from ..parse import maybe
from ..text import typeMsg
from ..waitaminute import VariableNotNone, MissingVariable

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Self, Any, Callable


class Field:
  """AbstractField provides an implementation of the descriptor protocol
  that allow the owning class to explicitly define the accessor methods.  """

  __field_name__ = None
  __field_owner__ = None

  __setter_keys__ = None
  __getter_key__ = None
  __deleter_keys__ = None

  def __set_name__(self, owner: type, name: str) -> None:
    """Set the name of the field."""
    self.__field_name__ = name
    self.__field_owner__ = owner

  def _getSetterKeys(self, ) -> tuple[str, ...]:
    """Getter-function for names of methods called when __set__ is called."""
    return maybe(self.__setter_keys__, ())

  def _getGetterKey(self, ) -> str:
    """Getter-function for name of method called when __get__ is called."""
    return self.__getter_key__

  def _getDeleterKeys(self) -> tuple[str, ...]:
    """Getter-function for names of methods called when __delete__ is
    called."""
    return maybe(self.__deleter_keys__, ())

  def _addSetterKey(self, setterKey: str) -> None:
    """Add a setter key to the list of setter keys."""
    if not isinstance(setterKey, str):
      raise TypeError(typeMsg('setterKey', setterKey, str))
    existing = self._getSetterKeys()
    self.__setter_keys__ = (*[*existing, setterKey],)

  def _setGetterKey(self, getterKey: str) -> None:
    """Set the getter key."""
    if self.__getter_key__ is not None:
      raise VariableNotNone('__getter_key__', )
    if not isinstance(getterKey, str):
      raise TypeError(typeMsg('getterKey', getterKey, str))
    self.__getter_key__ = getterKey

  def _addDeleterKey(self, key: str) -> None:
    """Add a deleter key to the list of deleter keys."""
    if not isinstance(key, str):
      raise TypeError(typeMsg('key', key, str))
    existing = self._getDeleterKeys()
    self.__deleter_keys__ = (*[*existing, key],)

  def __get__(self, instance: object, owner: type) -> Any:
    """Getter-function for the field."""
    if instance is None:
      return self
    getterKey = self._getGetterKey()
    if getterKey is None:
      raise MissingVariable('__getter_key__', str)
    if not isinstance(getterKey, str):
      raise TypeError(typeMsg('getterKey', getterKey, str))
    getterFunction = getattr(owner, getterKey, None)
    if getterFunction is None:
      raise MissingVariable(getterKey, Callable)
    if not callable(getterFunction):
      raise TypeError(typeMsg(getterKey, getterFunction, Func))
    return getterFunction(instance, )

  def __set__(self, instance: object, value: Any) -> None:
    """Setter-function for the field."""
    owner = type(instance)
    setterKeys = self._getSetterKeys()
    if not setterKeys:
      raise MissingVariable('__setter_keys__', tuple)
    if not isinstance(setterKeys, tuple):
      raise TypeError(typeMsg('__setter_keys__', setterKeys, tuple))
    for setterKey in setterKeys:
      if not isinstance(setterKey, str):
        raise TypeError(typeMsg('setterKey', setterKey, str))
      setterFunction = getattr(owner, setterKey, None)
      if setterFunction is None:
        raise MissingVariable(setterKey, Func)
      if not callable(setterFunction):
        raise TypeError(typeMsg(setterKey, setterFunction, Func))
      setterFunction(instance, value)

  def __delete__(self, instance: object) -> None:
    """Deleter-function for the field."""
    owner = type(instance)
    deleterKeys = self._getDeleterKeys()
    if not deleterKeys:
      raise MissingVariable('__deleter_keys__', tuple)
    if not isinstance(deleterKeys, tuple):
      raise TypeError(typeMsg('__deleter_keys__', deleterKeys, tuple))
    for deleterKey in deleterKeys:
      if not isinstance(deleterKey, str):
        raise TypeError(typeMsg('deleterKey', deleterKey, str))
      deleterFunction = getattr(owner, deleterKey, None)
      if deleterFunction is None:
        raise MissingVariable(deleterKey, Func)
      if not callable(deleterFunction):
        raise TypeError(typeMsg(deleterKey, deleterFunction, Func))
      deleterFunction(instance)

  def GET(self, callMeMaybe: Func) -> Func:
    """Decorator specifying the getter method for the field."""
    self._setGetterKey(callMeMaybe.__name__)
    return callMeMaybe

  def SET(self, callMeMaybe: Func) -> Func:
    """Decorator specifying the setter method for the field."""
    self._addSetterKey(callMeMaybe.__name__)
    return callMeMaybe

  def DELETE(self, callMeMaybe: Func) -> Func:
    """Decorator specifying the deleter method for the field."""
    self._addDeleterKey(callMeMaybe.__name__)
    return callMeMaybe

  def __init__(self, *args) -> None:
    if args:
      if isinstance(args[0], str):
        self._setGetterKey(args[0])
