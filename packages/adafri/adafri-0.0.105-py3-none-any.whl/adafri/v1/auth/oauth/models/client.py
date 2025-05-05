from ....base.firebase_collection import FirebaseCollectionBase
from .....utils import ArrayUtils, DictUtils, Crypto, get_object_model_class, init_class_kwargs
from .client_fields import ClientFields, ClientFieldProps, STANDARD_FIELDS, CLIENT_COLLECTION
from .....utils.response import ApiResponse, Error, ResponseStatus, StatusCode
from werkzeug.security import gen_salt
import time
from typing import Any
from dataclasses import dataclass
import json
from authlib.oauth2.rfc6749 import ClientMixin
from authlib.oauth2.rfc6749.util import list_to_scope, scope_to_list
import secrets
import pydash

ADAFRI_SCOPES = ["openid", "profile", "email", "profile", "profile.read", "profile.update", "accounts.read", "accounts.update", "accounts_management"]

@dataclass(init=False)
class OAuthClient(ClientMixin, FirebaseCollectionBase):
    id: str
    name: str
    uid: str
    description: str
    client_id: str
    client_secret: str
    uri: str
    grant_types: list[str]
    response_types: list[str]
    token_endpoint_auth_method: str
    redirect_uris: list[str]
    scopes: list[str]
    scope: str
    client_id_issued_at: int
    createdAt: any
    allowed_redirect_uris: list[str]
    default_redirect_uri: str
    allow_direct_grant_access: bool
    token_endpoint_auth_methods: list[str]
    
    def __init__(self, client=None, default_redirect_uri=None, **kwargs):
        if type(client) is str:
            client = {"client_id": client} 
        (cls_object, keys, data_args) = init_class_kwargs(self, client, STANDARD_FIELDS, ClientFieldProps, CLIENT_COLLECTION, ['id'], **kwargs)
        super().__init__(**data_args);
        for key in keys:
            setattr(self, key, cls_object[key])
        if getattr(self, 'allowed_redirect_uris',None) is None or bool(self.allowed_redirect_uris) is False:
            if getattr(self, 'redirect_uris',None) is not None:
                self.allowed_redirect_uris = self.redirect_uris
        #self.default_redirect_uri = default_redirect_uri


    @staticmethod
    def generate_model(_key_="default_value"):
        user = {};
        props = ClientFieldProps
        for k in DictUtils.get_keys(props):
            user[k] = props[k][_key_];
        return user;

    @staticmethod
    def from_dict(client = None, db=None, collection_name=None, default_redirect_uri=None) -> 'OAuthClient':
        cls_object, keys = get_object_model_class(client, OAuthClient, ClientFieldProps);
        _client = OAuthClient(cls_object, db=db, collection_name=collection_name, default_redirect_uri=default_redirect_uri)
        return _client

    def query(self, query_params: list, first=False, limit=None):
        result = [];
        query_result = self.custom_query(query_params, first=first, limit=limit)
        if bool(query_result):
            if first:
                return OAuthClient.from_dict(client=query_result, db=self.db, collection_name=self.collection_name, default_redirect_uri=getattr(self,  'default_redirect_uri', None))
            else:
                for doc in query_result:
                    result.append(OAuthClient.from_dict(client=doc, db=self.db, collection_name=self.collection_name, default_redirect_uri=getattr(self,  'default_redirect_uri', None)))
                return result
        if first:
                return None
        return [];

    def get_by_client_id(self, id) -> 'OAuthClient':
        if id is None or bool(id) is False:
            return None
        return self.query([{"key": "client_id", "comp": "==", "value": id}], True)
       

    def getOAuthClient(self) -> 'OAuthClient':
        if bool(self.id):
            doc = self.document_reference().get();
            if doc.exists is False:
                return None;
            return OAuthClient.from_dict(doc.to_dict(), db=self.db, collection_name=self.collection_name);
        if bool(self.client_id):
            return self.query([{"key": ClientFields.client_id, "comp": "==", "value": self.client_id}], True)

    @staticmethod
    def generate(**kwargs) -> 'ApiResponse':
        data_dict = DictUtils.pick_fields(kwargs, ClientFields.filtered_keys('mutable', True));
        client_model = OAuthClient.from_dict(DictUtils.merge_dict(data_dict, OAuthClient.generate_model()));
        
        if bool(client_model.to_json()) is False:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("Empty request","INVALID_REQUEST", 1)).to_json()
        
        if bool(client_model.name) is False:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("name required","INVALID_REQUEST", 1));
        
        if bool(client_model.uid) is False:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("uid required","INVALID_REQUEST", 1));

        client_model.client_id = gen_salt(24)
        client_model.id = Crypto().generate_id(client_model.name+"~"+client_model.uid+"~"+client_model.client_id);
        client_model.client_id_issued_at = int(time.time())
        
        if client_model.token_endpoint_auth_method == 'none':
            client_model.client_secret = ''
        else:
            client_model.client_secret = gen_salt(48)
        return ApiResponse(ResponseStatus.OK, StatusCode.status_200, client_model, None);
    
    def update(self, data):
        try:
            last_value = self.to_json();
            filtered_value = pydash.pick(data, ClientFields.filtered_keys('editable', True));
            new_value = DictUtils.merge_dict(filtered_value, self.to_json());
            changed_fields = DictUtils.get_changed_field(last_value, new_value);
            data_update = DictUtils.dict_from_keys(filtered_value, changed_fields);
            if bool(data_update) is False:
                return None;
            self.document_reference().set(data_update, merge=True)
            return DictUtils.dict_from_keys(self.getOAuthClient().to_json(), changed_fields);
        except Exception as e:
            print(e)
            return None;

    def get_default_redirect_uri(self):
        return self.redirect_uris[0]
    
    def check_response_type(self, response_type):
        return response_type in self.response_types
    
    def check_client_secret(self, client_secret):
        return secrets.compare_digest(self.client_secret, client_secret)
    
    def check_endpoint_auth_method(self, method, endpoint):
        if endpoint == 'token':
            # if client table has ``token_endpoint_auth_method``
            token_endpoint_auth_methods = getattr(self, 'token_endpoint_auth_methods', [])
            return self.token_endpoint_auth_method == method or method in token_endpoint_auth_methods
        return True
    
    def check_grant_type(self, grant_type):
        return grant_type in self.grant_types
    
    def get_allowed_scope(self, scope):
        if not scope:
            return ''
        allowed = set(scope_to_list(self.scope))
        return list_to_scope([s for s in scope.split() if s in allowed])
    
    def check_redirect_uri(self, redirect_uri):
        return redirect_uri in self.allowed_redirect_uris

    def get_client_id(self):
        return self.client_id
    