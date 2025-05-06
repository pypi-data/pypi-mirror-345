from __future__ import annotations

import os
from collections import defaultdict

from django.db.models import Field

# dict of (app_label, model_name) -> set of field names
_DECONSTRUCT_MIGRATED_FIELDS: dict[tuple[str, str], set[str]] = defaultdict(set)

"""
Utilities for tracking whether JSONModelFields have had a "compatibility migration" generated. The compatibility 
migration is needed for JSONModel fields that were created before the v1.0 release which added proper support for
deconstructing JSONModel fields for migrations.

Previously, JSONModel classes were imported directly into migrations, which causes problems when the JSONModel class
declaration changes or is moved. The compatibility migration creates a one-time AlterField operation that effectively
replaces the app state version of the field with one that uses correctly deconstructed JSONModel classes. This allows
subsequent changes to JSONModel classes to correctly generate migrations.

The compatibility migration is only generated once per field when running manage.py makemigrations with the environment
variable DJANGO_JSON_MODEL_FIELD_MIGRATION_COMPAT set to a truthy value.
"""


def is_enabled():
    return bool(os.environ.get("DJANGO_JSON_MODEL_FIELD_MIGRATION_COMPAT", False))


def mark_migrated(field: tuple[tuple[str, str], str]) -> None:
    model, field_name = field
    app_label, _ = model
    _DECONSTRUCT_MIGRATED_FIELDS[model].add(field_name)


def is_migrated_field(field: Field) -> bool:
    try:
        model, field = get_migration_entry(field)
        return model in _DECONSTRUCT_MIGRATED_FIELDS and field in _DECONSTRUCT_MIGRATED_FIELDS[model]
    except AttributeError:
        return False


def get_migration_entry(field: Field) -> tuple[[str, str], str]:
    entry = getattr(field, "_deconstruct_compat_migration", None)
    if entry:
        return entry
    return (field.model._meta.app_label or field.model.__module__, field.model._meta.model_name), field.name
