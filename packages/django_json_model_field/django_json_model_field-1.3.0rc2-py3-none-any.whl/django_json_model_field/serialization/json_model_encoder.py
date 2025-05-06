from __future__ import annotations

from json import JSONEncoder
from typing import Any

from django.db import connection, models
from django.db.models import Expression, Func

from django_json_model_field.db.models import BaseJSONModelField, JSONModel
from . import constants
from .types import JSONClassWrapper, JSONModelDict


class JSONModelEncoder(JSONEncoder):
    """
    Custom JSONEncoder that can serialize JSONModel or JSONClassWrapper instances.

    This encoder is used by JSONModelDictField to support using JSONModels in dicts, which is not currently supported
    by JSONModelField.
    """

    def default(self, o: object):
        return collect_data(o)

    def encode(self, o):
        return super().encode(collect_data(o))


_COLLECTABLE_TYPES = (JSONModel, JSONClassWrapper, JSONModelDict, dict)


def collect_data(value: Any) -> Any:
    """
    Recursively normalizes nested JSONModel and JSONClassWrapper instances to dicts to avoid double-serializing nested
    objects.
    """

    # important to check this first so __json_class__ can be added
    if isinstance(value, JSONClassWrapper):
        return _collect_data_from_json_class_wrapper(value)

    if isinstance(value, Func):
        return value

    if isinstance(value, JSONModelDict):
        db_json = value.as_db_json()
        if isinstance(db_json, JSONClassWrapper):
            return _collect_data_from_json_class_wrapper(db_json)
        return _collect_data_from_dict(db_json)

    if isinstance(value, JSONModel):
        return _collect_data_from_json_model(value)

    if isinstance(value, dict):
        return _collect_data_from_dict(value)

    return value


def _collect_data_from_json_model(instance: JSONModel) -> dict[str, Any]:
    field_value: dict[str, Any] = {}

    for field in instance._meta.get_fields():
        # cannot use get_db_prep_value on nested JSONFields because it will double-serialize the nested data
        if isinstance(field, BaseJSONModelField):
            field_value[field.name] = collect_data(
                field._get_db_prep_value_from_model(
                    field.value_from_object(instance),
                    connection=connection
                )
            )
        elif isinstance(field, models.JSONField):  # includes JSONModelDictField
            field_value[field.name] = collect_data(field.value_from_object(instance))
        else:
            # use the prep value for other fields
            field_value[field.name] = field.get_db_prep_value(field.value_from_object(instance), connection=connection)

    model = type(instance)
    field_value[constants.JSON_CLASS_KEY] = f"{model.__module__}.{model.__name__}"
    return field_value


def _collect_data_from_json_class_wrapper(instance: JSONClassWrapper) -> dict[str, Any]:
    model = instance.wraps
    collected = dict(collect_data(instance.data))
    collected[constants.JSON_CLASS_KEY] = f"{model.__module__}.{model.__name__}"
    return collected


def _collect_data_from_dict(
    instance: dict[str, Any] | Expression, *, use_json_class: bool = True
) -> dict[str, Any] | Expression | None:
    if instance is None:
        return None

    if isinstance(instance, (Expression,)):
        # pass through Expression/Func instances (e.g. JSONSet)
        return instance

    collected = {key: collect_data(sub_value) for key, sub_value in instance.items()}

    if use_json_class is False:
        return collected

    model = type(instance)
    if model != dict:
        collected[constants.JSON_CLASS_KEY] = f"{model.__module__}.{model.__name__}"

    return collected
