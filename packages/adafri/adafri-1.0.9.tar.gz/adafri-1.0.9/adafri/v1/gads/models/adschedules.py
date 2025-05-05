from dataclasses import dataclass
from typing import Any
from  ....utils.utils import DictUtils, BaseFieldsClass, BaseClass, init_class_kwargs,get_object_model_class

@dataclass
class AdsSchedulesFields(BaseFieldsClass):
    id = "id"
    dayEN = "dayEN"
    dayFR = "dayFR"
    endHour = "endHour"
    endMinute = "endMinute"
    startHour = "startHour"
    startMinute = "startMinute"
    end_hour_text = "end_hour_text"
    start_hour_text = "start_hour_text"
    criterionId = "criterionId"
    criterionType = "criterionType"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass(init=False)
class AdsSchedules(BaseClass):
    id: str
    dayEN: str
    dayFR: str
    endHour: str
    endMinute: str
    startHour: str
    startMinute: str
    start_hour_text: str
    end_hour_text: str
    criterionId: int
    criterionType: str
    def __init__(self, schedules=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, schedules, None, None, None, [], **kwargs)
        for key in keys:
            setattr(self, key, cls_object[key]) 
    def to_dict(self, field=None):
        return DictUtils.remove_none_values({
            "id": self.id,
            "dayEn": self.dayEN,
            "endHour": self.endHour,
            "endMinute": self.endMinute,
            "startHour": self.startHour,
            "startMinute": self.startMinute,
            "start_hour_text": self.start_hour_text,
            "end_hour_text": self.end_hour_text,
            "criterionId": self.criterionId,
            "criterionType": self.criterionType,
        })
    @staticmethod
    def from_dict(obj: Any) -> 'AdsSchedules':
        cls_object, keys = get_object_model_class(obj, AdsSchedules, None);
        return AdsSchedules(cls_object)
        