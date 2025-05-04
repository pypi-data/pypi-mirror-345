
from dataclasses import dataclass
from .....utils.utils import DictUtils
from datetime import datetime, timedelta
import os

CODE_COLLECTION = os.environ.get('CODE_COLLECTION');


def is_expired(expired_at):
    return datetime.fromisoformat(expired_at) < datetime.now()

def get_code_expire_at(expires_in):
    return datetime.now() + timedelta(seconds=expires_in)

@dataclass
class CodeFields:
    id = "id"
    code = "code"
    target = "target"
    code_type = "code_type"
    createdAt = "created_at"
    expired_at = "expired_at"
    expires_in = "expires_in"

    @staticmethod
    def keys():
        return DictUtils.get_keys(CodeFieldsProps);

    @staticmethod
    def filtered_keys(field, condition=True):
        mutable = DictUtils.filter(CodeFieldsProps, DictUtils.get_keys(CodeFieldsProps), field, condition)
        return DictUtils.get_keys(mutable);

CodeFieldsProps = {
    CodeFields.id: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    CodeFields.code: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    CodeFields.code_type: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    CodeFields.target: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    CodeFields.createdAt: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True
    },
    CodeFields.expires_in: {
        "type": int,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": 900,
        "pickable": True
    },
    CodeFields.expired_at: {
        "type": float,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "default_value": get_code_expire_at(900).isoformat(),
        "pickable": True
    },

    
}
STANDARD_FIELDS = CodeFields.filtered_keys('pickable', True)