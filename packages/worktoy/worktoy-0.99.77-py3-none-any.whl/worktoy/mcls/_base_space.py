"""BaseSpace provides the namespace class for the worktoy.mcls module."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..waitaminute import VariableNotNone
from . import AbstractNamespace
from .hooks import AccessorHook, OverloadHook, NameHook, ReservedNameHook

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import TypeAlias, Callable, Any
  from worktoy.static import TypeSig
  from worktoy.mcls import FunctionType as Func

  OverloadMap: TypeAlias = dict[str, dict[TypeSig, Callable[..., Any]]]


class BaseSpace(AbstractNamespace):
  """BaseSpace provides the namespace class for the worktoy.mcls module."""

  __overload_map__ = None

  def _buildOverloadMap(self, ) -> None:
    """Build the overload map for the namespace."""
    if self.__overload_map__ is not None:
      raise VariableNotNone('__overload_map__', )
    if self.isPrime():
      self.__overload_map__ = {}
      return
    parentSpace = self.getParentSpace()
    self.__overload_map__ = {**parentSpace.getOverloadMap(), }

  def getOverloadMap(self, **kwargs) -> OverloadMap:
    """Get the overload map for the namespace."""
    if self.__overload_map__ is None:
      if kwargs.get('_recursion', False):
        raise RecursionError
      self._buildOverloadMap()
      return self.getOverloadMap(_recursion=True)
    return self.__overload_map__

  def addOverload(self, key: str, sig: TypeSig, func: Func) -> None:
    """Add an overload to the overload map."""
    overloadMap = self.getOverloadMap()
    existingMap = overloadMap.get(key, {})
    existingMap[sig] = func
    overloadMap[key] = existingMap
    self.__overload_map__ = overloadMap

  reservedNameHook = ReservedNameHook()
  accessorHook = AccessorHook()
  overloadHook = OverloadHook()
  nameHook = NameHook()
