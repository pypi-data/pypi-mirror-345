from dataclasses import dataclass
from  .....utils.utils import DictUtils, BaseFieldsClass 
from ...models.base_campaign_fields import BaseCampaignFields, BaseCampaignFieldsProps
import os

DISPLAY_COLLECTION = os.environ.get('GADS_DISPLAY_COLLECTION');

@dataclass
class CampaignDisplayFields(BaseCampaignFields):
    targetedPlacements = "targetedPlacements"
    excludedPlacements = "excludedPlacements"
    websites = "websites"
    youtubeChannels = "youtubeChannels"
    youtubeVideos = "youtubeVideos"
    images = "images"
    imagesNative = "imagesNative"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.class_fields_props = CampaignDisplayFieldsProps



CampaignDisplayFieldsProps = {
    **BaseCampaignFieldsProps,
    BaseCampaignFields.type: {
        "type": str,
        "required": False,
        "mutable": False,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": "DISPLAY"
    },
    CampaignDisplayFields.targetedPlacements: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    CampaignDisplayFields.excludedPlacements: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    CampaignDisplayFields.websites: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    CampaignDisplayFields.youtubeChannels: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    CampaignDisplayFields.youtubeVideos: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    CampaignDisplayFields.images: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    },
    CampaignDisplayFields.imagesNative: {
        "type": list,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "pickable": True,
        "default_value": []
    }
}


STANDARD_FIELDS = CampaignDisplayFields(fields_props=CampaignDisplayFieldsProps).filtered_keys('pickable', True)
CAMPAIGN_DISPLAY_PICKABLE_FIELDS = CampaignDisplayFields(fields_props=CampaignDisplayFieldsProps).filtered_keys('pickable', True)
