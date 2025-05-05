from .....utils import ArrayUtils, DictUtils, Crypto, get_object_model_class, init_class_kwargs
from ....base.firebase_collection import (FirebaseCollectionBase, getTimestamp)
from .grant_fields import GrantFields, GrantFieldsProps, STANDARD_FIELDS, GRANT_COLLECTION
from .....utils.response import ApiResponse, Error, ResponseStatus, StatusCode
from .....utils.utils import read_file
from typing import Any
from dataclasses import dataclass
from authlib.oauth2.rfc6749 import AuthorizationCodeMixin
from authlib.oauth2.rfc6749 import grants
from authlib.common.urls import add_params_to_uri
from authlib.oauth2.rfc6749.util import list_to_scope, scope_to_list
from authlib.oauth2.rfc6749.errors import AccessDeniedError
from ....user import User
import pydash
import json
from authlib.oidc.core.grants import (
    OpenIDCode as _OpenIDCode,
    OpenIDImplicitGrant as _OpenIDImplicitGrant,
    OpenIDHybridGrant as _OpenIDHybridGrant,
    OpenIDToken
)
from authlib.oidc.core import UserInfo

from werkzeug.security import gen_salt
from authlib.oidc.core.grants.util import create_response_mode_response

import os
import pydash
import time
from joserfc.jwk import RSAKey
import requests

@dataclass(init=False)
class OAuthGrant(AuthorizationCodeMixin, FirebaseCollectionBase):
    id: str
    code: str
    nonce: str
    uid: str
    client_id: str
    redirect_uri: str
    scopes: list[str]
    scope: str
    expires: str
    code_challenge: str
    code_challenge_method: str
    auth_time: int
    
    def __init__(self, grant=None, **kwargs):
        if type(grant) is str:
            grant = {"code": grant} 
        (cls_object, keys, data_args) = init_class_kwargs(self, grant, STANDARD_FIELDS, GrantFieldsProps, GRANT_COLLECTION, ['id'], **kwargs)
        super().__init__(**data_args);
        for key in keys:
            setattr(self, key, cls_object[key]) 
        # kwargs['fields'] = STANDARD_FIELDS
        # kwargs['fields_props'] = GrantFieldsProps
        # collection_name = getattr(kwargs, 'collection_name', None)
        # documentId = getattr(cls_object, 'id', None)
        # if documentId is not None:
        #     kwargs['documentId'] = documentId;
        # if collection_name is None:
        #     kwargs['collection_name'] = GRANT_COLLECTION;
        


    @staticmethod
    def generate_model(_key_="default_value"):
        grant = {};
        props = GrantFieldsProps
        for k in DictUtils.get_keys(props):
            grant[k] = props[k][_key_];
        return grant;

    @staticmethod
    def from_dict(grant: Any=None, db=None, collection_name=None) -> 'OAuthGrant':
        cls_object, keys = get_object_model_class(grant, OAuthGrant, GrantFieldsProps);
        _client = OAuthGrant(cls_object, db=db, collection_name=collection_name)
        return _client

    def query(self, query_params: list, first=False, limit=None):
        result = [];
        query_result = self.custom_query(query_params, first=first, limit=limit)
        if bool(query_result):
            if first:
                return OAuthGrant.from_dict(grant=query_result, db=self.db, collection_name=self.collection_name)
            else:
                for doc in query_result:
                    result.append(OAuthGrant.from_dict(grant=doc, db=self.db, collection_name=self.collection_name))
                return result
        if first:
                return None
        return [];

    def getOAuthGrant(self) -> 'OAuthGrant':
        if bool(self.id):
            doc = self.document_reference(self.id).get();
            if doc.exists is False:
                return None;
            return OAuthGrant.from_dict(doc.to_dict(), db=self.db, collection_name=self.collection_name);
        if bool(self.code):
            return self.query([{"key": GrantFields.code, "comp": "==", "value": self.code}], True)

    @staticmethod
    def generate(**kwargs) -> 'ApiResponse':
        data_dict = DictUtils.pick_fields(kwargs, GrantFields.filtered_keys('mutable', True));
        authorization_code_model = OAuthGrant.from_dict(DictUtils.merge_dict(data_dict, OAuthGrant.generate_model()));
        
        if bool(authorization_code_model.to_json()) is False:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("Empty request","INVALID_REQUEST", 1)).to_json()
        
        if bool(authorization_code_model.code) is False:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("name required","INVALID_REQUEST", 1));

        authorization_code_model.id = Crypto().generate_id(authorization_code_model.uid+"~"+authorization_code_model.client_id);
        return ApiResponse(ResponseStatus.OK, StatusCode.status_200, authorization_code_model, None);

    def get_redirect_uri(self):
        return self.redirect_uri
    
    def get_scope(self):
       return self.scope
    
    @staticmethod
    def create(**kwargs):
        authorization_code = OAuthGrant().generate(**kwargs);
        if authorization_code.status == ResponseStatus.ERROR:
            return authorization_code
        
        authorization_code_model: OAuthGrant = authorization_code.data;
        docRef = OAuthGrant(authorization_code_model.to_json()).document_reference();
        # if docRef.get().exists:
        #     return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"Code with name {authorization_code.id} already exist","INVALID_REQUEST", 1));
        
        docRef.set({**authorization_code_model.to_json(), "createdAt": getTimestamp()}, merge=True);
        created_grant = authorization_code_model.getOAuthGrant()
        return ApiResponse(ResponseStatus.OK, StatusCode.status_200, created_grant.to_json(), None);
    
    def update(self, data):
        try:
            last_value = self.to_json();
            filtered_value = pydash.pick(data, GrantFields.filtered_keys('editable', True));
            new_value = DictUtils.merge_dict(filtered_value, self.to_json());
            changed_fields = DictUtils.get_changed_field(last_value, new_value);
            data_update = DictUtils.dict_from_keys(filtered_value, changed_fields);
            if bool(data_update) is False:
                return None;
            self.document_reference().set(data_update, merge=True)
            return DictUtils.dict_from_keys(self.getOAuthGrant().to_json(), changed_fields);
        except Exception as e:
            print(e)
            return None;
    
    def remove(self):
        try:
            if self.id is None:
                return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"Cannot identify Authorization code with id {self.id} to delete","INVALID_REQUEST", 1));
            deleted = self.document_reference().delete();
            return ApiResponse(ResponseStatus.OK, StatusCode.status_200, {"message": f"Authorization code {self.id} deleted"}, None);
        except:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"An error occurated while removing authorization code with id {self.id}","INVALID_REQUEST", 1));

    def get_nonce(self):
        return self.nonce
    def get_auth_time(self):
        self.auth_time

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = [
        'client_secret_basic',
        'client_secret_post',
        'none'
    ]
    def save_authorization_code(self, code, request):
        code_challenge = request.data.get('code_challenge')
        code_challenge_method = request.data.get('code_challenge_method')
        redirect_uri = request.redirect_uri;
        scope = request.args.get("scope")
        if request.args.get("redirect_uri") is not None:
            redirect_uri = request.args.get("redirect_uri");
        if redirect_uri is None:
            default_redirect_uri =os.environ.get('DEFAULT_REDIRECT_URI')
            redirect_uri = default_redirect_uri
        model = {
            "client_id": request.client.client_id,
            "code": code,
            "redirect_uri": redirect_uri,
            "scopes": scope_to_list(scope),
            "scope": scope,
            "uid": request.user.uid,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method
        }
        auth_code_request = OAuthGrant.create(**model)
        auth_code = auth_code_request.data
        return auth_code

    
    def query_authorization_code(self, code, client):
        query_params = [{"key": GrantFields.code, "comp": "==","value": code}, {"key": GrantFields.client_id, "comp": "==","value": client.client_id}]
        auth_code = OAuthGrant().query(query_params=query_params, first=True)
        #if auth_code and not auth_code.is_expired():
        return auth_code

    def delete_authorization_code(self, authorization_code):
        remove = OAuthGrant(authorization_code.to_json()).remove()
        print('removing authorization code', authorization_code.id)

    def authenticate_user(self, authorization_code):
        return User({"uid": authorization_code.uid}).get()
    
    def create_authorization_response(self, redirect_uri: str, grant_user):
        if not grant_user:
            raise AccessDeniedError(state=self.request.state, redirect_uri=redirect_uri)

        self.request.user = grant_user
        code = self.generate_authorization_code()
        element = code;
        element_key = "code";

        self.save_authorization_code(code, self.request)
        # if self.request.response_type=="token":
        #     element_key = "access_token"
        #     token = self.generate_token(self.request.user, self.request.scope, self.GRANT_TYPE, 3600, True);
        #     self.save_token(token);
        #     element = token['access_token']

        params = [(element_key, element)]
        if self.request.state:
            params.append(('state', self.request.state))
        uri = add_params_to_uri(redirect_uri, params)
        headers = [('Location', uri)]
        return 302, '', headers
    

def import_key(filepath, isJson=False):
    try:
        content = read_file(filepath, isJson)
        print('import content done')
        return RSAKey.import_key(content).as_dict(private=True)
    except Exception as e:
        print(f'exception occurated while importing key from file {filepath} ', e)
        return None
def read_private_key():
    pem_url = os.environ.get('OIDC_PEM_URL', None)
    json_url = os.environ.get('OIDC_JSON_URL', None)
    local_pem_file = os.environ.get('LOCAL_OIDC_PEM_URL', None)
    local_json_file = os.environ.get('LOCAL_OIDC_JSON_URL', None)
    print('private key search', {"local_pem": local_pem_file, "pem_url": pem_url, "local_json": local_json_file, "json_url": json_url})
    if local_pem_file is not None:
        try:
            fp = os.getcwd() + "/" + local_pem_file
            print('file for local pem', fp)
            key = import_key(fp, False)
            if key is None:
                print('import returns none')
            if key is not None:
                print('import returns success')
                return key
            else:
                print(f'cannot load private pem key from local file {local_pem_file}')
        except Exception as e:
            print(f'exception occurated while loading private pem key from local file {local_pem_file} ', e)
            pass
    if local_json_file is not None:
        try:
            fp = os.getcwd() + "/" + local_json_file
            print('file for local json', fp)
            key = import_key(fp, True)
            if key is not None:
                return key
            else:
                print(f'cannot load private json key from local file {local_json_file} ')
        except Exception as e:
            print(f'exception occurated while loading private json key from local file {local_json_file} ', e)
            pass

    if pem_url is not None and len(pem_url) > 0 and json_url is None:
        response = requests.get(pem_url)
        print('pem request response status code ', response.status_code)
        if response.status_code == 200:
            val = json.loads(response.content)
            print('val', val)
            print('type val', type(val))
            return val
    if json_url is not None and len(json_url) > 0:
        response = requests.get(json_url)
        print('json request response status code ', response.status_code)
        if response.status_code == 200:
            return json.loads(response.content)
    return None



def get_jwt_config(exp=3600):
    print('trying to reda private key')
    private_key = read_private_key()
    if private_key is None:
        print('private key is None')
    return {
        'key': private_key,
        'alg': os.environ.get("OIDC_JWT_ALG", 'RS256'),
        'iss': os.getenv('JWT_ISSUER'),
        # 'iat': int(time.time()),
        'exp': exp,
    }

def exists_nonce(nonce, req):
    query_params = [{"key": GrantFields.nonce, "comp": "==","value": nonce}, {"key": GrantFields.client_id, "comp": "==","value": req.client_id}]
    exists = OAuthGrant().query(query_params=query_params, first=True)
    return bool(exists)


def generate_user_info(user, scope):
    return UserInfo(sub=str(user.id), **pydash.omit(user.to_json(), ['password', 'token', 'auth_code', 'credentials']))



def create_authorization_code(client, grant_user, request):
    code = gen_salt(48)
    nonce = request.data.get('nonce')
    grant = {
        "code":code,
        "client_id": client.client_id,
        "redirect_uri": request.redirect_uri,
        "scope":request.scope,
        "uid": grant_user.id,
        "nonce": nonce,
    }
    auth_code = OAuthGrant.create(**grant)
    return auth_code.data

class OpenIDAuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    # RESPONSE_TYPES = set({"code"})
    TOKEN_ENDPOINT_AUTH_METHODS = [
        'client_secret_basic',
        'client_secret_post',
        'none'
    ]
    def save_authorization_code(self, code, request):
        code_challenge = request.data.get('code_challenge')
        code_challenge_method = request.data.get('code_challenge_method')
        redirect_uri = request.redirect_uri;
        nonce = request.data.get('nonce')
        scope = request.args.get("scope")
        if request.args.get("redirect_uri") is not None:
            redirect_uri = request.args.get("redirect_uri");
        if redirect_uri is None:
            default_redirect_uri =os.environ.get('DEFAULT_REDIRECT_URI')
            redirect_uri = default_redirect_uri
        model = {
            "client_id": request.client.client_id,
            "code": code,
            "redirect_uri": redirect_uri,
            "scopes": scope_to_list(scope),
            "scope": scope,
            "uid": request.user.uid,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
        }
        if nonce is not None:
            model['nonce'] = nonce
        auth_code_request = OAuthGrant.create(**model)
        auth_code = auth_code_request.data
        return auth_code
    
    def create_authorization_code(self, client, grant_user, request):
        return create_authorization_code(client, grant_user, request)
    
    def parse_authorization_code(self, code, client):
        query_params = [{"key": GrantFields.code, "comp": "==","value": code}, {"key": GrantFields.client_id, "comp": "==","value": client.client_id}]
        auth_code = OAuthGrant().query(query_params=query_params, first=True)
        #if auth_code and not auth_code.is_expired():
        return auth_code

    def query_authorization_code(self, code, client):
        query_params = [{"key": GrantFields.code, "comp": "==","value": code}, {"key": GrantFields.client_id, "comp": "==","value": client.client_id}]
        auth_code = OAuthGrant().query(query_params=query_params, first=True)
        #if auth_code and not auth_code.is_expired():
        return auth_code
    
    def delete_authorization_code(self, authorization_code):
        remove = OAuthGrant(authorization_code.to_json()).remove()
        print('removing authorization code', authorization_code.id)

    def authenticate_user(self, authorization_code):
        return User({"uid": authorization_code.uid}).get()
    
    
class OpenIDCode(_OpenIDCode):
    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_jwt_config(self,  grant):
        print('get jwt config for openid code')
        return get_jwt_config(86400)

    def generate_user_info(self, user, scope):
        return generate_user_info(user, scope)


class OpenIDImplicitGrant(_OpenIDImplicitGrant):
    RESPONSE_TYPES = {'id_token token', 'id_token', 'token'}
    DEFAULT_RESPONSE_MODE = 'query'
    
    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_jwt_config(self):
        return get_jwt_config()

    def generate_user_info(self, user, scope):
        return generate_user_info(user, scope)
    
    def authenticate_user(self, authorization_code):
        return User({"uid": authorization_code.uid}).get()


class OpenIDHybridGrant(_OpenIDHybridGrant):
    DEFAULT_RESPONSE_MODE = 'query'
    def create_authorization_code(self, client, grant_user, request):
        return create_authorization_code(client, grant_user, request)
    
    def save_authorization_code(self, code, request):
        code_challenge = request.data.get('code_challenge')
        code_challenge_method = request.data.get('code_challenge_method')
        redirect_uri = request.redirect_uri;
        nonce = request.data.get('nonce')
        scope = request.args.get("scope")
        if request.args.get("redirect_uri") is not None:
            redirect_uri = request.args.get("redirect_uri");
        if redirect_uri is None:
            default_redirect_uri =os.environ.get('DEFAULT_REDIRECT_URI')
            redirect_uri = default_redirect_uri
        model = {
            "client_id": request.client.client_id,
            "code": code,
            "redirect_uri": redirect_uri,
            "scopes": scope_to_list(scope),
            "scope": scope,
            "uid": request.user.uid,
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
        }
        if nonce is not None:
            model['nonce'] = nonce
        auth_code_request = OAuthGrant.create(**model)
        auth_code = auth_code_request.data
        return auth_code

    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_jwt_config(self):
        return get_jwt_config(86400)

    def generate_user_info(self, user, scope):
        return generate_user_info(user, scope)
    
    def create_authorization_response(self, redirect_uri, grant_user):
        return super().create_authorization_response(redirect_uri, grant_user)

    def authenticate_user(self, authorization_code):
        return User({"uid": authorization_code.uid}).get()