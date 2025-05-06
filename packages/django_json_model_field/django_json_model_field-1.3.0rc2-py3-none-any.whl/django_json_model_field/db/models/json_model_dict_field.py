from __future__ import annotations

from typing import Any, Callable, Type

from django.core import checks
from django.db.models import JSONField

from django_json_model_field.serialization import JSONModelDecoder, JSONModelEncoder
from django_json_model_field.serialization.json_model_encoder import _collect_data_from_dict
from django_json_model_field.serialization.types import JSONModelDict
from .json_model_dict_state import JSONModelDictState, reconstruct
from .migration_compat_field_mixin import MigrationCompatFieldMixin


class JSONModelDictField(MigrationCompatFieldMixin, JSONField):
    """
    A JSONField implementation that supports storing JSONModel instances in a dict.

    The django_json_model library doesn't support dicts yet. This field adds basic support for allowing JSONModels to
    be used for serializing and deserializing, but does not provide any support for Django forms or admin.

    json_dict_model must be a dict, a dict subclass, or a class that implements as_db_json(self), which returns a dict
    or JSONClassWrapper instance. All dict values must be JSON serializable, or instances of JSONModel or
    JSONClassWrapper.

    dict data is passed to json_dict_model as kwargs.
    """

    # JSONModelDictField works by using customized JSON encoder and decoders. The encoder stores the class path for
    # serialized JSONModel and JSONClassWrapper instances, and the decoder uses this information to deserialize the
    # data. Since JSONEncoder does not provide a hook for customizing serialization of dictionaries, data from dict
    # subclasses are wrapped in a JSONClassWrapper instance, which forces the encoder's default(obj) method to be
    # called, allowing it to store the class path.
    #
    # Example:
    #    Saving:
    #       my_model.custom_dict = CustomDictInstance({"key": JSONModelInstance(name="value")})
    #       my_model.save()
    #           JSONModelDictField.get_prep_value(...) ->
    #               {"key": {"name": "value", "__json_class__": "module.JSONModelInstance"}}  # gets stored in DB
    #
    #    Loading:
    #       my_model.custom_dict <- {"key": {"name": "value", "__json_class__": "module.JSONModelInstance"}}  # from DB
    #       JSONModelDictField.from_db_value(...) -> CustomDictInstance(**{"key": CustomDictInstance(name="value")})
    #       my_model.custom_dict = CustomDictInstance({"key": "value"})

    def __init__(
        self,
        json_dict_model: Type[JSONModelDict | dict] | JSONModelDictState,
        default: Callable[[], dict] = None,
        verbose_name=None,
        name=None,
        null=True,
        blank=True,
        encoder=None,
        decoder=None,
        **kwargs
    ):
        encoder = encoder or JSONModelEncoder
        decoder = decoder or JSONModelDecoder
        super().__init__(
            verbose_name=verbose_name,
            name=name,
            encoder=encoder,
            decoder=decoder,
            null=null,
            blank=blank,
            default=default,
            **kwargs,
        )
        self.json_dict_model = reconstruct(json_dict_model)

    def get_prep_value(self, value: Any):
        if isinstance(value, JSONModelDict):
            value = value.as_db_json()

        # the top level dict does not need the __json_class__ key since the type is known from the field
        value = _collect_data_from_dict(value, use_json_class=False)
        prep_value = super().get_prep_value(value)
        return prep_value

    def from_db_value(self, value, expression, connection):
        # deserialization is handled by the JSONField superclass through the decoder
        if isinstance(value, str):
            value = super().from_db_value(value, expression, connection)

        if value is None:
            return None

        if isinstance(value, self.json_dict_model):
            return value

        assert isinstance(value, dict)
        return self.json_dict_model(**value)

    def _deconstruct_compat(self, *, cloned: bool = False):
        name, path, args, kwargs = super()._deconstruct_compat(cloned=cloned)
        kwargs["json_dict_model"] = JSONModelDictState.from_model(self.json_dict_model)
        return name, path, args, kwargs

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_serialization(),
        ]

    def _check_serialization(self):
        errors: list[checks.CheckMessage] = []

        if not issubclass(self.encoder, JSONModelEncoder):
            errors.append(
                checks.Critical("JSONModelDictField encoder must be a subclass of JSONModelEncoder", obj=self)
            )

        if not issubclass(self.decoder, JSONModelDecoder):
            errors.append(
                checks.Critical("JSONModelDictField decoder must be a subclass of JSONModelDecoder", obj=self)
            )

        return errors

    def _deconstruct_compat_is_reconstructed(self) -> bool:
        value_class = JSONModelDictState.get_value_class(self.json_dict_model)
        return self._deconstruct_compat_model_is_reconstructed(value_class)
