from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, BaseFieldsClass, BaseClass,init_class_kwargs,get_object_model_class
@dataclass
class VideoAssetFields(BaseFieldsClass):
    id = "id"
    assetId = "assetId"
    videoId = "videoId"
    name = "name"
    thumbnails = "thumbnails"
    previewUrl = "previewUrl"
    snippet = "snippet"
    owner = "owner"
    accountId = "accountId"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass(init=False)
class VideoAsset(BaseClass):
    id: str
    name: str
    assetId: int
    videoId: str
    name: str
    thumbnails: str
    previewUrl: str
    snippet: str
    owner: str
    accountId: str

    def __init__(self, asset=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, asset, None, None, None, [], **kwargs)
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "id": self.id,
            "name": self.name,
            "assetId": self.assetId,
            "videoId": self.videoId,
            "thumbnails": self.thumbnails,
            "previewUrl": self.previewUrl,
            "snippet": self.snippet,
            "owner": self.owner,
            "accountId": self.accountId
        })
    @staticmethod
    def from_dict(obj: Any) -> 'VideoAsset':
        cls_object, keys = get_object_model_class(obj, VideoAsset, None);
        return VideoAsset(cls_object)

