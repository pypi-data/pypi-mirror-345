"""OverloadHook hooks into the namespace system and collects the overload
decorated methods replacing them with a dispatcher that calls the
correct method based on the arguments passed to it. It is used to
provide a simple way to overload methods in the namespace system."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ...static import Dispatch
from . import AbstractHook

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import TypeAlias
  from worktoy.mcls import BaseSpace as BSpace
  from .. import FunctionType as Func

  Types: TypeAlias = tuple[type, ...]
  TypesDict: TypeAlias = dict[Types, Func]
  KeyTypesDict: TypeAlias = dict[str, TypesDict]
  FuncDict: TypeAlias = dict[str, list[Func]]
  HashDict: TypeAlias = dict[int, Func]
  KeyHashFunc: TypeAlias = dict[str, HashDict]
  FuncList: TypeAlias = list[Func]
  KeyFunc: TypeAlias = dict[str, Func]
  KeyFuncList: TypeAlias = dict[str, FuncList]


class OverloadHook(AbstractHook):
  """OverloadHook hooks into the namespace system and collects the overload
  decorated methods replacing them with a dispatcher that calls the
  correct method based on the arguments passed to it. It is used to
  provide a simple way to overload methods in the namespace system.
  """

  def setItemHook(
      self,
      space: BSpace,
      key: str,
      value: object,
      oldValue: object
  ) -> bool:
    """Set the item hook for the namespace system. This method is called
    when an item is set in the namespace system. It collects the
    overload decorated methods and replaces them with a dispatcher that
    calls the correct method based on the arguments passed to it."""
    if getattr(value, '__is_overloaded__', None) is None:
      return False
    typeSigs = getattr(value, '__type_sigs__', None)
    for sig in typeSigs:
      space.addOverload(key, sig, value)
    return True

  def postCompileHook(self, space: BSpace, namespace: dict) -> dict:
    """Post compile hook for the namespace system. This method is called
    after the namespace system is compiled. It collects the overload
    decorated methods and replaces them with a dispatcher that calls the
    correct method based on the arguments passed to it."""
    overloadMap = space.getOverloadMap()
    dispatchNames = []
    for key, sigMap in overloadMap.items():
      namespace[key] = Dispatch(sigMap)
      dispatchNames.append(key)
    namespace['__dispatch_names__'] = dispatchNames
    return namespace
