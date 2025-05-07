"""FidGen provides filename generator. Given a format specification and a
directory, it returns the next available filename of the given format."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import os

from worktoy.attr import WaitForIt, Field
from worktoy.mcls import BaseObject
from worktoy.parse import maybe
from worktoy.static import overload
from worktoy.text import stringList
from worktoy.waitaminute import TypeException, MissingVariable
from worktoy.work_io import validateExistingDirectory

try:
  from typing import TYPE_CHECKING
except ImportError:
  try:
    from typing_extensions import TYPE_CHECKING
  except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
  from typing import Any, Optional


class FidGen(BaseObject):
  """
  FidGen provides filename generator. Given a format specification and a
  directory, it returns the next available filename of the given format.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  __field_name__ = None
  __field_owner__ = None
  __current_instance__ = None
  __current_owner__ = None
  fieldName = Field()
  fieldOwner = Field()
  currentInstance = Field()
  currentOwner = Field()

  def __set_name__(self, owner: type, name: str) -> None:
    """Set the name of the field."""
    self.__field_name__ = name
    self.__field_owner__ = owner

  def __get__(self, instance: Any, owner: type) -> Any:
    """Get the value of the field."""
    self.currentInstance = instance
    self.currentOwner = owner
    return self

  def __set__(self, instance: Any, value: Any) -> None:
    """Set the value of the field."""
    self.currentInstance = instance
    self.baseName = value

  def __delete__(self, instance: Any) -> None:
    """Delete the field."""
    delattr(instance, self.fieldName)

  #  Fallback variables
  __fallback_extension__ = 'json'
  __fallback_directory__ = WaitForIt(os.getcwd)

  #  Private variables
  __base_name__ = None
  __file_extension__ = None
  __file_directory__ = None

  #  Public variables
  fileExtension = Field()
  fileDirectory = Field()
  baseName = Field()

  #  Virtual variables
  filePath = Field()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  @fieldName.GET
  def _getFieldName(self) -> str:
    """Get the field name."""
    if self.__field_name__ is None:
      raise MissingVariable('__field_name__', str)
    return self.__field_name__

  @fieldOwner.GET
  def _getFieldOwner(self) -> type:
    """Get the field owner."""
    if self.__field_owner__ is None:
      raise MissingVariable('__field_owner__', type)
    return self.__field_owner__

  @currentInstance.GET
  def _getCurrentInstance(self) -> object:
    """Get the current instance."""
    return self.__current_instance__

  @currentOwner.GET
  def _getCurrentOwner(self) -> type:
    """Get the current owner."""
    return maybe(self.__current_owner__, self.__field_owner__, )

  @baseName.GET
  def _getFileName(self, ) -> str:
    """Get the name of the file."""
    return maybe(self.__base_name__, self.currentOwner.__name__)

  @fileExtension.GET
  def _getFileExtension(self, **kwargs) -> str:
    """Get the file extension."""
    return maybe(self.__file_extension__, self.__fallback_extension__, )

  @fileDirectory.GET
  def _getFileDirectory(self, **kwargs) -> str:
    """Get the file directory."""
    return maybe(self.__file_directory__, self.__fallback_directory__, )

  @filePath.GET
  def _getFilePath(self, **kwargs) -> str:
    """Getter-function for the file path. """
    n = kwargs.get('_n', 0)
    formatSpec = """%s_%03d"""
    fid = formatSpec % (self.baseName, n,)
    for item in os.listdir(self.fileDirectory):
      if item.startswith(fid):
        return self._getFilePath(_n=n + 1, )
    fidExt = """%s.%s""" % (fid, self.fileExtension)
    out = os.path.join(self.fileDirectory, fidExt)
    return str(out)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Setter methods
  @currentInstance.SET
  def _setCurrentInstance(self, instance: object) -> None:
    """Set the current instance."""
    if instance is not self.__current_instance__:
      self.__current_instance__ = instance

  @currentOwner.SET
  def _setCurrentOwner(self, owner: type) -> None:
    """Set the current owner."""
    if owner is not self.__current_owner__:
      self.__current_owner__ = owner

  @baseName.SET
  def _setFileName(self, newName: str) -> None:
    """Set the name of the file."""
    if self.__base_name__ == newName:
      return
    if not isinstance(newName, str):
      raise TypeException('__name__', newName, str)
    if not newName:
      raise ValueError('__name__ must be a non-empty string')
    self.__base_name__ = newName

  @fileExtension.SET
  def _setFileExtension(self, value: str) -> None:
    """Set the file extension."""
    if not isinstance(value, str):
      raise TypeException('__file_extension__', value, str)
    if not value:
      raise ValueError('__file_extension__ must be a non-empty string')
    self.__file_extension__ = value

  @fileDirectory.SET
  def _setFileDirectory(self, value: str, **kwargs) -> None:
    """Set the file directory."""
    if not isinstance(value, str):
      raise TypeException('__file_directory__', value, str)
    if not value:
      raise ValueError('__file_directory__ must be a non-empty string')
    try:
      validateExistingDirectory(value)
    except FileNotFoundError as e:
      if kwargs.get('_recursion', False):
        raise RecursionError from e
      os.makedirs(value, exist_ok=True)
      return self._setFileDirectory(value, _recursion=True)
    else:
      self.__file_directory__ = value
    finally:
      pass  # NOQA

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @staticmethod
  def _findDirectory(*args) -> Optional[str]:
    """Finds the directory in positional arguments. """
    for arg in args:
      if isinstance(arg, str):
        if os.path.isabs(arg):
          return arg
    return None  # pycharm, please!

  @staticmethod
  def _getCommonExtensions() -> list[str]:
    """Returns a list of common file extensions."""
    return stringList(
        """json, txt, csv, xml, html, pdf, doc, csv, py, 
        mkv, mp4, mp3, wav, jpg, png, gif, zip, tar, gz, bz2"""
    )

  @classmethod
  def _findFileExtension(cls, *args) -> Optional[str]:
    """Finds the file extension in positional arguments. """
    commonExtensions = cls._getCommonExtensions()
    for arg in args:
      if isinstance(arg, str):
        if str.startswith(arg, '*.'):
          return arg[2:]
        if arg in commonExtensions:
          return arg
    return None  # pycharm, please!

  @overload(str)
  def __init__(self, fileName: str, **kwargs) -> None:
    """Initialize the FidGen object."""
    self.__base_name__ = fileName
    self.__init__(**kwargs)

  @overload(str, str, str)
  @overload(str, str)
  def __init__(self, *args, **kwargs) -> None:
    argDir = self._findDirectory(*args)
    argExt = self._findFileExtension(*args)
    for arg in args:
      if arg in [argDir, argExt]:
        continue
      self.baseName = arg
      break
    if argDir is not None:
      self.fileDirectory = argDir
    if argExt is not None:
      self.fileExtension = argExt
    self.__init__(**kwargs)

  @overload()  # kwargs
  def __init__(self, **kwargs) -> None:
    """Initialize the FidGen object."""
    nameKeys = stringList("""name, file, fileName, filename, file_name""")
    extKeys = stringList("""ext, extension, file_extension""")
    dirKeys = stringList("""dir, directory, file_directory""")
    KEYS = [nameKeys, extKeys, dirKeys]
    NAMES = stringList("""name, ext, dirPath""")
    TYPES = dict(name=str, ext=str, dirPath=str)
    VALUES = dict()
    for (keys, (name, type_)) in zip(KEYS, TYPES.items()):
      for key in keys:
        if key in kwargs:
          value = kwargs[key]
          if isinstance(value, type_):
            VALUES[name] = value
            break
          raise TypeException(key, value, type_)
