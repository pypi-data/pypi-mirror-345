from __future__ import annotations

from inspect import isclass
from typing import Type, overload

from django.apps.registry import Apps
from django.db.models import Field, Model

from django_json_model_field.db.models import (
    BaseJSONModelField,
    ConditionalJSONModelField,
    JSONModel,
    JSONModelDictField,
    JSONModelDictState,
)


@overload
def get_json_model_class(
    model: Type[Model] | Type[JSONModel],
    field_name: str,
    /,
    *,
    selector_value: str = None,
) -> Type[JSONModel]:
    ...


@overload
def get_json_model_class(
    apps: Apps,
    app_label: str,
    model_name: str,
    field_name: str,
    /,
    *,
    selector_value: str = None,
) -> Type[JSONModel]:
    ...


def get_json_model_class(
    apps_or_model: Apps | Type[Model] | Type[JSONModel],
    model_or_app_label_or_field_name: Type[Model] | Type[JSONModel] | str,
    field_or_model_name: str = None,
    field_name: str = None,
    /,
    *,
    selector_value: str = None,
) -> Type[JSONModel]:
    """
    Helper for loading JSONModel classes in migrations for use in RunPython operations.

    Usage:

        from django_json_model_field import migration_helpers


        def forwards_func(apps, schema_editor):
            # using a model class
            HostClass = apps.get_model("my_app", "HostClass")
            JSONModelClass = migration_helpers.get_json_model_class(apps, HostClass, "json_model_field")

            # or, using app_label and model_name
            JSONModelClass = get_json_model_class(apps, "my_app", "HostClass", "json_model_field")

            json_model_data = JSONModelClass(...)
            obj = HostClass.objects.create(json_model_field=json_model_data)

            # get_json_model_class can also be used with nested JSONModels
            NestedJSONModelClass = get_json_model_class(apps, JSONModelClass, "nested_json_model_field")
            nested_json_model_data = NestedJSONModelClass(...)

            obj.json_model_field.nested_json_model_field = nested_json_model_data
            obj.save()

    """

    model, field, selector_value = _get_field_from_args(
        apps_or_model=apps_or_model,
        model_or_app_label_or_field_name=model_or_app_label_or_field_name,
        field_or_model_name=field_or_model_name,
        field_name=field_name,
        selector_value=selector_value,
    )

    if isinstance(field, JSONModelDictField):
        raise TypeError(f"{field_name} is a JSONModelDictField, use get_json_model_dict_class instead")

    if isinstance(field, ConditionalJSONModelField):
        if selector_value is None:
            raise ValueError(f"{field_name} is a ConditionalJSONModelField and requires a selector_value")
        return field.get_json_model_class({field.selector_field_name: selector_value})

    if selector_value is not None:
        raise ValueError(f"{field_name} is not a ConditionalJSONModelField and does not support a selector_value")

    return field.get_json_model_class({})


@overload
def get_json_model_dict_class(
    model: Type[Model] | Type[JSONModel],
    field_name: str,
    /,
) -> tuple[Type[dict], Type[JSONModel]]:
    ...


@overload
def get_json_model_dict_class(
    apps: Apps,
    app_label: str,
    model_name: str,
    field_name: str,
    /,
) -> tuple[Type[dict], Type[JSONModel]]:
    ...


def get_json_model_dict_class(
    apps_or_model: Apps | Type[Model] | Type[JSONModel],
    model_or_app_label_or_field_name: Type[Model] | Type[JSONModel] | str,
    field_or_model_name: str = None,
    field_name: str = None,
    /,
) -> tuple[Type[dict[str, JSONModel]], Type[JSONModel]]:

    model, field, _ = _get_field_from_args(
        apps_or_model=apps_or_model,
        model_or_app_label_or_field_name=model_or_app_label_or_field_name,
        field_or_model_name=field_or_model_name,
        field_name=field_name,
    )

    if not isinstance(field, JSONModelDictField):
        raise TypeError(f"{field_name} is a not JSONModelDictField, use get_json_model_class instead")

    value_class = JSONModelDictState.get_value_class(field.json_dict_model)
    return field.json_dict_model, value_class


def _get_field_from_args(
    *,
    apps_or_model: Apps | Type[Model] | Type[JSONModel],
    model_or_app_label_or_field_name: Type[Model] | Type[JSONModel] | str,
    field_or_model_name: str | None,
    field_name: str | None,
    selector_value: str = None
) -> tuple[Type[Model] | Type[JSONModel], BaseJSONModelField | JSONModelDictField, str | None]:
    if isclass(apps_or_model):
        if not issubclass(apps_or_model, (Model, JSONModel)):
            raise TypeError("model must be a Django Model or JSONModel class")
        model = apps_or_model
        field_name = model_or_app_label_or_field_name
    elif isclass(model_or_app_label_or_field_name):
        if not issubclass(model_or_app_label_or_field_name, (Model, JSONModel)):
            raise TypeError("model must be a Django Model or JSONModel class")
        model = model_or_app_label_or_field_name
        field_name = field_or_model_name
    else:
        if not isinstance(apps_or_model, Apps):
            raise TypeError("apps must be an Apps instance")
        if not isinstance(model_or_app_label_or_field_name, str):
            raise TypeError("app_label must be a string")
        if not isinstance(field_or_model_name, str):
            raise TypeError("model_name must be a string")
        apps = apps_or_model
        app_label = model_or_app_label_or_field_name
        model_name = field_or_model_name
        model = apps.get_model(app_label, model_name)

    if not isinstance(field_name, str):
        raise TypeError("field_name must be a string")

    if selector_value is not None and not isinstance(selector_value, str):
        raise TypeError("selector_value must be a string")

    field = _get_field(model, field_name)

    if not isinstance(field, (BaseJSONModelField, JSONModelDictField)):
        raise TypeError(f"{field_name} is not a JSONModel field")

    return model, field, selector_value


def _get_field(model: Type[Model] | Type[JSONModel], field_name: str) -> Field:
    return next(field for field in model._meta.get_fields() if field.name == field_name)
