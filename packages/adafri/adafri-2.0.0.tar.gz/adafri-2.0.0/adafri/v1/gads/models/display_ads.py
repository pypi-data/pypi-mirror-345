from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, BaseFieldsClass, BaseClass,init_class_kwargs, get_object_model_class
from .text import AssetText
from .videos import VideoAsset
from .images import AssetNative
@dataclass
class ResponsiveDisplayAdsToPublishFields(BaseFieldsClass):
    id = "id"
    titles = "titles"
    descriptions = "descriptions"
    longHeadline = "longHeadline"
    brand = "brand"
    videosAssets = "videosAssets"
    marketingImages = "marketingImages"
    squareMarketingImages = "squareMarketingImages"
    logoImages = "logoImages"
    landscapeLogoImages = "landscapeLogoImages"
    is_removed = "is_removed"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass(init=False)
class ResponsiveDisplayAdsToPublish(BaseClass):
    id: str
    titles: list[AssetText]
    descriptions: list[AssetText]
    longHeadline: str
    brand: AssetText
    videosAssets: list[VideoAsset]
    marketingImages: list[AssetNative]
    squareMarketingImages: list[AssetNative]
    logoImages: list[AssetNative]
    landscapeLogoImages: list[AssetNative]
    is_removed: bool

    def __init__(self, asset=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, asset, None, None, None, [], **kwargs)
        for key in keys:
            if key=='titles':
                setattr(self, key, AssetText().fromListDict(cls_object[key]))
            elif key=='descriptions':
                setattr(self, key, AssetText().fromListDict(cls_object[key]))
            elif key=='brand':
                setattr(self, key, AssetText().from_dict(cls_object[key]))
            elif key=='videosAssets':
                setattr(self, key, VideoAsset().fromListDict(cls_object[key]))
            elif key=='marketingImages':
                setattr(self, key, AssetNative().fromListDict(cls_object[key]))
            elif key=='squareMarketingImages':
                setattr(self, key, AssetNative().fromListDict(cls_object[key]))
            elif key=='logoImages':
                setattr(self, key, AssetNative().fromListDict(cls_object[key]))
            elif key=='landscapeLogoImages':
                setattr(self, key, AssetNative().fromListDict(cls_object[key]))
            else:
                setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "id": self.id,
            "titles": AssetText().toListDict(self.titles, None),
            "descriptions": AssetText().toListDict(self.descriptions, None),
            "longHeadline": self.longHeadline,
            "brand": self.brand.to_dict(None),
            "videosAssets": VideoAsset().toListDict(self.videosAssets, None),
            "marketingImages": AssetNative().toListDict(self.marketingImages, None),
            "squareMarketingImages": AssetNative().toListDict(self.squareMarketingImages, None),
            "logoImages": AssetNative().toListDict(self.logoImages, None),
            "landscapeLogoImages": AssetNative().toListDict(self.landscapeLogoImages, None),
            "is_removed": self.is_removed
        })
    @staticmethod
    def from_dict(obj: Any) -> 'ResponsiveDisplayAdsToPublish':
        cls_object, keys = get_object_model_class(obj, ResponsiveDisplayAdsToPublish, None);
        return ResponsiveDisplayAdsToPublish(cls_object)


@dataclass(init=False)
class DisplayAdsToPublishFields(BaseFieldsClass):
    id = "id"
    name = "name"
    mediaId = "mediaId"
    type = "type"
    width = "width"
    height = "height"
    urls = "urls"
    previewUrl = "previewUrl"
    resourceName = "resourceName"
    sourceUrl = "sourceUrl"
    type = "type"
    mimeType = "mimeType"
    owner = "owner"
    fileSize = "fileSize"
    clientCustomerId = "clientCustomerId"

@dataclass(init=False)
class DisplayAdsToPublish(BaseClass):
    id: str
    name: str
    mediaId: int
    type: str
    width: str
    height: str
    urls: str
    previewUrl: str
    resourceName: str
    sourceUrl: str
    type: str
    mimeType: str
    owner: str
    fileSize: str
    clientCustomerId: str
    def __init__(self, ad=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, ad, None, None, None, [], **kwargs)
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "id": self.id,
            "name": self.name,
            "mediaId": self.mediaId,
            "type": self.type,
            "width": self.width,
            "height": self.height,
            "urls": self.urls,
            "previewUrl": self.previewUrl,
            "resourceName": self.resourceName,
            "sourceUrl": self.sourceUrl,
            "type": self.type,
            "mimeType": self.mimeType,
            "owner": self.owner,
            "fileSize": self.fileSize,
            "clientCustomerId": self.clientCustomerId
        })
    @staticmethod
    def from_dict(obj: Any) -> 'DisplayAdsToPublish':
        cls_object, keys = get_object_model_class(obj, DisplayAdsToPublish, None);
        return DisplayAdsToPublish(cls_object)


