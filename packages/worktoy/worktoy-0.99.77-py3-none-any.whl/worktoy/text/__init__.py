"""The 'worktoy.text' package provides functions related to text.

- 'monoSpace': Replaces all continuous whitespace with a single space.
- 'typeMsg': Creates a common type error message
- 'joinWords': Joins words with a specified separator.
- 'stringList': Creates a list of strings from a given string.
- 'wordWrap': Wraps text to a specified width.
- 'funcReport': Generates a report of the function's arguments and their
  types.



"""
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

from ._mono_space import monoSpace
from ._join_words import joinWords
from ._type_msg import typeMsg
from ._string_list import stringList
from ._word_wrap import wordWrap
from ._func_report import funcReport

__all__ = [
    'monoSpace',
    'typeMsg',
    'joinWords',
    'stringList',
    'wordWrap',
    'funcReport',
]
