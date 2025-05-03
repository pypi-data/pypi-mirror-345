"""The Dispatch class dispatches a function call to the appropriate
function based on the type of the first argument. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..static import TypeSig
from ..text import typeMsg, monoSpace
from ..waitaminute import HashMismatch, CastMismatch, ResolveException, \
  VariableNotNone, TypeException
from ..waitaminute import DispatchException

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Callable, TypeAlias, Never

  Types: TypeAlias = tuple[type, ...]
  Hashes: TypeAlias = list[int]
  HashMap: TypeAlias = dict[int, Callable]
  TypesMap: TypeAlias = dict[Types, Callable]
  CastMap: TypeAlias = dict[Types, Callable]
  CallMap: TypeAlias = dict[TypeSig, Callable]


class Dispatch:
  """The Dispatch class dispatches a function call to the appropriate
  function based on the type of the first argument. """

  __field_name__ = None  # name of the function
  __field_owner__ = None  # owner of the function

  __call_map__ = None

  __bound_instance__ = None  # bound instance

  def _getBoundInstance(self) -> object:
    """Get the bound instance."""
    return self.__bound_instance__

  def __set_name__(self, owner: type, name: str) -> None:
    """Set the name of the function."""
    self.__field_name__ = name
    self.__field_owner__ = owner

    for sig, call in self.__call_map__.items():
      if not isinstance(sig, TypeSig):
        raise TypeError(typeMsg('sig', sig, TypeSig))
      if not callable(call):
        from worktoy.mcls import FunctionType
        raise TypeError(typeMsg('call', call, FunctionType))
      TypeSig.replaceTHIS(sig, owner)

  def __init__(self, callMap: CallMap) -> None:
    self.__call_map__ = callMap

  def __get__(self, instance: object, owner: type) -> Dispatch:
    """Get the bound instance."""
    self.__bound_instance__ = instance
    return self

  def __set__(self, *__, **_) -> Never:
    """Set the value of the field."""
    raise TypeError('Cannot set attribute on class')

  def _fastCall(self, *args: Any, **kwargs: Any) -> Any:
    """Fast call the function."""
    instance = self._getBoundInstance()
    for sig, call in self.__call_map__.items():
      try:
        posArgs = sig.fast(*args)
      except HashMismatch:
        continue
      except TypeError as typeError:
        if 'required positional argument' in str(typeError):
          continue
        raise typeError
      if instance is not None:
        return call(instance, *posArgs, **kwargs)
      return call(*posArgs, **kwargs)
    raise DispatchException(self, *args)

  def _flexCall(self, *args: Any, **kwargs: Any) -> Any:
    """Flex call the function."""
    instance = self._getBoundInstance()
    for sig, call in self.__call_map__.items():
      try:
        posArgs = sig.flex(*args)
      except HashMismatch:
        continue
      except CastMismatch:
        continue
      try:
        if instance is not None:
          return call(instance, *posArgs, **kwargs)
        return call(*posArgs, **kwargs)
      except TypeError as typeError:
        continue
      except IndexError as indexError:
        continue

    raise DispatchException(self, *args)

  def _resolveArgs(self, *args) -> tuple:
    """Resolves tuples, lists and strings. """
    posArgs = []
    anyResolved = False
    for arg in args:
      if isinstance(arg, list):
        posArgs = [*posArgs, *arg]
        anyResolved = True
        continue
      if isinstance(arg, tuple):
        posArgs = [*posArgs, *arg]
        anyResolved = True
        continue
      if isinstance(arg, str):
        posArgs.append(eval(arg))
        anyResolved = True
        continue
      posArgs.append(arg)
    if anyResolved:
      return (*posArgs,)
    raise ResolveException(self, args)

  def __call__(self, *args: Any, **kwargs: Any) -> Any:
    """Call the function."""
    try:
      return self._fastCall(*args, **kwargs)
    except DispatchException as fastException:
      pass
    try:
      return self._flexCall(*args, **kwargs)
    except DispatchException as flexException:
      pass
    try:
      posArgs = self._resolveArgs(*args)
    except ResolveException as resolveException:
      raise DispatchException(self, *args) from resolveException
    while True:
      try:
        posArgs = self._resolveArgs(*posArgs)
      except ResolveException:
        break
    return self.__call__(*posArgs, **kwargs)

  def getTypeSigs(self) -> list[TypeSig]:
    """Get the type signatures."""
    return [*self.__call_map__.keys(), ]

  def __str__(self, ) -> str:
    """Get the string representation of the function."""
    sigStr = [str(sig) for sig in self.getTypeSigs()]
    info = """%s object supporting type signatures: \n%s"""
    sigLines = '<br><tab>'.join(sigStr)
    return monoSpace(info % (self.__field_name__, sigLines))

  def __repr__(self, ) -> str:
    """Get the string representation of the function."""
    return object.__repr__(self)

  def replaceThis(self, cls: type) -> None:
    """Replace THIS with the class."""
    for sig in self.getTypeSigs():
      sig.replaceTHIS(cls)

  def getFieldName(self, ) -> str:
    """Get the field name."""
    if self.__field_name__ is None:
      raise VariableNotNone('__field_name__')
    if isinstance(self.__field_name__, str):
      return self.__field_name__
    raise TypeException('__field_name__', self.__field_name__, str)

  def getFieldOwner(self, ) -> type:
    """Get the field owner."""
    if self.__field_owner__ is None:
      raise VariableNotNone('__field_owner__')
    if isinstance(self.__field_owner__, type):
      return self.__field_owner__
    raise TypeException('__field_owner__', self.__field_owner__, type)
