from __future__ import annotations, annotations

from importlib import import_module
from types import new_class
from typing import Any, Dict, TYPE_CHECKING, Type, TypeVar, cast, overload

from .json_model_state import JSONModelState

if TYPE_CHECKING:
    from .json_model import JSONModel

TType = TypeVar("TType", bound=type)


class JSONModelDictState:
    """
    Used to represent the state of a JSONModel class in migrations to prevent importing the actual JSONModel subclass.
    """

    @classmethod
    def from_model(cls, model_class: Type[dict[Any, JSONModel]]) -> JSONModelDictState:
        """
        Deconstructs a JSONModelDict class into JSONModelDictState instance that is used to represent the model in
        migrations.
        """

        is_typing_dict = str(model_class).startswith("typing.Dict")
        dict_class = dict if is_typing_dict else model_class
        dict_class_name = "dict" if is_typing_dict else getattr(dict_class, "__qualname__", dict_class.__name__)

        value_class = _get_value_class(model_class)

        from .json_model import JSONModel

        if not issubclass(value_class, (JSONModel, dict)):
            raise TypeError(f"Value class {value_class} must be a subclass of JSONModel")

        state_kwargs = {
            "dict_class": (dict_class.__module__, dict_class_name),
            "value_class": (
                JSONModelDictState.from_model(value_class)
                if issubclass(value_class, dict)
                else JSONModelState.from_model(value_class)
            ),
        }

        return JSONModelDictState(**state_kwargs)

    @classmethod
    def get_value_class(cls, model_class: Type[dict[Any, JSONModel]]) -> Type[JSONModel]:
        return _get_value_class(model_class)

    def __init__(
        self,
        dict_class: tuple[str, str],
        value_class: JSONModelState,
    ):
        self.dict_class = dict_class
        self.value_class = value_class

    def deconstruct(self) -> tuple[str, tuple, dict]:
        attrs = {
            "dict_class": self.dict_class,
            "value_class": self.value_class,
        }

        return "django_json_model_field.db.models.JSONModelDictState", (), attrs

    def reconstruct(self) -> Type[dict]:
        """
        Reconstructs a JSONModel class from a deconstructed representation. Used when reconstructing JSONModelField
        instances from migration files during Django migration commands.

        The resulting classes are used for comparing the current state of the model as defined in the code against
        the cumulatively rendered state of the model in the migration files. It is not used at runtime.
        """

        dict_class_module, dict_class_name = self.dict_class
        dict_class = (
            Dict if (dict_class_module, dict_class_name) == ("builtins", "dict")
            else getattr(import_module(dict_class_module), dict_class_name)
        )
        value_class = self.value_class.reconstruct()

        result = new_class(dict_class_name, (dict_class,))
        result.__module__ = dict_class_module
        result.__args__ = (str, value_class)

        return cast(Type[dict], result)


def reconstruct(state: JSONModelDictState | Type[dict]) -> Type[dict]:
    """
    Convenience function for reconstructing a JSONModel class from a JSONModelState instance or a JSONModel class.
    """

    return state.reconstruct() if isinstance(state, JSONModelDictState) else state


@overload
def _get_value_class(model_class: type) -> Type[JSONModel]:
    ...


@overload
def _get_value_class(model_class: type, *, _depth: int = 0) -> Type[JSONModel] | None:
    ...


def _get_value_class(model_class: type, *, _depth: int = 0) -> Type[JSONModel] | None:

    value_class = _get_value_arg(getattr(model_class, "__args__", ()))
    if value_class is not None:
        from .json_model import JSONModel

        if issubclass(value_class, JSONModel):
            return value_class

        # JSONModelDict may be nested
        if issubclass(value_class, dict):
            return _get_value_class(value_class, _depth=_depth + 1)

    value_class = _find_value_class_in_bases(getattr(model_class, "__orig_bases__", ()), _depth=_depth)
    if value_class is not None:
        return value_class

    value_class = _find_value_class_in_bases(getattr(model_class, "__bases__", ()), _depth=_depth)
    if value_class is not None:
        return value_class

    if _depth > 0:
        return None

    raise TypeError(
        f"Model class {model_class} must be a generic dict type with a value type that is a JSONModel subclass "
        f"or another JSONModelDict type"
    )


def _get_value_arg(args: tuple[type, ...]) -> type | None:
    return len(args) == 2 and args[1] or None


def _find_value_class_in_bases(bases: tuple[type, ...], *, _depth: int) -> Type[JSONModel] | None:
    for base in bases:
        base_result = _get_value_class(base, _depth=_depth + 1)
        if base_result is not None:
            return base_result
    return None
