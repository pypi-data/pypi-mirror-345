from ....base.firebase_collection import FirebaseCollectionBase
from .....utils import (DictUtils, init_class_kwargs, get_request_fields)
from .base_adgroup_fields import BaseAdGroupFieldsProps, STANDARD_FIELDS, BASE_ADGROUP_PICKABLE_FIELDS
from typing import Any
from dataclasses import dataclass

from ..ages import Ages
from ..genders import Genders
from ..devices import Devices


def filter_request_fields(fields, default_fields = BASE_ADGROUP_PICKABLE_FIELDS):
    request_fields = get_request_fields(fields, default_fields, [default_fields[0]])
    if request_fields is None or bool(request_fields) is False:
        request_fields = [default_fields[0]]
    return request_fields



@dataclass(init=False)
class BaseAdGroup(FirebaseCollectionBase):
    id: str
    campaign_id: int
    name: str
    status: str
    budget: int
    budgetId: int
    bid: float
    ages: list[Ages]
    genders: list[Genders]
    devicesTargeted: list[Devices]
    devicesExcluded: list[Devices]
    is_removed: bool
    isEnded: bool
    ad_group_id: int
    owner: str
    provider: str
    clientCustomerId: str
    __baseFields: BaseAdGroupFieldsProps

    def __init__(self, adgroup=None, collection_name=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, adgroup, STANDARD_FIELDS, BaseAdGroupFieldsProps, collection_name, ['id'], **kwargs)
        super().__init__(**data_args);
        for key in keys:
            if key == "ages":
                setattr(self, key, Ages().fromListDict(cls_object[key], Ages))
            elif key == "genders":
                setattr(self, key, Genders().fromListDict(cls_object[key], Genders))
            elif key == "devicesTargeted":
                setattr(self, key, Devices().fromListDict(cls_object[key], Devices))
            elif key == "devicesExcluded":
                setattr(self, key, Devices().fromListDict(cls_object[key], Devices))
            else:
                setattr(self, key, cls_object[key]) 


    @staticmethod
    def generate_model(_key_="default_value"):
        adgroup = {};
        props = BaseAdGroupFieldsProps
        for k in DictUtils.get_keys(props):
            adgroup[k] = props[k][_key_];
        return adgroup;

    
    def to_dict(self, fields=None):
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "name": self.name,
            "status": self.status,
            "budget": self.budget,
            "budgetId": self.budgetId,
            "bid": self.bid,
            "ages": Ages().toListDict(self.ages, None),
            "genders": Genders().toListDict(self.genders, None),
            "devicesTargeted": Devices().toListDict(self.devicesTargeted, None),
            "devicesExcluded": Devices().toListDict(self.devicesExcluded, None),
            "is_removed": self.is_removed,
            "ad_group_id": self.ad_group_id,
            "owner": self.owner,
            "provider": self.provider,
            "clientCustomerId": self.clientCustomerId
        }
        