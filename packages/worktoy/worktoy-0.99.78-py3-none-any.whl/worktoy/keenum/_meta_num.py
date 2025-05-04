"""MetaNum provides the metaclass for the enumerations."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ..attr import Field
from ..mcls import AbstractMetaclass, Base
from . import NumSpace as NSpace
from ..text import monoSpace, typeMsg
from ..waitaminute import UnrecognizedMember

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Self, Any, Never


class MetaNum(AbstractMetaclass):
  """MetaNum provides the metaclass for the enumerations."""

  __iter_contents__ = None

  memberType = Field()
  NULL = Field()

  @memberType.GET
  def _getMemberType(cls) -> type:
    """Get the member type."""
    type_ = getattr(cls, '__member_type__', None)
    if type_ is None:
      raise AttributeError('Member type not set!')
    if isinstance(type_, type):
      return type_
    raise TypeError(typeMsg('__member_type__', type_, type))

  @NULL.GET
  def _getNULL(cls, ) -> Any:
    """Get the NULL value."""
    nullMember = getattr(cls, '__null_member__', None)
    if nullMember is None:
      e = """KeeNum class: '%s' does not have a NULL member!"""
      info = monoSpace(e % cls.__name__)
      raise AttributeError(info)
    return nullMember

  @classmethod
  def __prepare__(mcls, name: str, bases: Base, **kwargs) -> NSpace:
    """Prepare the class namespace."""
    return NSpace(mcls, name, bases, **kwargs)

  def __new__(mcls, name: str, bases: Base, space: NSpace, **kwargs) -> type:
    """Create a new class."""
    return AbstractMetaclass.__new__(mcls, name, bases, space, **kwargs)

  def __init__(cls, name: str, bases: Base, space: NSpace, **kwargs) -> None:
    """The __init__ method is invoked to initialize the class."""
    AbstractMetaclass.__init__(cls, name, bases, space, **kwargs)
    memberType = None
    memberObjects = []
    for i, member in enumerate(space.getMemberNums()):
      if memberType is None:
        memberType = type(member.val)
      if not isinstance(member.val, memberType):
        e = """Inconsistent types of inner values in the enumeration! 
        Expected: type: '%s', but received object: '%s' of type: '%s'!"""
        expType = memberType.__name__
        objStr = str(member.val)
        actType = type(member.val).__name__
        info = monoSpace(e % (expType, objStr, actType))
        raise TypeError(info)
      existing = getattr(cls, '__member_objects__', )
      newMember = cls(member.key, member.val, i)
      setattr(cls, member.key, newMember)
      memberObjects.append(newMember)
      if member.key == 'NULL':
        if getattr(cls, '__null_member__', None) is not None:
          e = """KeeNum class: '%s' has multiple NULL members!"""
          info = monoSpace(e % cls.__name__)
          raise AttributeError(info)
        if member.val:
          e = """The NULL member must evaluate to False, but received: '%s'
          which evaluates to True!"""
          raise ValueError(monoSpace(e % member.val))
        setattr(cls, '__null_member__', newMember)
    else:
      setattr(cls, '__allow_instantiation__', False)
      setattr(cls, '__member_type__', memberType)
      setattr(cls, '__member_objects__', memberObjects)

  def __call__(cls, *args: Any, **kwargs: Any) -> Self:
    """The __call__ method is invoked to create an instance of the
    class."""
    if getattr(cls, '__allow_instantiation__', False):
      return AbstractMetaclass.__call__(cls, *args, **kwargs)
    return cls._resolveMember(*args, **kwargs)

  def _resolveMember(cls, *args, **kwargs) -> Any:
    """The _resolveMember method is invoked to resolve the member
    variables."""
    if len(args) != 1:
      e = """Cannot resolve member with more than one argument!"""
      raise ValueError(monoSpace(e))
    identifier = args[0]
    if isinstance(identifier, cls):
      return identifier
    if isinstance(identifier, int):
      try:
        return cls._resolveIndex(identifier)
      except IndexError as indexError:
        raise UnrecognizedMember(cls, identifier) from indexError
    if isinstance(identifier, str):
      try:
        return cls._resolveKey(identifier)
      except KeyError as keyError:
        raise UnrecognizedMember(cls, identifier) from keyError
    if isinstance(identifier, cls.memberType):
      for self in cls:
        if identifier == self.val:
          return self
    raise UnrecognizedMember(cls, identifier)

  def _resolveIndex(cls, index: int) -> Any:
    """The _resolveIndex method is invoked to resolve the index of the
    member variables."""
    while index < 0:
      index += len(cls)
    if index >= len(cls):
      e = """Index out of range!"""
      raise IndexError(monoSpace(e))
    for self in cls:
      if self.index == index:
        return self

  def _resolveKey(cls, key: str) -> Any:
    """The _resolveKey method is invoked to resolve the key of the member
    variables."""
    for self in cls:
      if self.key.lower() == key.lower():
        return self
    e = """Key not found!"""
    raise KeyError(monoSpace(e))

  def __iter__(cls, ) -> Self:
    """The __iter__ method is invoked to iterate over the class."""
    cls.__iter_contents__ = getattr(cls, '__member_objects__', )
    return cls

  def __next__(cls) -> Any:
    """The __next__ method is invoked to get the next item in the
    iteration."""
    if cls.__iter_contents__:
      return cls.__iter_contents__.pop(0)
    raise StopIteration

  def __len__(cls, ) -> int:
    """The __len__ method is invoked to get the length of the class."""
    return len(getattr(cls, '__member_objects__', []))

  def __bool__(cls, ) -> bool:
    """The __bool__ method is invoked to get the boolean value of the
    class."""
    return True if getattr(cls, '__member_objects__', []) else False

  def __contains__(cls, item: Any) -> bool:
    """The __contains__ method is invoked to check if the class contains
    the item."""
    if item in getattr(cls, '__member_objects__', []):
      return True
    if item in cls.memberType:
      for self in cls:
        if self == item:
          return True
    return False

  def __getitem__(cls, key: str) -> Any:
    """The __getitem__ method is invoked to get the item in the class."""
    return cls._resolveKey(key)

  def __setitem__(cls, *_) -> Never:
    """Illegal operation"""
    info = """KeeNum classes are immutable, but an attempt was 
    made to set an item on KeeNum class: :'%s'!""" % cls.__name__
    raise TypeError(monoSpace(info))

  def __delitem__(cls, *_) -> Never:
    """Illegal operation"""
    info = """KeeNum classes are immutable, but an attempt was 
    made to delete an item on KeeNum class: :'%s'!""" % cls.__name__
    raise TypeError(monoSpace(info))

  def __getattr__(cls, key: str) -> Any:
    """The __getattr__ method is invoked to get the attribute of the
    class."""
    try:
      return cls._resolveKey(key)
    except KeyError as keyError:
      try:
        return object.__getattribute__(cls, key)
      except AttributeError as attributeError:
        raise attributeError from keyError
