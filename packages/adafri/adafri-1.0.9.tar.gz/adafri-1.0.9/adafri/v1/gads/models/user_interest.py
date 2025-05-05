from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, BaseFieldsClass, BaseClass,init_class_kwargs,get_object_model_class
from ...base.firebase_collection import FirebaseCollectionBase

@dataclass
class UserInterestFields(BaseFieldsClass):
    id = "id"
    name = "name"
    type = "type"
    userInterestParentId = "userInterestParentId"
    criterionId = "criterionId"
    criterionType = "criterionType"
    isTargeted = "isTargeted"
    isExcluded = "isExcluded"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


UserInterestFieldsProps = {
    UserInterestFields.id: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    UserInterestFields.name: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    UserInterestFields.type: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    UserInterestFields.criterionId: {
        "type": str or int or float,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    UserInterestFields.criterionType: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    UserInterestFields.userInterestParentId: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    UserInterestFields.isTargeted: {
        "type": bool,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    UserInterestFields.isExcluded: {
        "type": bool,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    }
}

@dataclass(init=False)
class UserInterest(FirebaseCollectionBase):
    id: str
    name: str
    type: str
    criterionType: str
    userInterestParentId: str
    criterionId: int
    isTrageted: bool
    isExcluded: bool
    __baseFields: UserInterestFieldsProps
    def __init__(self, user_interest=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, user_interest, None, None, None, [], **kwargs)
        super().__init__(**data_args);
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "criterionType": self.criterionType,
            "userInterestParentId": self.userInterestParentId,
            "criterionId": self.criterionId,
            "isTrageted": self.isTrageted,
            "isExcluded": self.isExcluded
        })
    @staticmethod
    def from_dict(user_interest = None, db=None, collection_name=None) -> 'UserInterest':
        cls_object, keys = get_object_model_class(user_interest, UserInterest, None);
        value  = UserInterest(cls_object);
        if db is not None:
            value.db = db
        if collection_name is not None:
            value.collection_name = collection_name
        return value
    
    def loadBrand(self):
        brands = self.query(UserInterest, "user_interest", [], False, None, "BRAND-user-interest-fr")
        if bool(brands) is True:
            return self.toListDict(brands, None);
        return []
    def loadInMarket(self):
        in_market = self.query(UserInterest, "user_interest", [], False, None, "IN_MARKET-user-interest-fr")
        if bool(in_market) is True:
            return self.toListDict(in_market, None);
        return []
    def loadMobileAppInstaller(self):
        mobile_app = self.query(UserInterest, "user_interest", [], False, None, "MOBILE_APP_INSTALL_USER-user-interest-fr")
        if bool(mobile_app) is True:
            return self.toListDict(mobile_app, None);
        return []
    def load(self):
        try:
            result = {};
            brands = self.loadBrand();
            if bool(brands) is True:
                result['brand'] = brands
            in_market = self.loadInMarket();
            if bool(in_market) is True:
                result['in_market'] = in_market
            mobile_app = self.loadMobileAppInstaller();
            if bool(mobile_app) is True:
                result['mobile_app_installer'] = mobile_app
            return result
        except Exception as e:
            print(str(e))
            return None;


