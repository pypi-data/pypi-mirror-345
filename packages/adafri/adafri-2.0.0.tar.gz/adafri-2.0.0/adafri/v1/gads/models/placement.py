from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, BaseFieldsClass, BaseClass,init_class_kwargs,get_object_model_class

@dataclass
class WebsiteFields(BaseFieldsClass):
    id = "id"
    url = "url"
    criterionId = "criterionId"
    criterionType = "criterionType"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass
class YoutubeChannelFields(BaseFieldsClass):
    id = "id"
    channelId = "channelId"
    name = "name"
    snippet = "snippet"
    thumbnails = "thumbnails"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass
class YoutubeVideoFields(BaseFieldsClass):
    id = "id"
    videoId = "videoId"
    name = "name"
    snippet = "snippet"
    thumbnails = "thumbnails"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass(init=False)
class Website(BaseClass):
    id: str
    url: str
    criterionId: int
    criterionType: str
    def __init__(self, website=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, website, None, None, None, [], **kwargs)
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "id": self.id,
            "url": self.url,
            "criterionId": self.criterionId,
            "criterionType": self.criterionType
        })
    @staticmethod
    def from_dict(obj: Any) -> 'Website':
        cls_object, keys = get_object_model_class(obj, Website, None);

        return Website(cls_object)
@dataclass(init=False)
class YoutubeChannel(BaseClass):
    id: str
    channelId: str
    name: str
    snippet: str
    thumbnails: str
    def __init__(self, channel=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, channel, None, None, None, [], **kwargs)
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "id": self.id,
            "channelId": self.channelId,
            "name": self.name,
            "snippet": self.snippet,
            "thumbnails": self.thumbnails
        })
    @staticmethod
    def from_dict(obj: Any) -> 'YoutubeChannel':
        cls_object, keys = get_object_model_class(obj, YoutubeChannel, None);
        return YoutubeChannel(cls_object)

@dataclass(init=False)
class YoutubeVideo(BaseClass):
    id: str
    videoId: str
    name: str
    snippet: str
    thumbnails: str
    def __init__(self, video=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, video, None, None, None, [], **kwargs)
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "id": self.id,
            "videoId": self.videoId,
            "name": self.name,
            "snippet": self.snippet,
            "thumbnails": self.thumbnails
        })
    @staticmethod
    def from_dict(obj: Any) -> 'YoutubeVideo':
        cls_object, keys = get_object_model_class(obj, YoutubeVideo, None);
        return YoutubeVideo(cls_object)