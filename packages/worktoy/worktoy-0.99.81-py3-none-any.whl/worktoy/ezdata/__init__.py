"""The 'worktoy.ezdata' leverages the 'worktoy' library to provide a
dataclass. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._data_field import DataField
from ._ez_hook import EZHook
from ._ez_space import EZSpace
from ._ez_meta import EZMeta
from ._ez_data import EZData

__all__ = [
    'DataField',
    'EZHook',
    'EZSpace',
    'EZMeta',
    'EZData',
]
