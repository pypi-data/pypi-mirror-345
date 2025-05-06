from __future__ import annotations

from abc import ABC, abstractmethod
from json import JSONDecoder, JSONEncoder
from typing import TYPE_CHECKING, Type

from django.db.models import Field

from . import migration_compat, migration_helpers

if TYPE_CHECKING:
    from .json_model import JSONModel


class MigrationCompatFieldMixin(Field, ABC):

    encoder: Type[JSONEncoder] | None
    decoder: Type[JSONDecoder] | None

    def __init__(
        self,
        *args,
        # internal flags used for deconstructing compatibility migrations
        # see comments in deconstruct_compat module for details
        _deconstruct_compat_migration: tuple[str, str, str] = None,
        _cloned: bool = False,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._deconstruct_compat_migration = self._init_deconstruct_compat_migration(
            _deconstruct_compat_migration,
            _cloned
        )

    @abstractmethod
    def _deconstruct_compat_is_reconstructed(self) -> bool:
        raise NotImplementedError()

    @classmethod
    def _deconstruct_compat_model_is_reconstructed(cls, model: Type[JSONModel]) -> bool:
        return model.__module__.endswith(".__reconstructed__")

    def deconstruct(self):
        return self._deconstruct_compat()

    def _deconstruct_compat(self, *, cloned: bool = False):
        """
        deconstruct() implementation that adds metadata to trigger a deconstruct compatibility migration if needed
        see comments in deconstruct_compat module for details
        """

        name, path, args, kwargs = super().deconstruct()

        if cloned:
            kwargs["_cloned"] = True

        kwargs["encoder"] = migration_helpers.get_migration_import_class_placeholder(
            self.encoder,
            "django_json_model_field.serialization"
        )
        kwargs["decoder"] = migration_helpers.get_migration_import_class_placeholder(
            self.decoder,
            "django_json_model_field.serialization"
        )

        if migration_compat.is_enabled() and not migration_compat.is_migrated_field(self):
            # cloned = coming from migration check to get the current state of the field
            if cloned and hasattr(self, "model"):
                kwargs["_deconstruct_compat_migration"] = migration_compat.get_migration_entry(self)
            elif self._deconstruct_compat_is_reconstructed() and self._deconstruct_compat_migration:
                kwargs["_deconstruct_compat_migration"] = self._deconstruct_compat_migration

        if path.startswith("django_json_model_field.db.models"):
            # provide the more concise path for the JSONModelField module in migrations - the import will use
            # django_json_model_field.db.models.JSONModelField
            # instead of
            # django_json_model_field.db.models.json_model_field.JSONModelField
            _, field_class_name = path.rsplit(".", 1)
            path = f"django_json_model_field.db.models.{field_class_name}"

        return name, path, args, kwargs

    def _init_deconstruct_compat_migration(
        self,
        deconstruct_compat_migration: tuple[tuple[str, str], str] | None,
        cloned: bool,
    ) -> tuple[tuple[str, str], str] | None:
        if not cloned and deconstruct_compat_migration:
            migration_compat.mark_migrated(deconstruct_compat_migration)

        return deconstruct_compat_migration

    def clone(self):
        name, path, args, kwargs = self._deconstruct_compat(cloned=True)
        return self.__class__(*args, **kwargs)
