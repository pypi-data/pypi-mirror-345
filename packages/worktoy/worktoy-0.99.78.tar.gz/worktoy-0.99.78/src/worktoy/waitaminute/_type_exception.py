"""TypeException is a custom exception class for handling type related
errors. Specifically, this exception should NOT be raised if the object is
None instead of the expected type. This is because None indicates absense
rather than type mismatch. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from warnings import warn

from . import _Attribute

from ..text import monoSpace, joinWords

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Self, Callable


def _resolveTypeNames(*types) -> str:
  """Creates the first part of the error message listing the expected type
  or types. """
  if len(types) == 1:
    if isinstance(types[0], (tuple, list)):
      return _resolveTypeNames(*types[0])
    if isinstance(types[0], type):
      expName = types[0].__name__
    elif isinstance(types[0], str):
      expName = types[0]
    else:
      raise TypeError("""Received bad arguments: %s""" % (str(types),))
    return """Expected object of type '%s'""" % (expName,)
  typeNames = []
  for type_ in types:
    if isinstance(type_, type):
      typeNames.append("""'%s'""" % type_.__name__)
    elif isinstance(type_, str):
      typeNames.append("""'%s'""" % type_)
    else:
      raise TypeError("""Received bad arguments: %s""" % (str(types),))
  infoSpec = """Expected object of any of the following types: %s"""
  typeStr = joinWords(*typeNames, sep='or')
  return monoSpace(infoSpec % (typeStr,))


class TypeException(TypeError):
  """
  TypeException is a custom exception class for handling type related
  errors. Specifically, this exception should NOT be raised if the object is
  None instead of the expected type.
  """

  varName = _Attribute()
  actType = _Attribute()
  expTypes = _Attribute()

  def __init__(self, name: str, obj: object, *types) -> None:
    """Initialize the TypeException with the name of the variable, the
    received object, and the expected types."""
    prelude = _resolveTypeNames(*types)
    actName = type(obj).__name__
    infoSpec = """%s at name: '%s', but received object of type '%s' with 
    repr: '%s'"""
    info = infoSpec % (prelude, name, actName, repr(obj))
    TypeError.__init__(self, monoSpace(info))
    self.varName = name
    self.actType = type(obj)
    self.expTypes = types

  def _resolveOther(self, other: Any) -> Self:
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
    """Compare the TypeException object with another object."""
    other = self._resolveOther(other)
    if other is NotImplemented:
      return False
    cls = type(self)
    if isinstance(other, cls):
      if self.varName != other.varName:
        return False
      if self.actType != other.actType:
        return False
      if self.expTypes != other.expTypes:
        return False
      return True
    return False
