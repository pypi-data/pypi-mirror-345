"""The 'worktoy.mcls.hooks' package provides the hooks used by the
Namespace system. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._reserved_names import ReservedNames
from ._abstract_hook import AbstractHook
from ._reserved_name_hook import ReservedNameHook
from ._accessor_hook import AccessorHook
from ._overload_hook import OverloadHook
from ._name_hook import NameHook

__all__ = [
    'ReservedNames',
    'AbstractHook',
    'ReservedNameHook',
    'AccessorHook',
    'OverloadHook',
    'NameHook',
]
