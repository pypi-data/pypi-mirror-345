"""NameHook filters named used in the namespace system. If it encounters
names that are near-misses of commonly used names, it will raise a
QuestionableSyntax exception. Because these names refer to built-in
functions, the near-miss names will not generally cause any errors related
to names. Instead, the built-in function is called instead of the
near-miss named custom function. Tracing the unexpected behaviour back
to the near-miss name is by no means obvious because of the presence
of the built-in function.

Below is a list of common functions along with potential near-miss names
and some comments.

# 1. __init__: Near-miss name: __int__
Both __init__ and __int__ find common use. The hook will inspect the
typehint of the return value. '__init__' and '__int__' should return
'None' and 'int' respectively. '__int__' should expect only 'self' as an
argument, whereas '__init__' might expect other arguments.

# 2. __set_name__: Near-miss name: __setname__ When a class body has a
key, value pair with value being of a type implementing __set_name__,
then this method is called when the owning class returns from __new__ in
the metaclass, but before __init__ is called. Although there is no
built-in implementation of __set_name__, no error will  be raised by its
absence. The typehints of the __set_name__ method  are:

  def __set_name__(self, owner: type, name: str) -> None:
    ...

# 3. __getitem__: Near-miss name: __get_item__ Dictionary like classes
call this method when encountering the syntax:
  dictLike = DictLike()
  print(dictLike[key])  # equivalent to:
  DictLike.__getitem__(dictLike, key)

# 4. __setitem__: Near-miss name: __set_item__ Exactly like above:
  dictLike = DictLike()
  dictLike[key] = value  # equivalent to:
  DictLike.__setitem__(dictLike, key, value)

# 5. __del__: Near-miss name: __delete__ When implementing the descriptor
protocol, the get and set accessors are '__get__' and '__set__' respectively.
The delete-accessor is '__delete__', but mistakenly using '__del__' does
happen. Since __del__ is a built-in function relating to garbage
collecting, this near-miss will cause HIGHLY UNDEFINED BEHAVIOUR.

"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import AbstractHook
from ...waitaminute import QuestionableSyntax

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any
  from .. import AbstractNamespace as ASpace


class _Name:
  """Name descriptor."""

  __pvt_name__ = None

  def __init__(self, pvtName: str) -> None:
    """Initialize the Name object."""
    self.__pvt_name__ = pvtName

  def __get__(self, instance: object, owner: type) -> Any:
    """Get the name of the function."""
    if instance is None:
      return self
    return getattr(instance, self.__pvt_name__, )


class _NearMiss:
  """Encapsulates a near-miss name and the real name."""

  __correct_name__ = None
  __missed_name__ = None

  correct = _Name('__correct_name__')
  missed = _Name('__missed_name__')

  def __init__(self, correctName: str, missedName: str) -> None:
    """Initialize the NearMiss object."""
    self.__correct_name__ = correctName
    self.__missed_name__ = missedName


class NameHook(AbstractHook):
  """NameHook filters named used in the namespace system. If it encounters
  names that are near-misses of commonly used names, it will raise a
  QuestionableSyntax exception. """

  @classmethod
  def _getNearMisses(cls) -> list[_NearMiss]:
    """Get the near-miss names."""
    return [
        _NearMiss('__set_name__', '__setname__'),
        _NearMiss('__getitem__', '__get_item__'),
        _NearMiss('__setitem__', '__set_item__'),
        _NearMiss('__delitem__', '__del_item__'),
    ]

  @classmethod
  def _validateName(cls, name: str) -> bool:
    """Compares the name to list of potential near-miss names. If the name
    is a near-miss, a QuestionableSyntax exception is raised. """
    nearMisses = cls._getNearMisses()
    for nearMiss in nearMisses:
      if name == nearMiss.missed:
        raise QuestionableSyntax(nearMiss.missed, nearMiss.correct)
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
    return self._validateName(key)
