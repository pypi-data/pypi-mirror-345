from dataclasses import dataclass 
from ...models.adgroups.base_adgroup_fields import BaseAdGroupFields, BaseAdGroupFieldsProps
import os

DISPLAY_ADGROUPS_COLLECTION = os.environ.get('GADS_ADGROUPS_DISPLAY_COLLECTION');

@dataclass
class AdGroupDisplayFields(BaseAdGroupFields):
    targetedPlacements = "targetedPlacements"
    excludedPlacements = "excludedPlacements"
    websites = "websites"
    youtubeChannels = "youtubeChannels"
    youtubeVideos = "youtubeVideos"
    images = "images"
    imagesNative = "imagesNative"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)



AdGroupDisplayFieldsProps = {
    **BaseAdGroupFieldsProps,
    AdGroupDisplayFields.targetedPlacements: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    AdGroupDisplayFields.excludedPlacements: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    AdGroupDisplayFields.websites: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    AdGroupDisplayFields.youtubeChannels: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    AdGroupDisplayFields.youtubeVideos: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    AdGroupDisplayFields.images: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    AdGroupDisplayFields.imagesNative: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    }
}


STANDARD_FIELDS = AdGroupDisplayFields(fields_props=AdGroupDisplayFieldsProps).filtered_keys('pickable', True)
ADGROUP_DISPLAY_PICKABLE_FIELDS = AdGroupDisplayFields(fields_props=AdGroupDisplayFieldsProps).filtered_keys('pickable', True)
