"""EZSpace provides the namespace for the EZData class. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import DataField, EZHook
from ..mcls import BaseSpace
from ..parse import maybe

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False


class EZSpace(BaseSpace):
  """EZSpace provides the namespace for the EZData class. """

  __data_fields__ = None

  def getDataFields(self) -> list[DataField]:
    """Get the data fields."""
    return maybe(self.__data_fields__, [])

  def addField(self, key: str, type_: type, val: object) -> None:
    """Add a field to the data fields."""
    if self.__data_fields__ is None:
      self.__data_fields__ = []
    dataField = DataField(key, type_, val)
    existing = self.getDataFields()
    self.__data_fields__ = [*existing, dataField]

  ezHook = EZHook()
