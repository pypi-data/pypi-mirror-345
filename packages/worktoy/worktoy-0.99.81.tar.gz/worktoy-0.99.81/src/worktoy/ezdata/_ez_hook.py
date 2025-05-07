"""EZHook collects the field entries in EZData class bodies. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..mcls import FunctionType
from ..mcls.hooks import AbstractHook

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Callable
  from worktoy.ezdata import EZSpace, EZData


class _EZIter:
  """_EZIter provides an iterator for the EZData class. """

  __iter_contents__ = None

  def __init__(self, *args) -> None:
    """The __init__ method is called when the class is created."""
    self.__iter_contents__ = [*args, ]

  def __next__(self, ) -> Any:
    """The __next__ method is called when the class is created."""
    if self.__iter_contents__:
      return self.__iter_contents__.pop(0)
    self.__iter_contents__ = None
    raise StopIteration()


class EZHook(AbstractHook):
  """EZHook collects the field entries in EZData class bodies. """

  @staticmethod
  def initFactory(*dataFields) -> FunctionType:
    """The initFactory method is called when the class is created."""

    slotKeys = [dataField.key for dataField in dataFields]
    defVals = [dataField.val for dataField in dataFields]

    def __init__(self, *args, **kwargs):
      """The __init__ method is called when the class is created."""
      posArgs = [*args, ]
      while len(posArgs) < len(slotKeys):
        posArgs.append(None)
      for key, defVal in zip(slotKeys, defVals):
        setattr(self, key, defVal)
      for key, arg in zip(slotKeys, posArgs):
        if arg is not None:
          setattr(self, key, arg)
      for key in slotKeys:
        if key in kwargs:
          setattr(self, key, kwargs[key])

    return __init__

  @staticmethod
  def eqFactory(*dataFields) -> FunctionType:
    """The eqFactory method is called when the class is created."""

    def __eq__(self, other: EZData) -> bool:
      """The __eq__ method is called when the class is created."""
      for dataField in dataFields:
        key = dataField.key
        if getattr(self, key) != getattr(other, key):
          return False
      return True

    return __eq__

  @staticmethod
  def strFactory(*dataFields) -> FunctionType:
    """The strFactory method is called when the class is created."""

    def __str__(self) -> str:
      """The __str__ method is called when the class is created."""
      clsName = type(self).__name__
      keys = [dataField.key for dataField in dataFields]
      vals = [str(getattr(self, key)) for key in keys]
      keyVals = ['%s=%s' % (key, val) for key, val in zip(keys, vals)]
      return """%s(%s)""" % (clsName, ', '.join(keyVals))

    return __str__

  @staticmethod
  def reprFactory(*dataFields) -> FunctionType:
    """The reprFactory method is called when the class is created."""

    def __repr__(self) -> str:
      """The __repr__ method is called when the class is created."""
      clsName = type(self).__name__
      keys = [dataField.key for dataField in dataFields]
      vals = [str(getattr(self, key)) for key in keys]
      return """%s(%s)""" % (clsName, ', '.join(vals))

    return __repr__

  @staticmethod
  def iterFactory(*dataFields) -> FunctionType:
    """The iterFactory method is called when the class is created."""

    def __iter__(self, ) -> _EZIter:
      """The __iter__ method is called when the class is created."""
      keys = [dataField.key for dataField in dataFields]
      vals = [getattr(self, key) for key in keys]
      return _EZIter(*vals)

    return __iter__

  @staticmethod
  def getItemFactory(*dataFields) -> FunctionType:
    """The getItemFactory method is called when the class is created."""

    def __getitem__(self, key: str) -> object:
      """The __getitem__ method is called when the class is created."""
      if key in self.__slots__:
        return getattr(self, key)
      raise KeyError(key)

    return __getitem__

  @staticmethod
  def setItemFactory(*dataFields) -> FunctionType:
    """The setItemFactory method is called when the class is created."""

    def __setitem__(self, key: str, value: object) -> None:
      """The __setitem__ method is called when the class is created."""
      if key in self.__slots__:
        return setattr(self, key, value)
      raise KeyError(key)

    return __setitem__

  def setItemHook(
      self,
      space: EZSpace,
      key: str,
      value: object,
      oldValue: object
  ) -> bool:
    """The setItemHook method is called when an item is set in the
    enumeration."""
    if callable(value):
      return False
    space.addField(key, type(value), value)
    return True

  def preCompileHook(self, space: EZSpace, namespace: dict) -> dict:
    """The preCompileHook method is called before the class is compiled."""
    dataFields = space.getDataFields()
    namespace['__slots__'] = (*[dataField.key for dataField in dataFields],)
    return namespace

  def postCompileHook(self, space: EZSpace, namespace: dict) -> dict:
    """The postCompileHook method is called after the class is compiled."""
    dataFields = space.getDataFields()
    initMethod = self.initFactory(*dataFields)
    eqMethod = self.eqFactory(*dataFields)
    strMethod = self.strFactory(*dataFields)
    reprMethod = self.reprFactory(*dataFields)
    iterMethod = self.iterFactory(*dataFields)
    getItemMethod = self.getItemFactory(*dataFields)
    setItemMethod = self.setItemFactory(*dataFields)
    namespace['__init__'] = initMethod
    namespace['__eq__'] = eqMethod
    namespace['__str__'] = strMethod
    namespace['__repr__'] = reprMethod
    namespace['__iter__'] = iterMethod
    namespace['__getitem__'] = getItemMethod
    namespace['__setitem__'] = setItemMethod
    return namespace
