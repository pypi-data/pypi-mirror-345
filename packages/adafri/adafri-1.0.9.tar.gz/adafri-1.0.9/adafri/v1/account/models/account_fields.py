from dataclasses import dataclass
from  ....utils.utils import DictUtils, BaseFieldsClass 
import os

ACCOUNT_COLLECTION = os.environ.get('ACCOUNT_COLLECTION');
ACCOUNT_LINK_COLLECTION = os.environ.get('ACCOUNT_LINK_COLLECTION');

@dataclass
class AccountFields(BaseFieldsClass):
    id = "id"
    aacid = "aacid"
    account_value = "account_value"
    creationDate = "creationDate"
    creationDateString = "creationDateString"
    name = "name"
    owner = "owner"
    owner_email = "owner_email"
    status = "status"
    totalClics = "totalClics"
    totalCosts = "totalCosts"
    totalImpressions = "totalImpressions"
    usedPackTest = "usedPackTest"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass
class AccountLinkFields(BaseFieldsClass):
    id = "id"
    linkDate = "linkDate"
    linkDateString = "linkDateString"
    owner = "owner"
    owner_email = "owner_email"
    target = "target"
    target_email = "target_email"
    status = "status"
    linked_account = "linked_account"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)



AccountFieldProps = {
    AccountFields.id: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountFields.aacid: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountFields.account_value: {
        "type": (int or float),
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": 0
    },
    AccountFields.creationDateString: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": False,
        "pickable": True,
        "default_value": ""
    },
    AccountFields.creationDate: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountFields.name: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountFields.owner: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountFields.owner_email: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountFields.status: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountFields.totalClics: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountFields.totalCosts: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountFields.totalImpressions: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountFields.usedPackTest: {
        "type": bool,
        "required": False,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": False
    }
}
AccountLinkFieldProps = {
    AccountLinkFields.id: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountLinkFields.linkDate: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountLinkFields.linkDateString: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountLinkFields.owner: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountLinkFields.owner_email: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountLinkFields.target: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountLinkFields.target_email: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountLinkFields.status: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": ""
    },
    AccountLinkFields.linked_account: {
        "type": dict,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    }
}

STANDARD_FIELDS = AccountFields(fields_props=AccountFieldProps).filtered_keys('pickable', True)
ACCOUNT_PICKABLE_FIELDS = AccountFields(fields_props=AccountFieldProps).filtered_keys('pickable', True)
LINK_STANDARD_FIELDS = AccountLinkFields(fields_props=AccountLinkFieldProps).filtered_keys('pickable', True)
