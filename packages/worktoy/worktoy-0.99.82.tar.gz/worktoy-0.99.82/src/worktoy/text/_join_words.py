"""The 'joinWords' function joins a list of words into a single string
with appropriate use of commas and 'and/or'. By default, the final two
given words a separated by 'and', but this can be changed at keyword
argument 'sep'."""
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations


def joinWords(*words: str, **kwargs) -> str:
  """Join a list of words into a single string with appropriate use of
  commas and 'and'."""
  sep = kwargs.get('sep', 'and')
  if len(words) == 1 and isinstance(words[0], list):
    return joinWords(*words[0])
  if not words:
    return ''
  if len(words) == 1:
    if isinstance(words[0], str):
      return words[0]
    raise TypeError
  if len(words) == 2:
    return '%s %s %s' % (words[0], sep, words[1])
  return joinWords(', '.join(words[:-1]), words[-1])
