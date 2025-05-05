from dataclasses import dataclass
from  .....utils.utils import BaseFieldsClass


@dataclass
class BaseAdGroupFields(BaseFieldsClass):
    id = "id"
    campaign_id = "campaign_id"
    ad_group_id = "ad_group_id"
    name = "name"
    status = "status"
    budget = "budget"
    owner = "owner"
    createdAt = "createdAt"
    createdBy = "createdBy"
    accountId = "accountId"
    is_removed = "is_removed"
    ages = "ages"
    genders = "genders"
    devicesTargeted = "devicesTargeted"
    devicesExcluded = "devicesExcluded"
    clientCustomerId = "clientCustomerId"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)



BaseAdGroupFieldsProps = {
    BaseAdGroupFields.id: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdGroupFields.name: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdGroupFields.status: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ''
    },
    BaseAdGroupFields.budget: {
        "type": (int or float),
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": 0
    },
    BaseAdGroupFields.owner: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdGroupFields.accountId: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdGroupFields.campaign_id: {
        "type": int,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": 0
    },
    BaseAdGroupFields.ad_group_id: {
        "type": int,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": 0
    },
    BaseAdGroupFields.is_removed: {
        "type": bool,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": False
    },
    BaseAdGroupFields.ages: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdGroupFields.genders: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdGroupFields.clientCustomerId: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdGroupFields.createdBy: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdGroupFields.createdAt: {
        "type": (int or str),
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseAdGroupFields.devicesTargeted: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    BaseAdGroupFields.devicesExcluded: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    }
}


STANDARD_FIELDS = BaseAdGroupFields(fields_props=BaseAdGroupFieldsProps).filtered_keys('pickable', True)
BASE_ADGROUP_PICKABLE_FIELDS = BaseAdGroupFields(fields_props=BaseAdGroupFieldsProps).filtered_keys('pickable', True)

