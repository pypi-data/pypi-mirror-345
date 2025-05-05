from typing import Any
from dataclasses import dataclass
from .....utils import DictUtils, Crypto, get_object_model_class, pydash, init_class_kwargs
from ....base.firebase_collection import (FirebaseCollectionBase, getTimestamp)
from .code_fields import CodeFields, CodeFieldsProps, STANDARD_FIELDS, CODE_COLLECTION, get_code_expire_at, is_expired
from .....utils.response import ApiResponse, Error, ResponseStatus, StatusCode

@dataclass(init=False)
class Code(FirebaseCollectionBase):
    id: str
    code: str
    target: str
    code_type: str
    createdAt: any
    expired_at: str
    expires_in: int

    def __init__(self, code=None, **kwargs):
        if type(code) is str or type(code) is int:
            code = {"code": str(code), "code_type": "email_validation"} 
        (cls_object, keys, data_args) = init_class_kwargs(self, code, STANDARD_FIELDS, CodeFieldsProps, CODE_COLLECTION, ['id'], **kwargs)
        super().__init__(**data_args);
        for key in keys:
            setattr(self, key, cls_object[key]) 


    @staticmethod
    def generate_model(_key_="default_value"):
        code = {};
        props = CodeFieldsProps
        for k in DictUtils.get_keys(props):
            code[k] = props[k][_key_];
        return code;

    @staticmethod
    def from_dict(code: Any=None, db=None, collection_name=None) -> 'Code':
        cls_object, keys = get_object_model_class(code, Code, CodeFieldsProps);
        _client = Code(cls_object, db=db, collection_name=collection_name)
        return _client

    def query(self, query_params: list, first=False, limit=None):
        result = [];
        query_result = self.custom_query(query_params, first=first, limit=limit)
        if bool(query_result):
            if first is True:
                return Code.from_dict(code=query_result, db=self.db, collection_name=self.collection_name)
            else:
                for doc in query_result:
                    result.append(Code.from_dict(code=doc, db=self.db, collection_name=self.collection_name))
                return result
        if first:
                return None
        return [];

    def getCode(self) -> 'Code':
        if bool(self.id):
            doc = self.document_reference().get();
            if doc.exists is False:
                return None;
            return Code.from_dict(doc.to_dict(), db=self.db, collection_name=self.collection_name);
        if bool(self.code) and bool(self.code_type):
            params = [{"key": CodeFields.code, "comp": "==", "value": self.code}, {"key": CodeFields.code_type, "comp": "==", "value": self.code_type}]
            return self.query(params, True)
        return None;

    @staticmethod
    def generate(**kwargs) -> 'ApiResponse':
        data_dict = DictUtils.pick_fields(kwargs, CodeFields.filtered_keys('pickable', True));
        code_model = Code.from_dict(DictUtils.merge_dict(data_dict, Code.generate_model()));
        
        if bool(code_model.to_json()) is False:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("Empty request","INVALID_REQUEST", 1)).to_json()
        
        if bool(code_model.code) is False:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("name required","INVALID_REQUEST", 1));

        code_model.id = Crypto().generate_id(code_model.target+"~"+code_model.code_type+"~");
        code_model.expired_at = get_code_expire_at(code_model.expires_in).isoformat()
        return ApiResponse(ResponseStatus.OK, StatusCode.status_200, code_model, None);
    @staticmethod
    def get_id(cls, target, type):
        return Crypto().generate_id(target+"~"+type+"~");
    @staticmethod
    def create(**kwargs):
        authorization_code = Code().generate(**kwargs);
        if authorization_code.status == ResponseStatus.ERROR:
            return authorization_code
        
        authorization_code_model: Code = authorization_code.data;
        docRef = Code(authorization_code_model.to_json()).document_reference();
        # if docRef.get().exists:
        #     return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"Code with name {authorization_code.id} already exist","INVALID_REQUEST", 1));
        
        docRef.set({**authorization_code_model.to_json(), "createdAt": getTimestamp()}, merge=True);
        created_campaign = authorization_code_model.getCode()
        return ApiResponse(ResponseStatus.OK, StatusCode.status_200, created_campaign.to_json(), None);
    
    def update(self, data):
        try:
            last_value = self.to_json();
            filtered_value = pydash.pick(data, CodeFields.filtered_keys('editable', True));
            new_value = DictUtils.merge_dict(filtered_value, self.to_json());
            changed_fields = DictUtils.get_changed_field(last_value, new_value);
            data_update = DictUtils.dict_from_keys(filtered_value, changed_fields);
            if bool(data_update) is False:
                return None;
            self.document_reference().set(data_update, merge=True)
            return DictUtils.dict_from_keys(self.getCode().to_json(), changed_fields);
        except Exception as e:
            print(e)
            return None;
    
    def use_code(self):
        code = self.getCode();
        if code is None:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"Invalid code","INVALID_REQUEST", 1));
        if code.is_expired():
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"Expired code","INVALID_REQUEST", 1));
        remove = code.remove()
        if remove.status == ResponseStatus.ERROR:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"An error occurated","INVALID_REQUEST", 1));
        return ApiResponse(ResponseStatus.OK, StatusCode.status_200, {"message": "success"}, None);

    def remove(self):
        try:
            if self.id is None:
                return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"Cannot identify Authorization code with id {self.id} to delete","INVALID_REQUEST", 1));
            deleted = self.document_reference().delete();
            return ApiResponse(ResponseStatus.OK, StatusCode.status_200, {"message": f"Code {self.id} deleted"}, None);
        except Exception as e:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"An error occurated while removing authorization code with id {self.id} {str(e)}","INVALID_REQUEST", 1));

    def is_expired(self):
        return is_expired(self.expired_at)