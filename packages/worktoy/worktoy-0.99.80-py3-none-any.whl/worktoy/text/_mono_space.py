"""The monoSpace function receives a string and returns it with all
consecutive white spaces replaced by a single space. Only characters that
are recognized as digits, letters or punctuation are included. Include in
the string the following tags to explicitly set new lines or indentations:
  '<br>' for new lines
  '<tab>' for one tab containing the number of spaces defined at the
  keyword argument 'tab', by default 2."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from string import digits, punctuation, ascii_letters


def _getPrintables() -> str:
  """Return a list of printable characters."""
  return '%s %s %s' % (digits, punctuation, ascii_letters)


def _removeNonPrintableCharacters(word: str) -> str:
  """Remove all non-printable characters from the string."""
  printables = _getPrintables()
  return ''.join([c if c in printables else ' ' for c in word])


def monoSpace(words: str, **kwargs) -> str:
  """The monoSpace function receives a string and returns it with all
  consecutive white spaces replaced by a single space. Only characters that
  are recognized as digits, letters or punctuation are included. Include in
  the string the following tags to explicitly set new lines or indentations:
    '<br>' for new lines
    '<n: int>' for indentations of 'n' spaces.
    '<tab>' for one tab containing the number of spaces defined at the
    keyword argument 'tab', by default 2."""
  tabSymbol = kwargs.get('tab', '<tab>')
  newLineSymbol = kwargs.get('newLine', '<br>')
  words = _removeNonPrintableCharacters(words)
  lines = words.split(newLineSymbol)
  lines = [' '.join(line.split()) for line in lines]
  lines = [line.replace(' %s' % tabSymbol, tabSymbol) for line in lines]
  lines = [line.replace('%s ' % tabSymbol, tabSymbol) for line in lines]
  lines = [line.replace(tabSymbol, ' ' * 2) for line in lines]
  return '\n'.join(lines)
