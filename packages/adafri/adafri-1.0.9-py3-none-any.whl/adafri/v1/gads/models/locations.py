from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, BaseFieldsClass, BaseClass,init_class_kwargs,get_object_model_class,get_request_fields


@dataclass
class LocationFields(BaseFieldsClass):
    id = "id"
    locationName = "locationName"
    displayType = "displayType"
    targetingStatus = "targetingStatus"
    reach = "reach"
    canonicalName = "canonicalName"
    criterionId = "criterionId"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.class_fields_props = LocationFieldsProps


LocationFieldsProps = {
    LocationFields.id: {
        "type": int,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    LocationFields.locationName: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    LocationFields.canonicalName: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    LocationFields.displayType: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    LocationFields.displayType: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    LocationFields.targetingStatus: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    },
    LocationFields.reach: {
        "type": int,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "pickable": True,
        "default_value": None
    }
}

@dataclass(init=False)
class Location(BaseClass):
    id: str
    locationName: str
    displayType: str
    targetingStatus: str
    reach: str
    canonicalName: str
    criterionId: int
    def __init__(self, location=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, location, None, None, None, [], **kwargs)
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "id": self.id,
            "locationName": self.locationName,
            "targetingStatus": self.targetingStatus,
            "reach": self.reach,
            "canonicalName": self.canonicalName,
            "criterionId": self.criterionId
        })
    @staticmethod
    def from_dict(obj: Any) -> 'Location':
        cls_object, keys = get_object_model_class(obj, Location, None);
        return Location(cls_object)
    
def filter_locations_request_fields(fields, default_fields = LocationFields().filtered_keys('pickable')):
    request_fields = get_request_fields(fields, default_fields, None)
    if request_fields is None or bool(request_fields) is False:
        request_fields = [default_fields[0]]
    return request_fields