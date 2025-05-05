from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, BaseFieldsClass, BaseClass,init_class_kwargs,get_object_model_class

@dataclass
class DevicesFields(BaseFieldsClass):
    id = "id"
    name = "name"
    type = "type"
    criterionId = "criterionId"
    criterionType = "criterionType"
    isTargeted = "isTargeted"
    isExcluded = "isExcluded"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass(init=False)
class Devices(BaseClass):
    id: str
    name: str
    type: str
    criterionType: str
    criterionId: int
    isTrageted: bool
    isExcluded: bool
    def __init__(self, device=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, device, None, None, None, [], **kwargs)
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "criterionType": self.criterionType,
            "criterionId": self.criterionId,
            "isTrageted": self.isTrageted,
            "isExcluded": self.isExcluded
        })
    @staticmethod
    def from_dict(obj: Any) -> 'Devices':
        cls_object, keys = get_object_model_class(obj, Devices, None);
        return Devices(cls_object)