from .....utils import (DictUtils, get_object_model_class, init_class_kwargs, BaseClass, get_request_fields, RequestFields)
from .....utils.response import ApiResponse, Error, ResponseStatus, StatusCode
from typing import Any
from dataclasses import dataclass
import pydash
from ...models.adgroups.base import BaseAdGroup
from ...models.placement import (Website, YoutubeChannel, YoutubeVideo)
from .adgroup_fields import (AdGroupDisplayFields, AdGroupDisplayFieldsProps, ADGROUP_DISPLAY_PICKABLE_FIELDS, DISPLAY_ADGROUPS_COLLECTION)
from ...models.placement import Website, YoutubeChannel, YoutubeVideo
from ...models.display_ads import (DisplayAdsToPublish, ResponsiveDisplayAdsToPublish)

def filter_adgroup_display_request_fields(fields, default_fields = ADGROUP_DISPLAY_PICKABLE_FIELDS):
    request_fields = get_request_fields(fields, default_fields, [default_fields[0]])
    if request_fields is None or bool(request_fields) is False:
        request_fields = [default_fields[0]]
    return request_fields

@dataclass(init=False)
class AdGroupDisplay(BaseAdGroup):
    targetedPlacements: list[Website]
    excludedPlacements: list[Website]
    websites: list[Website]
    youtubeChannels: list[YoutubeChannel]
    youtubeVideos: list[YoutubeVideo]
    __baseFields: AdGroupDisplayFieldsProps

    def __init__(self, adgroup=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, adgroup, ADGROUP_DISPLAY_PICKABLE_FIELDS, AdGroupDisplayFieldsProps, DISPLAY_ADGROUPS_COLLECTION, ['id'], **kwargs)
        super().__init__(**{**data_args, "adgroup": adgroup});
        for key in keys:
            if AdGroupDisplayFieldsProps.get(key) is None:
                website = ['targetedPlacements', 'excludedPlacements', 'websites']
                if key in website:
                    setattr(self, key, Website().fromListDict(cls_object[key]))
                elif key == 'youtubeChannels':
                    setattr(self, key, YoutubeChannel().fromListDict(cls_object[key]))
                elif key == 'youtubeVideos':    
                    setattr(self, key, YoutubeVideo().fromListDict(cls_object[key]))
                elif key == 'images':
                    setattr(self, key, DisplayAdsToPublish().fromListDict(cls_object[key]))
                elif key == 'imagesNative':
                    setattr(self, key, ResponsiveDisplayAdsToPublish().fromListDict(cls_object[key]))
                else:
                    setattr(self, key, cls_object[key]) 


    @staticmethod
    def generate_model(_key_="default_value"):
        user = {};
        props = AdGroupDisplayFieldsProps
        for k in DictUtils.get_keys(props):
            user[k] = props[k][_key_];
        return user;

    @staticmethod
    def from_dict(adgroup: Any, db=None, collection_name=None) -> 'AdGroupDisplay':
        cls_object, keys = get_object_model_class(adgroup, AdGroupDisplay, AdGroupDisplayFieldsProps);
        _adgroup = AdGroupDisplay(cls_object, db=db, collection_name=collection_name)
        return _adgroup
    
    def to_dict(self, fields=None):
        base = super().to_dict(fields)
        return {
            **base,
            "targetedPlacements": Website().toListDict(self.targetedPlacements, None),
            "excludedPlacements": Website().toListDict(self.excludedPlacements, None),
            "websites": Website().toListDict(self.websites, None),
            "youtubeChannels": YoutubeChannel().toListDict(self.youtubeChannels, None),
            "youtubeVideos": YoutubeVideo().toListDict(self.youtubeVideos, None),
            "images": DisplayAdsToPublish().toListDict(getattr(self, 'images', None), None),
            "imagesNative": ResponsiveDisplayAdsToPublish().toListDict(getattr(self, 'imagesNative', None), None),
    }
    def getAdGroups(self, accountId, campaignId, fields=None):
        print('getAdGroups', accountId, campaignId)
        isID = False
        try:
            campaignId = int(campaignId)
        except:
            isID = True
        if isID is False and accountId is None:
            return None
        adgroups = []
        adgroups_ = self.query(AdGroupDisplay, "adgroup", query_params=[{"key": "accountId", "comp": "==", "value": accountId}, {"key": "campaign_id", "comp": "==", "value": campaignId}])
        request_fields = filter_adgroup_display_request_fields(fields)
        print('request_fields adgroup ===>', request_fields)
        # print('account query', account)
        for adgroup in adgroups_:
            adgroups.append(DictUtils.filter_by_fields(adgroup.to_dict(), request_fields))

        return adgroups
    
    def get(self, fields=None):
        if bool(self.id) is None:
            return None;
        request_fields = filter_adgroup_display_request_fields(fields)
        doc = self.document_reference().get();
        if doc.exists is False:
            return None;
        data = {"id": doc.id, **doc.to_dict()}
        return AdGroupDisplay.from_dict(adgroup=AdGroupDisplay.from_dict(adgroup=data).to_dict(),  db=self.db, collection_name=self.collection_name);

    def getByUserId(self,id, fields=None):
        adgroups = [];
        request_fields = filter_adgroup_display_request_fields(fields)
        docs = self.collection().where('owner','==',id).get();
        for doc in docs:
            data = doc.to_dict();
            data['id'] = doc.id;
            adgroups.append(AdGroupDisplay.from_dict(adgroup=AdGroupDisplay.from_dict(adgroup=data).to_json(request_fields),  db=self.db, collection_name=self.collection_name));
        return adgroups;


    def update(self, data):
        try:
            last_value = self.to_json();
            filtered_value = pydash.pick(data, AdGroupDisplayFields.filtered_keys('editable', True));
            new_value = DictUtils.merge_dict(filtered_value, self.to_json());
            changed_fields = DictUtils.get_changed_field(last_value, new_value);
            data_update = DictUtils.dict_from_keys(filtered_value, changed_fields);
            if bool(data_update) is False:
                return None;
            self.document_reference().set(data_update, merge=True)
            return DictUtils.dict_from_keys(self.getAccount(), changed_fields);
        except Exception as e:
            print(e)
            return None;

    def remove(self, only_mark_as_removed=True):
        try:
            if self.id is None:
                return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"Cannot identify Campaign with id {self.id}","INVALID_REQUEST", 1));
            if only_mark_as_removed:
                self.document_reference().set({"is_removed": True})
            else:
                self.document_reference().delete();
            return ApiResponse(ResponseStatus.OK, StatusCode.status_200, {"message": f"Campaign {self.id} deleted"}, None);
        except:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"An error occurated while removing authorization code with id {self.id}","INVALID_REQUEST", 1));

