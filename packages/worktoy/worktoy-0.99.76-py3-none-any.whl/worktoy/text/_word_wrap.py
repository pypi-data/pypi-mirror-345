"""The 'worktoy.workWrap' function receives an integer defining character
width and any number of strings. The function then returns a list of
strings containing the words from the strings received such that each
entry in the list does not exceed the character width. """
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

from worktoy.text import typeMsg


def _wrap(width: int, *textLines) -> list[str]:
  """The wordwrap function wraps the input text to a specified width."""
  words = []
  for line in textLines:
    words.extend(line.split())
  lines = []
  line = []
  while words:
    word = words.pop(0)
    if len(' '.join([*line, word])) <= width:
      line.append(word)
    else:
      lines.append(' '.join(line))
      line = [word]
  if line:
    lines.append(' '.join(line))
  return lines


def _splitWords(*textLines) -> list[str]:
  """The wordwrap function wraps the input text to a specified width."""
  words = []
  for line in textLines:
    words.extend(line.split())
  return words


def _combineWords(width: int, *words) -> list[str]:
  """The wordwrap function wraps the input text to a specified width."""
  lines = []
  line = []
  words = [*words, ]
  while words:
    word = words.pop(0)
    if len(' '.join([*line, word])) <= width:
      line.append(word)
    else:
      lines.append(' '.join(line))
      line = [word]
  return lines


def wordWrap(width: int, *textLines, **kwargs) -> str:
  """The wordwrap function wraps the input text to a specified width."""
  newLine = kwargs.get('newLine', '<br>').strip().lower()
  if not isinstance(width, int):
    raise TypeError(typeMsg('width', width, int))
  words = []
  for line in textLines:
    if not isinstance(line, str):
      raise TypeError(typeMsg('line', line, str))
    words.extend(line.split())
  lines = []
  line = []
  while words:
    word = words.pop(0)
    if not word:
      continue
    if word.lower() == newLine or len(' '.join([*line, word])) > width:
      lines.append(' '.join(line))
      line = []
      continue
    line.append(word)
  return '\n'.join(lines)
