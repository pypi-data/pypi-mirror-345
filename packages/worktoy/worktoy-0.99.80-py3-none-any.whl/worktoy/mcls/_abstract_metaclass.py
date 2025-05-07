"""AbstractMetaclass provides the baseclass for custom metaclasses. """
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

from ..text import monoSpace, typeMsg
from ..waitaminute import QuestionableSyntax
from . import Base
from . import AbstractNamespace as ASpace

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Self, Any, Callable


class _MetaMetaclass(type):
  """MetaMetaclass is necessary to customize the __str__ method of a
  metaclass"""

  def __str__(cls, ) -> str:
    """Returns the name of the class. """
    return """%s[metaclass=%s]""" % (cls.__name__, cls.__class__.__name__)


class AbstractMetaclass(_MetaMetaclass, metaclass=_MetaMetaclass):
  """The AbstractMetaclass class provides a base class for custom
  metaclasses."""

  @staticmethod
  def _validateNamespace(namespace: dict, **kwargs) -> dict:
    """The _validateNamespace method is invoked to validate the namespace
    object before the class is created. """
    if '__del__' in namespace and '__delete__' not in namespace:
      if not kwargs.get('trustMeBro', False):
        e = """The namespace encountered the '__del__' method! 
          This method has very limited practical use. It has significant 
          potential for unexpected behaviour. If '__del__' were actually
          the intention, the 'worktoy' library requires passing the 
          keyword 'trustMeBro=True' to the class creation."""
        raise SyntaxError(monoSpace(e))
    derpNames = [
        '__get_item__', '__set_item__', '__get_attr__',
        '__set_attr__'
    ]
    realNames = ['__getitem__', '__setitem__', '__getattr__', '__setattr__']
    for derp, name in zip(derpNames, realNames):
      if derp in namespace:
        raise QuestionableSyntax(derp, name, )
    return namespace

  @staticmethod
  def _notifySubclassHook(cls, *bases) -> type:
    """The _notifySubclassHook method is invoked to notify each baseclass
    of the created class of the class creation."""
    for base in bases:
      hook = getattr(base, '__subclasshook__', None)
      if hook is None:
        continue
      hook(cls)
    return cls

  @classmethod
  def __prepare__(mcls, name: str, bases: Base, **kwargs) -> ASpace:
    """The __prepare__ method is invoked before the class is created. This
    implementation ensures that the created class has access to the safe
    __init__ and __init_subclass__ through the BaseObject class in its
    method resolution order."""
    return ASpace(mcls, name, bases, **kwargs)

  def __new__(mcls, name: str, bases: Base, space: ASpace, **kwargs) -> type:
    """The __new__ method is invoked to create the class."""
    namespace = mcls._validateNamespace(space.compile(), **kwargs)
    cls = _MetaMetaclass.__new__(mcls, name, bases, namespace, **kwargs)
    return mcls._notifySubclassHook(cls, *bases)

  def __init__(cls, name: str, bases: Base, space: ASpace, **kwargs) -> None:
    """The __init__ method is invoked to initialize the class."""
    if TYPE_CHECKING:
      assert isinstance(space, ASpace)
      assert isinstance(bases, tuple)
    _MetaMetaclass.__init__(cls, name, bases, space, **kwargs)

  def __call__(cls, *args, **kwargs) -> Any:
    """The __call__ method is invoked when the class is called."""
    classCall = getattr(cls, '__class_call__', None)
    if classCall is None:
      return type.__call__(cls, *args, **kwargs)
    if hasattr(classCall, '__self__'):
      return classCall(*args, **kwargs)
    if callable(classCall):
      return classCall(cls, *args, **kwargs)
    e = typeMsg('classCall', classCall, Callable)
    raise TypeError(e)

  def __instancecheck__(cls, instance) -> bool:
    """This implementation allows the class to customize the instance
    check by implementing a method called __class_instancecheck__."""
    instanceCheck = getattr(cls, '__class_instancecheck__', None)
    if instanceCheck is None:
      return _MetaMetaclass.__instancecheck__(cls, instance)
    if hasattr(instanceCheck, '__self__'):
      return True if instanceCheck(instance) else False
    if callable(instanceCheck):
      return True if instanceCheck(cls, instance) else False
    e = typeMsg('instanceCheck', instanceCheck, Callable)
    raise TypeError(e)

  def __subclasscheck__(cls, subclass) -> bool:
    """This implementation allows the class to customize the subclass
    check by implementing a method called __class_subclasscheck__."""
    subclassCheck = getattr(cls, '__class_subclasscheck__', None)
    if subclassCheck is None:
      return _MetaMetaclass.__subclasscheck__(cls, subclass)
    if hasattr(subclassCheck, '__self__'):
      return True if subclassCheck(subclass) else False
    if callable(subclassCheck):
      return True if subclassCheck(cls, subclass) else False
    e = typeMsg('subclassCheck', subclassCheck, Callable)
    raise TypeError(e)

  def __iter__(cls, ) -> Self:
    """The __iter__ method is invoked to iterate over the class."""
    func = getattr(cls, '__class_iter__', None)
    if func is None:
      func = getattr(_MetaMetaclass, '__iter__')
      return func(cls)
    if hasattr(func, '__self__'):
      return func()
    if callable(func):
      return func(cls)
    e = typeMsg('iter', func, Callable)
    raise TypeError(e)

  def __next__(cls, ) -> Any:
    """The __next__ method is invoked to get the next item in the class."""
    func = getattr(cls, '__class_next__', None)
    if func is None:
      func = getattr(_MetaMetaclass, '__next__')
      return func(cls)
    if hasattr(func, '__self__'):
      return func()
    if callable(func):
      return func(cls)
    e = typeMsg('next', func, Callable)
    raise TypeError(e)
