"""AttriBox provides a descriptor with lazy instantiation of the
underlying object. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..static import DELETED
from ..text import monoSpace
from ..waitaminute import MissingVariable, TypeException
from . import AbstractBox

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any


class AttriBox(AbstractBox):
  """AttriBox provides a descriptor with lazy instantiation of the
  underlying object. """

  def __class_getitem__(cls, fieldType: type) -> AttriBox:
    """Get the field type."""
    self = cls()
    self._setFieldType(fieldType)
    return self

  def __call__(self, *args, **kwargs) -> AttriBox:
    """Call the descriptor with the given arguments."""
    self._setPosArgs(*args)
    self._setKeyArgs(**kwargs)
    return self

  def _createInitObject(self, instance: object, ) -> Any:
    """Create the object."""
    fieldTypes = self._getFieldTypes()
    posArgs = self._getPosArgs(instance)
    keyArgs = self._getKeyArgs(instance)
    exception = None
    for cls in fieldTypes:
      try:
        newObject = cls(*posArgs, **keyArgs)
      except TypeError as typeError:
        if exception is None:
          exception = typeError
      else:
        return newObject
    else:
      raise exception

  def _getExistingObject(self, instance: object) -> Any:
    """Get the existing object."""
    pvtName = self.getPrivateName()
    existingObject = getattr(instance, pvtName, None)
    if existingObject is DELETED:
      e = """Attempted to access attribute '%s' from object of type: '%s',
      which has been deleted!""" % (pvtName, type(instance),)
      raise AttributeError(monoSpace(e))
    if existingObject is None:
      fieldTypes = self._getFieldTypes()
      raise MissingVariable(pvtName, *fieldTypes)
    return existingObject

  def _instanceGet(self, instance: Any, **kwargs) -> Any:
    """Get the instance."""
    pvtName = self.getPrivateName()
    fieldTypes = self._getFieldTypes()
    try:
      out = self._getExistingObject(instance)
    except MissingVariable:
      if kwargs.get('_recursion', False):
        raise RecursionError
      out = self._createInitObject(instance)
      setattr(instance, pvtName, out)
      return self._instanceGet(instance, _recursion=True)
    else:
      return out

  def _instanceSet(self, instance: Any, value: Any, **kwargs) -> None:
    """Set the instance."""
    pvtName = self.getPrivateName()
    fieldTypes = self._getFieldTypes()
    if isinstance(value, fieldTypes):
      return setattr(instance, pvtName, value)
    raise TypeException('value', value, *fieldTypes, )

  def _instanceDelete(self, instance: object, **kwargs) -> None:
    """Delete the instance."""
    pvtName = self.getPrivateName()
    if getattr(instance, pvtName, None) is None:
      e = """Attempted to delete attribute '%s' from object of type: '%s', 
      which owns no such attribute!""" % (pvtName, type(instance),)
      raise AttributeError(monoSpace(e))
    setattr(instance, pvtName, DELETED)
