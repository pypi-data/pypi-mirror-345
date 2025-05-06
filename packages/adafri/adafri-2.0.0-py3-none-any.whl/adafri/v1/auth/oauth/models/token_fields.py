from dataclasses import dataclass
from .....utils import DictUtils
from datetime import datetime, timedelta
import os

TOKEN_COLLECTION = os.environ.get('TOKEN_COLLECTION');

def get_token_expire_at(expires_in):
    return datetime.now() + timedelta(seconds=expires_in)


def is_expired(expired_at):
    return datetime.fromisoformat(expired_at) < datetime.now()

@dataclass
class TokenFields:
    id = "id"
    client_id = "client_id"
    uid = "uid"
    token_type = "token_type"
    access_token = "access_token"
    refresh_token = "refresh_token"
    scopes = "scopes"
    scope = "scope"
    expires_in = "expires_in"
    expired_at = "expired_at"
    expires = "expires"
    type = "type"

    @staticmethod
    def keys():
        return DictUtils.get_keys(TokenFieldsProps);

    @staticmethod
    def filtered_keys(field, condition=True):
        mutable = DictUtils.filter(TokenFieldsProps, DictUtils.get_keys(TokenFieldsProps), field, condition)
        return DictUtils.get_keys(mutable);

TokenFieldsProps = {
    TokenFields.id: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    TokenFields.client_id: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    TokenFields.scope: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    TokenFields.uid: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    TokenFields.token_type: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    TokenFields.type: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    TokenFields.access_token: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    TokenFields.refresh_token: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    TokenFields.scopes: {
        "type": list,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": [],
        "pickable": True
    },
    TokenFields.expires: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    TokenFields.expires_in: {
        "type": int,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": None,
        "pickable": True
    },
    TokenFields.expired_at: {
        "type": float,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": None,
        # "default_value": get_token_expire_at(3600).isoformat(),
        "pickable": True
    },
}

STANDARD_FIELDS = TokenFields.filtered_keys('pickable', True)