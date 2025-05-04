from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, BaseFieldsClass,init_class_kwargs
import os

@dataclass
class BaseAdgroupFields(BaseFieldsClass):
    id = "id"
    name = "name"
    campaign_id = "campaign_id"
    ad_group_id = "ad_group_id"
    status = "status"
    ages = "ages"
    genders = "genders"
    clientCustomerId = "clientCustomerId"
    servingStatus = "servingStatus"
    owner = "owner"
    accountId = "accountId"
    createdAt = "createdAt"
    createdBy = "createdBy"
    devicesTargeted = "devicesTargeted"
    devicesExcluded = "devicesExcluded"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)



BaseAdgroupFieldsProps = {
    BaseAdgroupFields.id: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdgroupFields.name: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdgroupFields.status: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": 0
    },
    BaseAdgroupFields.owner: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdgroupFields.accountId: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdgroupFields.campaign_id: {
        "type": int,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": 0
    },
    BaseAdgroupFields.ad_group_id: {
        "type": int,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": 0
    },
    BaseAdgroupFields.ages: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdgroupFields.genders: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdgroupFields.clientCustomerId: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdgroupFields.createdBy: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdgroupFields.createdAt: {
        "type": (int or str),
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    }
}


STANDARD_FIELDS = BaseAdgroupFields(fields_props=BaseAdgroupFieldsProps).filtered_keys('pickable', True)
BASE_ADGROUP_PICKABLE_FIELDS = BaseAdgroupFields(fields_props=BaseAdgroupFieldsProps).filtered_keys('pickable', True)
