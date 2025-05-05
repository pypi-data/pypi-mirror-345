
from dataclasses import dataclass
from .....utils.utils import DictUtils
from datetime import datetime, timedelta
import os

GRANT_COLLECTION = os.environ.get('GRANT_COLLECTION');

def get_grant_expire_at(expires_in):
    return datetime.now() + timedelta(seconds=expires_in)
@dataclass
class GrantFields:
    id = "id"
    code = "code"
    uid = "uid"
    client_id = "client_id"
    redirect_uri = "redirect_uri"
    scopes = "scopes"
    scope = "scope"
    expires = "expires"
    code_challenge = "code_challenge"
    code_challenge_method = "code_challenge_method"
    nonce = "nonce"
    auth_time = "auth_time"

    @staticmethod
    def keys():
        return DictUtils.get_keys(GrantFieldsProps);

    @staticmethod
    def filtered_keys(field, condition=True):
        mutable = DictUtils.filter(GrantFieldsProps, DictUtils.get_keys(GrantFieldsProps), field, condition)
        return DictUtils.get_keys(mutable);

GrantFieldsProps = {
    GrantFields.id: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    GrantFields.code: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    GrantFields.uid: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    GrantFields.client_id: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    GrantFields.redirect_uri: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    GrantFields.scopes: {
        "type": list,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": [],
        "pickable": True
    },
    GrantFields.expires: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": get_grant_expire_at(120).isoformat(),
        "pickable": True
    },
    GrantFields.scope: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    GrantFields.code_challenge: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    GrantFields.code_challenge_method: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    GrantFields.nonce: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    GrantFields.auth_time: {
        "type": int,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": 0,
        "pickable": True
    },
}

STANDARD_FIELDS = GrantFields.filtered_keys('pickable', True)