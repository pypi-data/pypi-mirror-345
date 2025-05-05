from ....base.firebase_collection import FirebaseCollectionBase
from .....utils import (DictUtils, DateUtils, ArrayUtils, get_object_model_class, init_class_kwargs, BaseClass, get_request_fields, RequestFields)
from .....utils.response import ApiResponse, Error, ResponseStatus, StatusCode
from typing import Any
from dataclasses import dataclass
import pydash
from ...models.base import BaseCampaign, BaseCampaignFieldsProps
from ...models.placement import (Website, YoutubeChannel, YoutubeVideo)
from .display_fields import (CampaignDisplayFields, CampaignDisplayFieldsProps, CAMPAIGN_DISPLAY_PICKABLE_FIELDS, DISPLAY_COLLECTION)
from ...models.display_ads import (DisplayAdsToPublish, ResponsiveDisplayAdsToPublish)
from ...models.placement import Website, YoutubeChannel, YoutubeVideo
from firebase_admin.firestore import firestore
import time

def filter_campaign_display_request_fields(fields, default_fields = CAMPAIGN_DISPLAY_PICKABLE_FIELDS):
    request_fields = get_request_fields(fields, default_fields, [default_fields[0]])
    if request_fields is None or bool(request_fields) is False:
        request_fields = [default_fields[0]]
    return request_fields

@dataclass(init=False)
class CampaignDisplay(BaseCampaign):
    id: str
    targetedPlacements: list[Website]
    excludedPlacements: list[Website]
    websites: list[Website]
    youtubeChannels: list[YoutubeChannel]
    youtubeVideos: list[YoutubeVideo]
    images: list[DisplayAdsToPublish]
    imagesNative: list[ResponsiveDisplayAdsToPublish]
    __baseFields: CampaignDisplayFieldsProps

    def __init__(self, campaign=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, campaign, CAMPAIGN_DISPLAY_PICKABLE_FIELDS, CampaignDisplayFieldsProps, DISPLAY_COLLECTION, ['id'], **kwargs)
        super().__init__(**{**data_args, "campaign": campaign});
        for key in keys:
            if BaseCampaignFieldsProps.get(key) is None:
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
        model = {};
        props = CampaignDisplayFieldsProps
        for k in DictUtils.get_keys(props):
            if _key_ in props[k] and props[k][_key_] is not None:
                model[k] = props[k][_key_];
        return model;

    @staticmethod
    def from_dict(campaign: Any, db=None, collection_name=None) -> 'CampaignDisplay':
        cls_object, keys = get_object_model_class(campaign, CampaignDisplay, CampaignDisplayFieldsProps);
        _campaign = CampaignDisplay(cls_object, db=db, collection_name=collection_name)
        return _campaign
    
    def to_dict(self, fields=None):
        base = super().to_dict(fields)
        # print('base', base['ages'])
        return DictUtils.remove_none_values({
            **base,
            "targetedPlacements": Website().toListDict(self.targetedPlacements, None),
            "excludedPlacements": Website().toListDict(self.excludedPlacements, None),
            "websites": Website().toListDict(self.websites, None),
            "youtubeChannels": YoutubeChannel().toListDict(self.youtubeChannels, None),
            "youtubeVideos": YoutubeVideo().toListDict(self.youtubeVideos, None),
            "images": DisplayAdsToPublish().toListDict(self.images, None),
            "imagesNative": ResponsiveDisplayAdsToPublish().toListDict(self.imagesNative, None),
    })
    def getCampaigns(self, aacid, fields=None):
        campaigns = []
        campaigns_ = self.query(CampaignDisplay, "campaign", query_params=[{"key": "accountId", "comp": "==", "value": aacid}])
        request_fields = filter_campaign_display_request_fields(fields)
        # print('account query', account)
        for campaign in campaigns_:
            campaigns.append(campaign)
            # campaigns.append(D(campaign.to_dict(request_fields)))

        return campaigns
    
    def get(self, fields=None):
        if bool(self.id) is None:
            return None;
        request_fields = filter_campaign_display_request_fields(fields)
        doc = self.document_reference(self.id).get();
        if doc.exists is False:
            return None;
        data = {"id": doc.id, **doc.to_dict()}
        # print('created at===>', DateUtils.convert_firestore_timestamp_to_str(data['createdAt']))
        return CampaignDisplay.from_dict(campaign=CampaignDisplay.from_dict(campaign=data).to_dict(),  db=self.db, collection_name=self.collection_name);

    def getByUserId(self,id):
        campaigns = [];
        docs = self.collection().where('owner','==',id).get();
        for doc in docs:
            data = doc.to_dict();
            data['id'] = doc.id;
            campaigns.append(CampaignDisplay.from_dict(data))
        return campaigns;


    def create(self, data, account: any, uid):
        # creation_date = created_at * 1000
        # return DateUtils.from_timestamp(creation_date).isoformat()
        # try:
        data_create = DictUtils.dict_from_keys(data, CampaignDisplayFields().filtered_keys('mutable', True));
        if bool(data_create) is False:
            return None;
        campaign_dates = DateUtils.format_campaign_date(data_create)
        if "error" in campaign_dates and bool(campaign_dates["error"]) is True:
            return {"error": campaign_dates['error']}
        data_create = DictUtils.merge_dict({
            **campaign_dates['campaign'],
                "accountId": account.id,
                "owner": account.owner,
                "createdBy": f"users/${uid}"
            }, data_create,True)
        document_id = self.collection().document().id

        exist = self.query(CampaignDisplay, "campaign", [{"key": "name", "comp": "==", "value": data_create['name']}], True)
        if exist is not None:
            return {"error": f"Campaign name {data_create['name']} already exists"}
        doc_ref = self.collection().document(document_id);
        doc_ref.set({**data_create, 'createdAt': firestore.SERVER_TIMESTAMP}, True);
        time.sleep(2) 
        # campaign = CampaignDisplay.from_dict({"id": document_id, **data_create})
        campaign = CampaignDisplay.from_dict({"id": document_id}).get()
        if campaign is None:
            return {"error": "Failed to create campaign"};
        return campaign;  # Return the created campaign object.  # Return the created campaign object.  # Return the created campaign object.  # Return the created campaign object.  # Return the created campaign object.  # Return the created campaign object.  # Return the created campaign object.  # Return the created campaign object.  # Return the created campaign object.  # Return the created campaign object.  # Return the created campaign object.  # Return the
        # except Exception as e:
        #     print(e)
        #     return {"error": "Exception creating campaign"};
    def update(self, data):
        # try:
        last_value = self.to_dict();
        # print('last', last_value);
        filtered_value = pydash.pick(data, CampaignDisplayFields().filtered_keys('editable', True));
        # print('filtered', filtered_value);
        new_value = DictUtils.merge_dict(filtered_value, last_value, True);
        _changed_fields = DictUtils.compare_nested_objects(last_value, new_value);
        changed_fields = ArrayUtils.filter(DictUtils.get_keys(_changed_fields), lambda x: str(x).find('.') == -1)
        print('changed fields =>', changed_fields)
        data_update = DictUtils.dict_from_keys(filtered_value, changed_fields);
        if bool(data_update) is False:
            return {"status": "ok"};
        if 'startDate' in data_update or 'endDate' in data_update:
            dates = DateUtils.format_campaign_date(new_value, False)
            if dates is None  or ("error" in dates and bool(dates['error']) is True):
                return dates
        
            data_update = {**data_update, **dates['campaign']}
            changed_fields.extend(DictUtils.get_keys(data_update))

        # self.document_reference().set(data_update, merge=True)
        # return DictUtils.dict_from_keys(self.get(), changed_fields);
        fields = changed_fields
        print('fields', fields)
        print('data_update', data_update)
        return {"status": "ok", "data": DictUtils.filter_by_fields(CampaignDisplay.from_dict(campaign=data_update).to_dict(), fields)};
        # return {"status": "ok", "data": CampaignDisplay.from_dict(campaign=data_update).to_dict()};
        # return {"status": "ok", "data": DictUtils.filter_by_fields(self.get().to_dict(), fields)};
        # except Exception as e:
        #     print(e)
        #     return None;

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

