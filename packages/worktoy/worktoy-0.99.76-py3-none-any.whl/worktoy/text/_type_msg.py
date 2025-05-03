"""The 'typeMsg' function generates a structured error message when an
object with a given name does not belong to the given type.

Example:

  def square(number: int) -> int:
    #  The function expects an integer as argument
    if not isinstance(number, int):
      e = typeMsg('number', number, int)
      raise TypeError(e)
    return number ** 2

  square(69.420)
"""
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

from warnings import warn

from . import monoSpace, joinWords


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


def typeMsg(name: str, obj: object, *types) -> str:
  """The 'typeMsg' function generates a structured error message when an
  object with a given name does not belong to the given type."""

  prelude = _resolveTypeNames(*types)
  actName = type(obj).__name__
  infoSpec = """%s at name: '%s', but received object of type '%s' with 
  repr: '%s'"""
  info = infoSpec % (prelude, name, actName, repr(obj))
  return monoSpace(info)
