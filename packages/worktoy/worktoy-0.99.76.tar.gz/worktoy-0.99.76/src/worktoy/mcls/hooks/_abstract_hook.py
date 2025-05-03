"""AbstractHook provides an abstract baseclass for hooks used by the
namespaces in the metaclass system. These hooks allow modification of the
class creation process. The following static methods are expected from the
hooks:
- setItem: called before calls to __setitem__ on the namespace object.
- getItem: called before calls to __getitem__ on the namespace object.
- preCompile: called before the final namespace object is populated with
the conventional key, value pairs.
- postCompile: called after the final namespace object is populated with
the conventional key, value pairs.

Subclasses may implement either of the above methods. The default
implementations have no effect, so subclasses need only implement the
methods they are interested in.

AbstractHook implements the descriptor protocol such that calls to
'__get__' receive:
- instance: The current instance of the namespace object.
- owner: The current namespace class

Subclasses should be made available as attributes on the namespace subclass.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ...waitaminute import MissingVariable, ReadOnlyError

try:
  from typing import TYPE_CHECKING, Type
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Self, Callable, Self, Never
  from worktoy.mcls import AbstractNamespace as ASpace

  AccessorHook = Callable[[ASpace, str, Any], Any]
  CompileHook = Callable[[ASpace, dict], dict]


class AbstractHook:
  """AbstractHook provides an abstract baseclass for hooks used by the
  namespaces in the metaclass system. These hooks allow modification of the
  class creation process. The following static methods are expected from the
  hooks:
  - setItem: called before calls to __setitem__ on the namespace object.
  - getItem: called before calls to __getitem__ on the namespace object.
  - preCompile: called before the final namespace object is populated with
    the conventional key, value pairs.
  - postCompile: called after the final namespace object is populated with
    the conventional key, value pairs.

  Subclasses may implement either of the above methods. The default
  implementations have no effect, so subclasses need only implement the
  methods they are interested in.

  AbstractHook implements the descriptor protocol such that calls to
  '__get__' receive:
  - instance: The current instance of the namespace object.
  - owner: The current namespace class

  Subclasses should be made available as attributes on the namespace
  subclass. """

  __field_name__ = None
  __field_owner__ = None

  __owning_instance__ = None
  __owning_class__ = None

  __owner_hooks_list_name__ = '__hook_objects__'
  __owner_hooks_getter_name__ = 'getHooks'

  @classmethod
  def _getOwnerHooksName(cls) -> str:
    """Getter-function for the name at which the hook is available on the
    namespace class. """
    if cls.__owner_hooks_list_name__ is None:
      raise MissingVariable('__owner_hooks_name__', str)
    return cls.__owner_hooks_list_name__

  @classmethod
  def _getOwnerHooksGetterName(cls) -> str:
    """Getter-function for the name at which the hook is available on the
    namespace class. """
    if cls.__owner_hooks_getter_name__ is None:
      raise MissingVariable('__owner_hooks_getter_name__', str)
    return cls.__owner_hooks_getter_name__

  def __set_name__(self, owner: type, name: str) -> None:
    """Set the name of the field and the owner of the field."""
    self.__field_name__ = name
    self.__field_owner__ = owner
    if TYPE_CHECKING:
      assert issubclass(owner, ASpace)
    owner.addHook(self, )

  def __get__(self, instance: object, owner: type) -> Self:
    """Get the wrapped function. The owner is the class through which the
    descriptor is accessed. This is either __field_class__ or a subclass
    hereof. """
    self.__owning_instance__ = instance
    self.__owning_class__ = owner
    return self

  def __set__(self, instance: object, value: object) -> Never:
    """Set the wrapped function. This is not allowed. """
    raise ReadOnlyError(instance, self, value)

  def getOwningNamespace(self) -> ASpace:
    """Get the owning instance. This is the instance of the namespace
    object that owns this hook. """
    if TYPE_CHECKING:
      assert isinstance(self.__owning_instance__, ASpace)
    return self.__owning_instance__

  def getPrimeSpace(self) -> ASpace:
    """Get the prime space. This is the instance of the namespace object
    that owns this hook. """
    namespace = self.getOwningNamespace()
    if TYPE_CHECKING:
      assert isinstance(namespace, ASpace)
    return namespace.getPrimeSpace()

  def getOwningClass(self) -> type:
    """Get the owning class. This is the class of the namespace object
    that owns this hook. """
    return self.__owning_class__

  def getItemHook(self, space: ASpace, key: str, value: object) -> bool:
    """Hook for getItem. This is called before the __getitem__ method of
    the namespace object is called. The default implementation does nothing
    and returns False. """
    if TYPE_CHECKING:
      assert isinstance(self, AbstractHook)
    self.__owning_instance__ = space
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
    if TYPE_CHECKING:
      assert isinstance(self, AbstractHook)
    self.__owning_instance__ = space
    return False

  def preCompileHook(self, space: ASpace, namespace: dict) -> dict:
    """Hook for preCompile. This is called before the __init__ method of
    the namespace object is called. The default implementation does nothing
    and returns the contents unchanged. """
    if TYPE_CHECKING:
      assert isinstance(self, AbstractHook)
    self.__owning_instance__ = space
    return namespace

  def postCompileHook(self, space: ASpace, namespace: dict) -> dict:
    """Hook for postCompile. This is called after the __init__ method of
    the namespace object is called. The default implementation does nothing
    and returns the contents unchanged. """
    if TYPE_CHECKING:
      assert isinstance(self, AbstractHook)
    self.__owning_instance__ = space
    return namespace
