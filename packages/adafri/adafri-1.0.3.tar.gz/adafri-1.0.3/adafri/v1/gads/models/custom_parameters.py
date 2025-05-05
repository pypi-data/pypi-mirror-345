from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, BaseFieldsClass, BaseClass,init_class_kwargs,get_object_model_class

@dataclass
class CustomParametersFields(BaseFieldsClass):
    key = "key"
    value = "value"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass(init=False)
class CustomParameters(BaseClass):
    key: str
    value: str
    def __init__(self, custom_parameters=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, custom_parameters, None, None, None, [], **kwargs)
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "key": self.key,
            "value": self.value
        })
    @staticmethod
    def from_dict(obj: Any) -> 'CustomParameters':
        cls_object, keys = get_object_model_class(obj, CustomParameters, None);
        return CustomParameters(cls_object)