from __future__ import annotations, annotations

from typing import TYPE_CHECKING, Type, TypeVar, cast

from django.db.models import Field

from . import migration_helpers

if TYPE_CHECKING:
    from .json_model import JSONModel

TType = TypeVar("TType", bound=type)


class JSONModelState:
    """
    Used to represent the state of a JSONModel class in migrations to prevent importing the actual JSONModel subclass.
    """

    @classmethod
    def from_model(cls, model_class: Type[JSONModel]) -> JSONModelState:
        """
        Deconstructs a JSONModel class into JSONModelState instance that is used to represent the model in migrations.
        """

        bases = tuple(
            (
                cls._get_deconstructed_parent(parent)
                for parent in model_class.__bases__
            )
        )
        opts = model_class._meta
        fields = [(field.name, field) for field in opts.get_fields(include_parents=False)]
        attrs = {}
        if hasattr(model_class, "__classcell__"):
            attrs["__classcell__"] = model_class.__classcell__
        if opts.abstract:
            attrs["abstract"] = True

        state_kwargs = {
            "name": model_class.__name__,
            "bases": tuple(bases),
            "fields": fields,
        }
        if attrs:
            state_kwargs["attrs"] = attrs

        return JSONModelState(**state_kwargs)

    @classmethod
    def _get_deconstructed_parent(cls, parent: type) -> type | JSONModelState:
        from .json_model import JSONModel

        if parent == JSONModel:
            return migration_helpers.get_migration_import_class_placeholder(
                JSONModel,
                "django_json_model_field.db.models"
            )

        if issubclass(parent, JSONModel):
            return cls.from_model(parent)

        return parent

    def __init__(
        self,
        name: str,
        bases: tuple[type | JSONModelState, ...],
        fields: list[tuple[str, Field]],
        attrs: dict = None,
    ):
        self.name = name
        self.bases = bases
        self.fields = fields
        self.attrs = attrs or {}

    def deconstruct(self) -> tuple[str, tuple, dict]:
        attrs = {
            "name": self.name,
            "bases": self.bases,
            "fields": self.fields,
        }
        if self.attrs:
            attrs["attrs"] = self.attrs

        return "django_json_model_field.db.models.JSONModelState", (), attrs

    def reconstruct(self) -> Type[JSONModel]:
        """
        Reconstructs a JSONModel class from a deconstructed representation. Used when reconstructing JSONModelField
        instances from migration files during Django migration commands.

        The resulting classes are used for comparing the current state of the model as defined in the code against
        the cumulatively rendered state of the model in the migration files. It is not used at runtime.
        """

        bases = tuple(base.reconstruct() if isinstance(base, JSONModelState) else base for base in self.bases)
        attrs: dict = {name: field for name, field in self.fields}
        attrs.update(self.attrs)
        attrs.update(__module__="django_json_model_field.db.models.__reconstructed__")

        from .json_model import JSONModel

        return cast(Type[JSONModel], type(self.name, bases, attrs))


def reconstruct(state: JSONModelState | Type[JSONModel]) -> Type[JSONModel]:
    """
    Convenience function for reconstructing a JSONModel class from a JSONModelState instance or a JSONModel class.
    """

    return state.reconstruct() if isinstance(state, JSONModelState) else state
