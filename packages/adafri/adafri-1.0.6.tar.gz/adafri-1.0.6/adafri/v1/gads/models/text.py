from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, BaseFieldsClass, BaseClass,init_class_kwargs,get_object_model_class
        
@dataclass
class AssetTextFields(BaseFieldsClass):
    assetText = "assetText"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
@dataclass(init=False)
class AssetText(BaseClass):
    assetText: str
    def __init__(self, asset=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, asset, None, None, None, [], **kwargs)
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "assetText": self.assetText,
        })
    @staticmethod
    def from_dict(obj: Any) -> 'AssetText':
        cls_object, keys = get_object_model_class(obj, AssetText, None);
        return AssetText(cls_object)


