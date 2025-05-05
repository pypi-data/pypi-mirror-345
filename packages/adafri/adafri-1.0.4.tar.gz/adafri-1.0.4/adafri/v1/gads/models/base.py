from ...base.firebase_collection import FirebaseCollectionBase
from ....utils import (DictUtils, DateUtils, get_object_model_class, init_class_kwargs, BaseClass, get_request_fields, RequestFields)
from ....utils.response import ApiResponse, Error, ResponseStatus, StatusCode
from .base_campaign_fields import BaseCampaignFieldsProps, STANDARD_FIELDS, BASE_CAMPAIGN_PICKABLE_FIELDS
from typing import Any
from dataclasses import dataclass

from .objective import Objective
from .adchannel import AdChannel
from .ages import Ages
from .genders import Genders
from .locations import Location
from .adschedules import AdsSchedules
from .custom_parameters import CustomParameters
from .devices import Devices


def filter_request_fields(fields, default_fields = BASE_CAMPAIGN_PICKABLE_FIELDS):
    request_fields = get_request_fields(fields, default_fields, [default_fields[0]])
    if request_fields is None or bool(request_fields) is False:
        request_fields = [default_fields[0]]
    return request_fields



@dataclass(init=False)
class BaseCampaign(FirebaseCollectionBase):
    id: str
    id_campagne: int
    name: str
    status: str
    objective: Objective
    adChannel: AdChannel
    startDate: str
    endDate: str
    startDateFormattedGoogle: str
    endDateFormattedGoogle: str
    areaTargetedOption: str
    areaExcludedOption: str
    budget: int
    budgetId: int
    dailyBudget: int
    bid: float
    urlPromote: str
    strategie: str
    ages: list[Ages]
    genders: list[Genders]
    targetedLocations: list[Location]
    excludedLocations: list[Location]
    devicesTargeted: list[Devices]
    devicesExcluded: list[Devices]
    deliveryMethod: str
    trackingTemplate: str
    finalUrlSuffix: str
    accountId: str
    type: str
    is_removed: bool
    isEnded: bool
    isComplete: bool
    isPayed: bool
    publish: bool
    publishing: bool
    budgetEnded: bool
    ad_group_id: int
    ad_group_id_firebase: str
    servingStatus: str
    owner: str
    provider: str
    urlCustomParameters: list[CustomParameters]
    adsSchedules: list[AdsSchedules]
    createdAt: any
    createdBy: any
    clientCustomerId: str
    __baseFields: BaseCampaignFieldsProps

    def __init__(self, campaign=None, collection_name=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, campaign, STANDARD_FIELDS, BaseCampaignFieldsProps, collection_name, ['id'], **kwargs)
        super().__init__(**data_args);
        for key in keys:
            if key == "objective":
                setattr(self, key, Objective().from_dict(cls_object[key]))
            elif key == "adChannel":
                setattr(self, key, AdChannel().from_dict(cls_object[key]))
            elif key == "ages":
                setattr(self, key, Ages().fromListDict(cls_object[key]))
            elif key == "genders":
                setattr(self, key, Genders().fromListDict(cls_object[key]))
            elif key == "targetedLocations":
                setattr(self, key, Location().fromListDict(cls_object[key]))
            elif key == "excludedLocations":
                setattr(self, key, Location().fromListDict(cls_object[key]))
            elif key == "devicesTargeted":
                setattr(self, key, Devices().fromListDict(cls_object[key]))
            elif key == "devicesExcluded":
                setattr(self, key, Devices().fromListDict(cls_object[key]))
            elif key == "urlCustomParameters":
                setattr(self, key, CustomParameters().fromListDict(cls_object[key]))
            elif key == "adsSchedules":
                setattr(self, key, AdsSchedules().fromListDict(cls_object[key]))
            elif key == "createdAt":
                # print('created at int', type(cls_object[key]))
                setattr(self, key, cls_object[key]) 
            else:
                setattr(self, key, cls_object[key]) 


    @staticmethod
    def generate_model(_key_="default_value"):
        campaign = {};
        props = BaseCampaignFieldsProps
        for k in DictUtils.get_keys(props):
            campaign[k] = props[k][_key_];
        return campaign;

    
    def to_dict(self, fields=None):
        createdAt = DateUtils.convert_firestore_timestamp_to_str(self.createdAt)
        return DictUtils.remove_none_values({
            "id": self.id,
            "id_campagne": self.id_campagne,
            "name": self.name,
            "status": self.status,
            "objective": self.objective.to_dict(None),
            "adChannel": self.adChannel.to_dict(None),
            "startDate": self.startDate,
            "endDate": self.endDate,
            "startDateFormattedGoogle": self.startDateFormattedGoogle,
            "endDateFormattedGoogle": self.endDateFormattedGoogle,  
            "areaTargetedOption": self.areaTargetedOption,
            "areaExcludedOption": self.areaExcludedOption,  
            "budget": self.budget,
            "budgetId": self.budgetId,
            "dailyBudget": self.dailyBudget,
            "bid": self.bid,
            "urlPromote": self.urlPromote,
            "strategie": self.strategie,
            "ages": Ages().toListDict(self.ages, None),
            "genders": Genders().toListDict(self.genders, None),
            "targetedLocations": Location().toListDict(self.targetedLocations, None),
            "excludedLocations": Location().toListDict(self.excludedLocations, None),
            "devicesTargeted": Devices().toListDict(self.devicesTargeted, None),
            "devicesExcluded": Devices().toListDict(self.devicesExcluded, None),
            "deliveryMethod": self.deliveryMethod,
            "trackingTemplate": self.trackingTemplate,
            "finalUrlSuffix": self.finalUrlSuffix,
            "accountId": self.accountId,
            "type": self.type,
            "is_removed": self.is_removed,
            "isEnded": self.isEnded,
            "isComplete": self.isComplete,
            "isPayed": self.isPayed,
            "publish": self.publish,
            "publishing": self.publishing,
            "budgetEnded": self.budgetEnded,
            "ad_group_id": self.ad_group_id,
            "ad_group_id_firebase": self.ad_group_id_firebase,
            "servingStatus": self.servingStatus,
            "owner": self.owner,
            "provider": self.provider,
            "urlCustomParameters": CustomParameters().toListDict(self.urlCustomParameters, None),
            "adsSchedules": AdsSchedules().toListDict(self.adsSchedules, None),
            "clientCustomerId": self.clientCustomerId,
            "createdAt": createdAt,
            "createdBy": self.createdBy
        })
        