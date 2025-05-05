from typing import Any
from dataclasses import dataclass
import json
from .utils import JsonEncoder
from enum import Enum

class ResponseStatus:
    OK = 'ok'
    ERROR = 'error'

class StatusCode:
    status_200 = 200
    status_400 = 400

@dataclass
class Error:
    message: str
    name: str
    error_code: int = 1

    @staticmethod
    def from_dict(obj: Any) -> 'Error':
        _message = str(obj.get("message"))
        _name = str(obj.get("name"))
        _error_code = "1"
        code = obj.get("error_code")
        if code is not None:
            _error_code = int(str(code))
        return Error(_message, _name, _error_code)

@dataclass
class ApiResponse:
    status: str
    status_code: int
    data: Any
    error: Error

    @staticmethod
    def from_dict(obj: Any) -> 'ApiResponse':
        _status = str(obj.get("status"))
        _status_code = int(obj.get("status_code"))
        _data = obj.get("data")
        _error = Error.from_dict(obj.get("error"))
        return ApiResponse(_status, _status_code, _data, _error)
    
    def to_json(self):
        return self.to_dict()

    def to_dict(self, fields=None):
        values = {
            "status": self.status,
            "status_code": self.status_code,
            "data": self.data,
            "error": self.error
        }
        if 'data' in values and values['data'] is None:
            del values['data']
        if 'error' in values and values['error'] is None:
            del values['error']
        return values

    # def to_json(self):
    #     return json.loads(JsonEncoder().encode(self))
