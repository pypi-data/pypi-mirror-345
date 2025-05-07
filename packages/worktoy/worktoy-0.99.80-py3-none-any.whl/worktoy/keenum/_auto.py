"""The auto function creates an enumeration member. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..attr import Field
from ..text import typeMsg
from ..waitaminute import MissingVariable, VariableNotNone

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Self


class NUM:
  """The NUM class provides a temporary dataclass for enumeration
  entries. """

  __iter_contents__ = None

  __member_name__ = None
  __member_value__ = None

  key = Field()
  val = Field()

  @key.GET
  def _getKey(self, ) -> str:
    """Get the key of the enumeration member."""
    if self.__member_name__ is None:
      raise MissingVariable('__member_name__', str)
    if isinstance(self.__member_name__, str):
      return self.__member_name__
    raise TypeError(typeMsg('__member_name__', self.__member_name__, str))

  @key.SET
  def _setKey(self, key: str) -> None:
    """Set the key of the enumeration member."""
    if self.__member_name__ is not None:
      raise VariableNotNone('__member_name__', )
    if not isinstance(key, str):
      raise TypeError(typeMsg('__member_name__', key, str))
    self.__member_name__ = key

  @val.GET
  def _getVal(self, ) -> Any:
    """Get the value of the enumeration member."""
    if self.__member_value__ is None:
      return self.__member_name__
    return self.__member_value__

  @val.SET
  def _setVal(self, value: Any) -> None:
    """Set the value of the enumeration member."""
    if self.__member_value__ is not None:
      raise VariableNotNone('__member_value__', )
    self.__member_value__ = value

  def __iter__(self) -> Self:
    """Iterate over the enumeration member."""
    self.__iter_contents__ = [self.key, self.val]
    return self

  def __next__(self) -> Any:
    """Get the next item in the enumeration member."""
    if self.__iter_contents__:
      return self.__iter_contents__.pop(0)
    raise StopIteration

  def __getitem__(self, identifier: Any) -> Any:
    """Get the item from the enumeration member."""
    if isinstance(identifier, str):
      if len(identifier) > 2:
        if identifier.lower()[:3] == 'key':
          return self.key
        if identifier.lower()[:3] == 'val':
          return self.val
      raise KeyError(identifier)
    if isinstance(identifier, int):
      if identifier < 2:
        if identifier % 2:
          return self.val
        return self.key
    valType = type(self.val)
    if isinstance(identifier, valType):
      if identifier == self.val:
        return self.val

  def asDict(self) -> dict:
    """Get the enumeration member as a dictionary."""
    return {self.key: self.val}

  @classmethod
  def fromValue(cls, *args) -> Self:
    """Create a new enumeration member from a value."""
    self = cls()
    if len(args) == 1:
      value = args[0]
    else:
      value = args
    self.val = value
    return self


def auto(innerValue: Any = None, ) -> NUM:
  """The auto function creates an enumeration member.

  Args:
    innerValue: The value to be assigned to the enumeration member.
  """
  return NUM.fromValue(innerValue)
