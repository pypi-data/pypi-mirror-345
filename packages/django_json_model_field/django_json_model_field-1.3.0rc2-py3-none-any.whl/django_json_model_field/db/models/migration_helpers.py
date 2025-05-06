from __future__ import annotations

from copy import copy
from inspect import isclass
from typing import TypeVar

TOriginal = TypeVar("TOriginal")


def get_migration_import_class_placeholder(original: TOriginal, module: str) -> TOriginal:
    # get a placeholder type to clean up imported module paths in migrations

    original_type = original if isclass(original) else type(original)
    if not original_type.__module__.startswith(module):
        return original

    if not isclass(original):
        placeholder_type = get_migration_import_class_placeholder(type(original), module)
        copied = copy(original)
        copied.__class__ = placeholder_type
        return copied

    attr = f"_{original_type.__module__}.{original_type.__name__}"
    if hasattr(get_migration_import_class_placeholder, attr):
        return getattr(get_migration_import_class_placeholder, attr)

    copied_type = copy(original_type)
    copied_type.__module__ = module
    setattr(get_migration_import_class_placeholder, attr, copied_type)

    return copied_type
