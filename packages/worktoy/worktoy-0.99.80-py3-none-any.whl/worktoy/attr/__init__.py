"""The 'worktoy.attr' module implements the descriptor protocol."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._wait_for_it import WaitForIt
from ._abstract_descriptor import AbstractDescriptor
from ._abstract_box import AbstractBox
from ._attri_box import AttriBox
from ._flex_box import FlexBox
from ._field import Field
from ._alias import Alias

__all__ = [
    'WaitForIt',
    'AbstractDescriptor',
    'AbstractBox',
    'AttriBox',
    'FlexBox',
    'Field',
    'Alias',
]
