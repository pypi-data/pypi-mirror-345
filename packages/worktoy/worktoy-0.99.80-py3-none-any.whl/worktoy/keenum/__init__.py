"""The 'worktoy.keenum' module provides a baseclass for enumerations. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._auto import auto, NUM
from ._num_hook import NumHook
from ._num_space import NumSpace
from ._meta_num import MetaNum
from ._keenum import KeeNum


__all__ = [
    'auto',
    'NUM',
    'NumHook',
    'NumSpace',
    'MetaNum',
    'KeeNum',
]