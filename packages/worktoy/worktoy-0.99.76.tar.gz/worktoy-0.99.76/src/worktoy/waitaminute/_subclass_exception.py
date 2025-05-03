"""SubclassException should be raised when a class is not a subclass of
the expected base class. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import _Attribute

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Self, Any, Callable, Never


class _SubclassException(TypeError):
  """SubclassException should be raised when a class is not a subclass of
  the expected base class."""

  def __init__(self, obj: object, expBase: type, ) -> None:
    """Initialize the exception with the object and expected base class."""
    if isinstance(obj, type):
      cls = obj
      infoSpec = """Expected subclass of '%s', but received '%s%s' having 
      the following method resolution order: <br><tab>%s"""
      objStr = ''
    else:
      cls = type(obj)
      infoSpec = """Expected object of a subclass of '%s', but received
      object: '%s' of type: '%s' having the following method resolution
      order: <br><tab>%s"""
      objStr = str(obj)
    expName = expBase.__name__
    clsName = cls.__name__
    clsMRO = cls.__mro__
    mroStr = '<br><tab>'.join([base.__name__ for base in clsMRO])
    info = infoSpec % (expName, objStr, clsName, mroStr)
    TypeError.__init__(self, info)


class SubclassException(TypeError):
  """SubclassException should be raised when a class is not a subclass of
  the expected base class."""

  actualObject = _Attribute(None)
  actualClass = _Attribute()
  expectedClass = _Attribute()

  def __init__(self, obj: object, expBase: type) -> None:
    """Initialize the exception with the object and expected base class."""
    if isinstance(obj, type):
      self.actualClass = obj
    else:
      self.actualClass = type(obj)
      self.actualObject = obj
    self.expectedClass = expBase
    if self.actualObject is not None:
      infoSpec = """Expected object of a subclass of '%s', but received 
      '%s' having mro: <br><tab>%s. """
      expName = expBase.__name__
      objStr = str(obj)
      mroList = [base for base in self.actualClass.__mro__]
      mroNames = [base.__name__ for base in mroList]
      mroStr = '<br><tab>'.join(mroNames)
      info = infoSpec % (expName, objStr, mroStr)
    else:
      infoSpec = """Expected subclass of '%s', but received '%s' having mro:
      <br><tab>%s. """
      expName = expBase.__name__
      objStr = ''
      mroList = [base for base in self.actualClass.__mro__]
      mroNames = [base.__name__ for base in mroList]
      mroStr = '<br><tab>'.join(mroNames)
      info = infoSpec % (expName, objStr, mroStr)
    TypeError.__init__(self, info)

  def _resolveOther(self, other: object) -> Self:
    """Resolve the other object."""
    cls = type(self)
    if isinstance(other, cls):
      return other
    if isinstance(other, (tuple, list)):
      try:
        return cls(*other)
      except TypeError:
        return NotImplemented
    return NotImplemented

  def __eq__(self, other: object) -> bool:
    """Compare the exception to another object."""
    cls = type(self)
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    if isinstance(other, cls):
      if self.actualObject != other.actualObject:
        return False
      if self.expectedClass != other.expectedClass:
        return False
      if self.actualClass != other.actualClass:
        return False
      return True
    return False
