from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, BaseFieldsClass, BaseClass,init_class_kwargs,get_object_model_class

@dataclass
class GendersFields(BaseFieldsClass):
    text = "text"
    gendersRangeType = "gendersRangeType"
    criterionId = "criterionId"
    criterionType = "criterionType"
    type = "type"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass(init=False)
class Genders(BaseClass):
    text: str
    gendersRangeType: str
    criterionId: int
    criterionType: str
    type: str
    def __init__(self, ages=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, ages, None, None, None, [], **kwargs)
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "text": self.text,
            "gendersRangeType": self.gendersRangeType,
            "criterionId": self.criterionId,
            "criterionType": self.criterionType,
            "type": self.type
        })
    @staticmethod
    def from_dict(obj: Any) -> 'Genders':
        cls_object, keys = get_object_model_class(obj, Genders, None);
        return Genders(cls_object)