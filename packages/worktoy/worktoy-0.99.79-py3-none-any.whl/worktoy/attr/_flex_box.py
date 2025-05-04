"""FlexBox provides a descriptor with lazy instantiation of the underlying
object and with type-flexibility. This means that the __set__ method will
attempt to cast to the field type, if the value is not of the field type."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..static import DELETED
from ..text import typeMsg, monoSpace
from ..waitaminute import MissingVariable, DeletedAttributeException
from worktoy.attr import AbstractBox

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Self


class FlexBox(AbstractBox):
  """FlexBox provides a descriptor with lazy instantiation of the underlying
  object and with type-flexibility. This means that the __set__ method will
  attempt to cast to the field type, if the value is not of the field
  type."""

  def __class_getitem__(cls, fieldType: type) -> Self:
    """Get the field type."""
    self = cls()
    self._setFieldType(fieldType)
    return self

  def __call__(self, *args, **kwargs) -> Self:
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

  def _createSetObject(self, instance: object, *args, **kwargs) -> Any:
    """Create the object."""
    fieldTypes = self._getFieldTypes()
    exception = None
    for cls in fieldTypes:
      try:
        newObject = cls(*args, )
      except TypeError as typeError:
        if exception is None:
          exception = typeError
      else:
        return newObject
    else:
      if args:
        if isinstance(args[0], (tuple, list)):
          if kwargs.get('_recursion', False):
            raise RecursionError
          return self._createSetObject(instance, *args[0], _recursion=True)
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
      fieldType = self._getFieldTypes()
      raise MissingVariable(pvtName, fieldType)
    return existingObject

  def _instanceGet(self, instance: Any, **kwargs) -> Any:
    """Get the instance."""
    pvtName = self.getPrivateName()
    fieldTypes = self._getFieldTypes()
    try:
      existingObject = self._getExistingObject(instance)
    except MissingVariable:
      if kwargs.get('_recursion', False):
        raise RecursionError
      newObject = self._createInitObject(instance, )
      setattr(instance, pvtName, newObject)
      return self._instanceGet(instance, _recursion=True, )
    else:
      return existingObject

  def _instanceSet(self, instance: Any, value, *args, **kwargs) -> None:
    """Set the instance."""
    pvtName = self.getPrivateName()
    fieldTypes = self._getFieldTypes()
    if isinstance(value, fieldTypes):
      return setattr(instance, pvtName, value)
    if kwargs.get('_recursion', False):
      raise RecursionError
    newObject = self._createSetObject(instance, value, )
    return self._instanceSet(instance, newObject, _recursion=True, )

  def _instanceDelete(self, instance: object, **kwargs) -> None:
    """Delete the instance."""
    pvtName = self.getPrivateName()
    if getattr(instance, pvtName, None) is None:
      e = """Attempted to delete attribute '%s' from object of type: '%s', 
      which owns no such attribute!""" % (pvtName, type(instance),)
      raise AttributeError(monoSpace(e))
    setattr(instance, pvtName, DELETED)
