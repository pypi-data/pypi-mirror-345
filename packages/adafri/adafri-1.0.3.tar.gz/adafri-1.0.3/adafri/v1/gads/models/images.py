from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, BaseFieldsClass, BaseClass,init_class_kwargs,get_object_model_class

@dataclass
class DisplayAdsToPublishFields(BaseFieldsClass):
    id = "id"
    name = "name"
    mediaId = "mediaId"
    type = "type"
    width = "width"
    height = "height"
    url = "url"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass
class AssetNativeFields(BaseFieldsClass):
    id = "id"
    assetId = "assetId"
    width = "width"
    height = "height"
    imageUrl = "imageUrl"
    imageFileSize = "imageFileSize"
    imageMimeType = "imageMimeType"
    usage = "usage"
    useFor = "useFor"
    owner = "owner"
    aacid = "aacid"
    clientCustomerId = "clientCustomerId"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass(init=False)
class AssetNative(BaseClass):
    id: str
    name: str
    assetId: int
    imageFileSize: int
    imageMimeType: str
    usage: list[str]
    useFor: str
    owner: str
    aacid: str
    width: int
    height: int
    imageUrl: str
    def __init__(self, asset=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, asset, None, None, None, [], **kwargs)
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "id": self.id,
            "name": self.name,
            "assetId": self.assetId,
            "imageFileSize": self.imageFileSize,
            "imageMimeType": self.imageMimeType,
            "usage": self.usage,
            "useFor": self.useFor,
            "owner": self.owner,
            "aacid": self.aacid,
            "width": self.width,
            "height": self.height,
            "imageUrl": self.imageUrl
        })
    @staticmethod
    def from_dict(obj: Any) -> 'AssetNative':
        cls_object, keys = get_object_model_class(obj, AssetNative, None);
        return AssetNative(cls_object)

