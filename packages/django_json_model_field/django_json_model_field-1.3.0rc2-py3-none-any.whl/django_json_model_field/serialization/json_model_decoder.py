from importlib import import_module
from json import JSONDecoder

from django.db import connection

from django_json_model_field.db.models import JSONModel
from . import constants


class JSONModelDecoder(JSONDecoder):

    def __init__(self, **kwargs):
        super().__init__(object_hook=self._object_hook, **kwargs)

    @classmethod
    def _object_hook(cls, d: dict):
        if constants.JSON_CLASS_KEY not in d:
            return d

        # load the model class from __json_class__ and instantiate it
        model_name = d.pop(constants.JSON_CLASS_KEY)
        module_name, model_name = model_name.rsplit(".", 1)
        model_module = import_module(module_name)
        model = getattr(model_module, model_name)

        if issubclass(model, JSONModel):
            from django_json_model_field.db.models import JSONModelField

            field = JSONModelField(model)
            return field.from_db_data_dict(d, connection)

        return model(**d)
