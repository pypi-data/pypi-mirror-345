"""The stringList function receives a single string describing a list of
items and returns a list of strings each representing an item."""
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

from . import monoSpace


def stringList(items: str, **kwargs) -> list[str]:
  """The stringList function receives a single string describing a list of
  items and returns a list of strings each representing an item."""
  if not items:
    return []
  separator = kwargs.get('separator', ',')
  items = monoSpace(items).split(separator)
  items = [item.strip() for item in items]
  return items
