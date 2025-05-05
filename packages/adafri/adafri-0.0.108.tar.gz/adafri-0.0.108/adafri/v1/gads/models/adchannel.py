from dataclasses import dataclass
from typing import Any
from  ....utils.utils import ArrayUtils, DictUtils, BaseFieldsClass, BaseClass, init_class_kwargs,get_object_model_class
from ..data.adsChannel import ads_channel_data
@dataclass
class AdChannelFields(BaseFieldsClass):
    obj_id = "obj_id"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass(init=False)
class AdChannel(BaseClass):
    obj_id: str
    primary: dict
    secondary: dict
    def __init__(self, adChannel=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, adChannel, ['obj_id'], None, None, [], **kwargs)
        objective_value = ArrayUtils.find(ads_channel_data, lambda x: x['obj_id'] == cls_object['obj_id'])
        if objective_value is not None:
            for key in objective_value:
                setattr(self, key, objective_value[key]) 
        # for key in keys:
        #     setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "obj_id": self.obj_id,
            "primary": self.primary,
            "secondary": self.secondary
        })
    @staticmethod
    def from_dict(obj: Any) -> 'AdChannel':
        cls_object, keys = get_object_model_class(obj, AdChannel, None);
        return AdChannel(cls_object)