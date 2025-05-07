"""IllegalInstantiationError is a custom exception raised to indicate than
an attempt was made to instantiate a class under illegal conditions."""
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
  from typing import Never


class IllegalInstantiationError(TypeError):
  """IllegalInstantiationError is a custom exception raised to indicate than
  an attempt was made to instantiate a class under illegal conditions."""

  cls = _Attribute()

  def __init__(self, cls_: type) -> None:
    """Initialize the IllegalInstantiationError with the class."""
    self.cls = cls_
    infoSpec = """Illegal instantiation of class '%s'"""
    info = infoSpec % cls_.__name__
    TypeError.__init__(self, info)
