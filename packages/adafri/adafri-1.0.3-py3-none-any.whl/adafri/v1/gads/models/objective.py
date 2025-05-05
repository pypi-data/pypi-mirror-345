from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, ArrayUtils, BaseFieldsClass, BaseClass,init_class_kwargs,get_object_model_class
from ..data.objectives import objectives_data
@dataclass
class ObjectveFields(BaseFieldsClass):
    id = "obj_id"
    primary = "primary"
    secondary = "secondary"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass(init=False)
class Objective(BaseClass):
    obj_id: str
    primary: dict
    secondary: dict
    def __init__(self, objective=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, objective, ['obj_id'], None, None, [], **kwargs)
        objective_value = ArrayUtils.find(objectives_data, lambda x: x['obj_id'] == cls_object['obj_id'])
        if objective_value is not None:
            for key in objective_value:
                setattr(self, key, objective_value[key]) 
    def to_dict(self, fields=None):
        return DictUtils.remove_none_values(
            {
            ObjectveFields.id: self.obj_id,
            ObjectveFields.primary: self.primary,
            ObjectveFields.secondary: self.secondary
        }
        )
    @staticmethod
    def from_dict(obj: Any) -> 'Objective':
        cls_object, keys = get_object_model_class(obj, Objective, None);
        return Objective(cls_object)