from dataclasses import dataclass
from typing import Any
from  ....utils.utils import BaseFieldsClass
from google.cloud.firestore_v1.document import Timestamp
from google.api_core.datetime_helpers import DatetimeWithNanoseconds


@dataclass
class BaseCampaignFields(BaseFieldsClass):
    id = "id"
    id_campagne = "id_campagne"
    name = "name"
    objective = "objective"
    adChannel = "adChannel"
    status = "status"
    startDate = "startDate"
    endDate = "endDate"
    startDateFormattedGoogle = "startDateFormattedGoogle"
    endDateFormattedGoogle = "endDateFormattedGoogle"
    areaTargetedOption = "areaTargetedOption"
    areaExcludedOption = "areaExcludedOption"
    budget = "budget"
    budgetId = "budgetId"
    dailyBudget = "dailyBudget"
    bid = "bid"
    urlPromote = "urlPromote"
    strategie = "strategie"
    deliveryMethod = "deliveryMethod"
    trackingTemplate = "trackingTemplate"
    finalUrlSuffix = "finalUrlSuffix"
    urlCustomParameters = "urlCustomParameters"
    clientCustomerId = "clientCustomerId"
    servingStatus = "servingStatus"
    owner = "owner"
    createdAt = "createdAt"
    createdBy = "createdBy"
    endedAt = "endedAt"
    isPayed = "isPayed"
    isEnded = "isEnded"
    type = "type"
    accountId = "accountId"
    is_removed = "is_removed"
    targetedLocations = "targetedLocations"
    excludedLocations = "excludedLocations"
    ages = "ages"
    genders = "genders"
    devicesTargeted = "devicesTargeted"
    devicesExcluded = "devicesExcluded"
    adsSchedules = "adsSchedules"
    budgetEnded = "budgetEnded"
    publish = "publish"
    publishing = "publishing"
    ad_group_id = "ad_group_id"
    ad_group_id_firebase = "ad_group_id_firebase"
    publicationDate = "publicationDate"
    provider = "provider"
    isComplete = "isComplete"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)



BaseCampaignFieldsProps = {
    BaseCampaignFields.id: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.name: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.status: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": "ENABLED"
    },
    BaseCampaignFields.startDate: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.endDate: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.startDateFormattedGoogle: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": False,
        "default_value": None
    },
    BaseCampaignFields.endDateFormattedGoogle: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": False,
        "default_value": None
    },
    BaseCampaignFields.strategie: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": "CPM"
    },
    BaseCampaignFields.bid: {
        "type": float,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": 0.1
    },
    BaseCampaignFields.budget: {
        "type": [int,float],
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.budgetId: {
        "type": int,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.urlPromote: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.objective: {
        "type": dict,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": {"obj_id": "6"}
    },
    BaseCampaignFields.adChannel: {
        "type": dict,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": {"obj_id": 'display'}
    },
    BaseCampaignFields.provider: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.type: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.owner: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.accountId: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.id_campagne: {
        "type": int,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.ad_group_id: {
        "type": int,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.ad_group_id_firebase: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.isEnded: {
        "type": bool,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": False
    },
    BaseCampaignFields.isPayed: {
        "type": bool,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": False
    },
    BaseCampaignFields.is_removed: {
        "type": bool,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": False
    },
    BaseCampaignFields.finalUrlSuffix: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.trackingTemplate: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.urlCustomParameters: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.publish: {
        "type": bool,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": False
    },
    BaseCampaignFields.publishing: {
        "type": bool,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": False
    },
    BaseCampaignFields.isComplete: {
        "type": bool,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": False
    },
    BaseCampaignFields.budgetEnded: {
        "type": bool,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": False
    },
    BaseCampaignFields.publicationDate: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    BaseCampaignFields.areaTargetedOption: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.areaExcludedOption: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.ages: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.genders: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.servingStatus: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.clientCustomerId: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.createdBy: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.createdAt: {
        "type": [int, str, Timestamp, DatetimeWithNanoseconds],
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.adsSchedules: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.deliveryMethod: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    BaseCampaignFields.targetedLocations: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    BaseCampaignFields.excludedLocations: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    BaseCampaignFields.devicesTargeted: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    BaseCampaignFields.devicesExcluded: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    }
}


STANDARD_FIELDS = BaseCampaignFields(fields_props=BaseCampaignFieldsProps).filtered_keys('pickable', True)
BASE_CAMPAIGN_PICKABLE_FIELDS = BaseCampaignFields(fields_props=BaseCampaignFieldsProps).filtered_keys('pickable', True) + ['objective.primary']
