"""AbstractNamespace class provides a base class for custom namespace
objects used in custom metaclasses."""
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

from ..text import typeMsg, monoSpace
from ..waitaminute import MissingVariable, HookException
from . import Base, Types, Spaces
from .hooks import AbstractHook

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Self


class AbstractNamespace(dict):
  """AbstractNamespace class provides a base class for custom namespace
  objects used in custom metaclasses."""

  #  Reserved private names
  __meta_class__ = None
  __class_name__ = None
  __base_classes__ = None
  __key_args__ = None
  __owner_hooks_list_name__ = '__hook_objects__'

  @classmethod
  def getHookListName(cls, ) -> str:
    """Getter-function for the name of the hook list. """
    if TYPE_CHECKING:
      assert isinstance(cls, dict)
    return cls.__owner_hooks_list_name__

  @classmethod
  def addHook(cls, hook: AbstractHook) -> None:
    """Adds a hook to the list of hooks. """
    if TYPE_CHECKING:
      assert isinstance(cls, dict)
    if not isinstance(hook, AbstractHook):
      raise TypeError(typeMsg('hook', hook, AbstractHook))
    existingHooks = getattr(cls, cls.getHookListName(), [])
    setattr(cls, cls.getHookListName(), [*existingHooks, hook])

  def getHooks(self, owner: type = None) -> list[AbstractHook]:
    """Getter-function for the AbstractHook classes. """
    pvtName = self.getHookListName()
    cls = type(self)
    hooks = getattr(cls, pvtName, [])
    out = []
    for hook in hooks:
      out.append(hook.__get__(self, cls))
    return out

  def __init__(self, mcls: type, name: str, bases: Base, **kwargs) -> None:
    self.__meta_class__ = mcls
    self.__class_name__ = name
    if len(bases) > 1:
      e = """The 'worktoy' package does not support multiple inheritance!"""
      raise TypeError(monoSpace(e))
    self.__base_class__ = [*bases, object][0]
    self.__key_args__ = kwargs or {}

  def getMetaclass(self, ) -> type:
    """Returns the metaclass."""
    return self.__meta_class__

  def getClassName(self, ) -> str:
    """Returns the name of the class."""
    return self.__class_name__

  def getBaseClass(self, ) -> type:
    """Returns the base class."""
    return self.__base_class__

  def getKwargs(self, ) -> dict:
    """Returns the keyword arguments passed to the class."""
    return {**self.__key_args__, **dict()}

  def getMRO(self, ) -> Types:
    """Returns the method resolution order of the class."""
    return self.getBaseClass().__mro__

  def getMROSpace(self, ) -> Spaces:
    """Returns the namespace objects of the baseclasses. """
    cls = type(self)
    mcls = self.getMetaclass()
    out = []
    for base in self.getMRO():
      if isinstance(base, mcls):
        out.append(getattr(base, '__namespace__', ))
    return (*out,)

  def getPrimeBase(self, ) -> type:
    """Returns the prime baseclass of the class under creation. """
    baseMRO = [*self.getMRO(), ]
    mcls = self.getMetaclass()
    while baseMRO:
      base = baseMRO.pop()
      if base is object:
        continue
      if isinstance(base, mcls):
        return base
    raise MissingVariable('base', mcls)

  def getPrimeSpace(self, ) -> Self:
    """Getter-function for the namespace object of the prime baseclass of
    the class under creation. The prime baseclass is the baseclass whose
    baseclasses are not derived from this metaclass. """
    try:
      primeBase = self.getPrimeBase()
    except MissingVariable as missingVariable:
      return self
    cls = type(self)
    primeSpace = getattr(primeBase, '__namespace__', None)
    if isinstance(primeSpace, cls):
      return primeSpace
    raise TypeError(typeMsg('primeSpace', primeSpace, cls))

  def isPrime(self, ) -> bool:
    """Returns True if the class is the prime baseclass of the class
    under creation. """
    return True if self.getPrimeSpace() is self else False

  def getParent(self, ) -> type:
    """Getter-function for the parent baseclass of the class under
    creation. """
    if self.isPrime():
      raise MissingVariable('parent', type(self))
    return self.getBaseClass()

  def getParentSpace(self, ) -> Self:
    """Getter-function for the namespace object of the parent baseclass of
    the class under creation. """
    cls = type(self)
    try:
      parentBase = self.getParent()
    except MissingVariable as missingVariable:
      return self
    parentSpace = getattr(parentBase, '__namespace__', None)
    if parentSpace is None:
      raise MissingVariable('__namespace__', cls)
    if isinstance(parentSpace, cls):
      return parentSpace
    raise TypeError(typeMsg('parentSpace', parentSpace, cls))

  def __getitem__(self, key: str) -> Any:
    """Returns the value of the key."""
    try:
      val = dict.__getitem__(self, key)
    except KeyError as keyError:
      val = keyError
    for hook in self.getHooks():
      if not isinstance(hook, AbstractHook):
        raise TypeError(typeMsg('hook', hook, AbstractHook))
      try:
        hook.getItemHook(self, key, val)
      except Exception as exception:
        print('hook exception: %s' % type(hook).__name__)
        print('  key: %s' % key)
        print('  value: %s' % val)
        print('  %s!\n%s' % (type(exception).__name__, str(exception)))
        raise HookException(exception, self, key, val, hook)
    if isinstance(val, KeyError):
      raise val
    return val

  def __setitem__(self, key: str, val: object) -> None:
    """Sets the value of the key."""
    try:
      oldVal = dict.__getitem__(self, key)
    except KeyError:
      oldVal = None
    for hook in self.getHooks():
      if TYPE_CHECKING:
        assert isinstance(hook, AbstractHook)
      if hook.setItemHook(self, key, val, oldVal):
        break
    else:
      dict.__setitem__(self, key, val)

  def preCompile(self, ) -> dict:
    """The return value from this method is passed to the compile method.
    Subclasses can implement this method to provide special objects at
    particular names in the namespace. By default, an empty dictionary is
    returned. """
    namespace = dict()
    for hook in self.getHooks():
      if TYPE_CHECKING:
        assert isinstance(hook, AbstractHook)
      namespace = hook.preCompileHook(self, namespace)
    return namespace

  def compile(self, ) -> dict:
    """This method is responsible for building the final namespace object.
    Subclasses may reimplement preCompile or postCompile as needed,
    but must not reimplement this method."""
    namespace = self.preCompile()
    for (key, val) in dict.items(self, ):
      namespace[key] = val
    namespace['__metaclass__'] = self.getMetaclass()
    namespace['__namespace__'] = self
    return self.postCompile(namespace)

  def postCompile(self, namespace: dict) -> dict:
    """The object returned from this method is passed to the __new__
    method in the owning metaclass. By default, this method returns dict
    object created by the compile method after performing certain
    validations. Subclasses can implement this method to provide further
    processing of the compiled object. """
    for hook in self.getHooks():
      if TYPE_CHECKING:
        assert isinstance(hook, AbstractHook)
      namespace = hook.postCompileHook(self, namespace)
    if '__metaclass__' not in namespace:
      raise MissingVariable('__metaclass__', self.getMetaclass())
    if '__namespace__' not in namespace:
      raise MissingVariable('__namespace__', type(self))
    return namespace

  def __str__(self, ) -> str:
    """Returns the string representation of the namespace object."""
    spaceName = type(self).__name__
    clsName = self.getClassName()
    baseName = self.getBaseClass().__name__
    mclsName = self.getMetaclass().__name__
    info = """Namespace object of type: '%s' created by the '__prepare__' 
    method on metaclass: '%s' with base: %s to create class: '%s'."""
    return monoSpace(info % (spaceName, mclsName, baseName, clsName))

  def __repr__(self, ) -> str:
    """Returns the string representation of the namespace object."""
    spaceName = type(self).__name__
    clsName = self.getClassName()
    mclsName = self.getMetaclass().__name__
    baseName = self.getBaseClass().__name__
    mclsName = self.getMetaclass().__name__
    args = """%s, %s, (%s,)""" % (mclsName, clsName, baseName)
    kwargs = [(k, v) for (k, v) in self.getKwargs().items()]
    kwargStr = ', '.join(['%s=%s' % (k, str(v)) for (k, v) in kwargs])
    if kwargStr:
      kwargStr = ', %s' % kwargStr
    return """%s(%s%s)""" % (spaceName, args, kwargStr)
