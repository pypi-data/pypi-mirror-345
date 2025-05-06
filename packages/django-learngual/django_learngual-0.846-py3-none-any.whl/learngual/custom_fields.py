import json

from django.db import models
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework import serializers

from .interface import BaseTypeModel
from .logger import logger


class PydanticModelFieldEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump(mode="json")
        elif isinstance(obj, list) and isinstance(obj[0], BaseModel):
            data: list[BaseModel] = obj
            return [model.model_dump(mode="json") for model in data]
        else:
            return super().default(obj)


class PydanticModelField(models.JSONField):
    """Usage

    data = PydanticModelField(pydantic_model=AnswerModel) \n
    data = PydanticModelField(pydantic_model=[AnswerModel]) \n
    data = PydanticModelField(pydantic_model={"word_play":AnswerModel,"essay":EssayAnswer})
    """

    def __init__(
        self,
        pydantic_model: BaseModel | tuple[BaseModel] | dict[str, BaseModel] = None,
        null=True,
        blank=True,
        *args,
        **kwargs,
    ):
        """Pydantic Model field

        Args:
            pydantic_model (BaseModel | Tuple[BaseModel] | dict[str,BaseModel], optional): _description_. Defaults to None. # noqa

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """

        if pydantic_model:
            if isinstance(pydantic_model, (list, tuple)):
                if not pydantic_model:
                    raise ValueError("pydantic_model list cannot be empty")

                for model_class in pydantic_model:
                    if not issubclass(model_class, (BaseModel, BaseTypeModel)):
                        raise ValueError(
                            "All elements in the tuple/list must be subclasses of BaseModel"
                        )
            elif isinstance(pydantic_model, dict):
                for model_class in pydantic_model.values():
                    if not issubclass(model_class, BaseTypeModel):
                        raise ValueError(
                            "All values in the dictionary must be subclasses of BaseTypeModel"
                        )
            elif not issubclass(pydantic_model, (BaseModel, BaseTypeModel)):
                raise ValueError("pydantic_model must be a subclass of BaseModel")
        self.pydantic_model: BaseModel | BaseTypeModel | None | tuple[
            BaseModel | BaseTypeModel
        ] | dict[str, BaseModel | BaseTypeModel] = pydantic_model

        kwargs["encoder"] = kwargs.get("encoder", PydanticModelFieldEncoder)
        super().__init__(null=null, blank=blank, *args, **kwargs)

    def to_python(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (TypeError, ValueError):
                pass

        if value and self.pydantic_model:
            try:
                if isinstance(self.pydantic_model, (list, tuple)):
                    data = []
                    ModelClass = self.pydantic_model[0]
                    value: list[dict]
                    for x in value:
                        data.append(ModelClass(**x))
                    return data
                elif isinstance(self.pydantic_model, dict):
                    value: dict
                    ModelClass = self.pydantic_model.get(value.get("type"))
                    return ModelClass(**value.get("data"))
                elif issubclass(self.pydantic_model, (BaseModel, BaseTypeModel)):
                    return self.pydantic_model(**value)
                else:
                    raise ValueError("Invalid data")
            except Exception:
                logger.exception("invalid data")
                return
                # raise ValidationError(f"Invalid data for {self.pydantic_model}: {e}")

        return value

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value: BaseModel | BaseTypeModel | list[BaseModel] | None):
        if value is None:
            return [] if isinstance(self.pydantic_model, (list, tuple)) else {}
        data = {}

        if not self.pydantic_model:
            return

        if isinstance(self.pydantic_model, (list, tuple)):
            if not isinstance(value, (list, tuple)):
                raise ValueError("Value must be a list or tuple")
            data = []
            ModelClass = self.pydantic_model[0]
            for model_instance in value:
                model_instance: BaseModel | BaseTypeModel
                if not isinstance(model_instance, ModelClass):
                    raise ValueError("Value must be a list %s" % str(ModelClass))
                data.append(model_instance.model_dump(mode="json"))
        elif isinstance(self.pydantic_model, dict):
            if not isinstance(value, BaseTypeModel):
                raise ValueError("Value must be an instance of BaseTypeModel")
            _type = getattr(value, "type", None)
            if not _type:
                raise ValueError(
                    "%s must have a field `type`" % value.__class__.__name__
                )
            model_type = _type
            ModelClass = self.pydantic_model.get(model_type)
            if ModelClass is None:
                raise ValueError("Invalid value.type")

            if not isinstance(value, ModelClass):
                raise ValueError("Value must be a list %s" % str(ModelClass))
            data = {"type": model_type, "data": value.model_dump(mode="json")}
        elif issubclass(self.pydantic_model, (BaseModel, BaseTypeModel)):
            if not isinstance(value, BaseModel):
                if not value:
                    return value
                raise ValueError(
                    f"Value must be an instance of BaseModel {value = } {self.pydantic_model = }"
                )
            return value.model_dump_json()
        else:
            raise ValueError("Invalid data")
        return json.dumps(data)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)


class PydanticModelSerializerField(serializers.JSONField):
    """
    Example:
        class TestModelRetrieve(serializers.ModelSerializer):
            data = PydanticModelSerializerField(
                pydantic_model=modelsv2.TestModel.data.field.pydantic_model
            )\n
            list_data = PydanticModelSerializerField(
                pydantic_model=modelsv2.TestModel.list_data.field.pydantic_model
            )\n
            type_data = PydanticModelSerializerField(
                pydantic_model=modelsv2.TestModel.type_data.field.pydantic_model
            )\n

            class Meta:
                model = modelsv2.TestModel\n
                fields = [
                    "data",
                    "list_data",
                    "type_data",
                ]


        data with different type will be

        {
            "type":"WORD_PLAY",
            "data":{
                "key1":"value1",
            }
        }

    Args:
        serializers (_type_): _description_
    """

    def __init__(self, pydantic_model=None, *args, **kwargs):
        self.pydantic_model = pydantic_model
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data: dict):
        try:
            if self.pydantic_model:
                if isinstance(self.pydantic_model, (list, tuple)):
                    deserialized_data = []
                    ModelClass = self.pydantic_model[0]
                    for item in data:
                        deserialized_data.append(ModelClass(**item))
                    return deserialized_data
                elif isinstance(self.pydantic_model, dict):
                    ModelClass = self.pydantic_model.get(data.get("type"))
                    if not ModelClass:
                        raise serializers.ValidationError(
                            f"Invalid type; {data.get('type')}"
                        )
                    return ModelClass(**data)
                elif issubclass(self.pydantic_model, (BaseModel, BaseTypeModel)):

                    return self.pydantic_model(**data)
                else:
                    raise serializers.ValidationError("Invalid data")
            return data
        except PydanticValidationError as e:
            raise serializers.ValidationError(e.json())

    def to_representation(self, value) -> str:
        data = PydanticModelField(self.pydantic_model).get_prep_value(value)
        if isinstance(data, str):
            data = json.loads(data)
        if (
            data
            and isinstance(data, dict)
            and sorted(list(data.keys())) == sorted(["data", "type"])
            and data.get("type")
            and data.get("type") == data.get("data", {}).get("type")
        ):
            data = data.get("data")
        return data

    def _format_validation_error(self, error):
        if isinstance(error, PydanticValidationError):
            error_messages = []

            for error_obj in error.errors():
                if isinstance(error_obj, dict):
                    for field, field_errors in error_obj.items():
                        for sub_error in field_errors:
                            error_messages.append(
                                {
                                    "field": field,
                                    "message": str(sub_error),
                                }
                            )
                else:
                    error_messages.append({"field": "", "message": str(error_obj)})

            return error_messages
        return str(error)
