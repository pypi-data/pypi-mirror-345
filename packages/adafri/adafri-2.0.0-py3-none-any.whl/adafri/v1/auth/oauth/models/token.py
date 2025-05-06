from .....utils import DictUtils, Crypto, get_object_model_class, pydash, init_class_kwargs
from ....base.firebase_collection import (FirebaseCollectionBase, getTimestamp)
from .token_fields import TokenFields, TokenFieldsProps, STANDARD_FIELDS, TOKEN_COLLECTION, get_token_expire_at, is_expired
from .....utils.response import ApiResponse, Error, ResponseStatus, StatusCode
from .....utils.utils import read_file
from typing import Any
from dataclasses import dataclass
from ....user import User
from authlib.oauth2.rfc7009 import RevocationEndpoint
from authlib.oauth2.rfc6750 import BearerTokenValidator
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc6749 import TokenMixin, scope_to_list
from authlib.oauth2.rfc6750 import BearerTokenGenerator, BearerToken
from authlib.oauth2.rfc9068 import JWTBearerTokenGenerator, JWTBearerTokenValidator
import json
from flask import abort, Response
from joserfc.jwk import KeySet

@dataclass(init=False)
class OAuthToken(TokenMixin, FirebaseCollectionBase):
    id: str
    client_id: str
    uid: str
    token_type: str
    access_token: str
    refresh_token: str
    scopes: list[str]
    scope: str
    expired_at: str
    expires_in: int
    revoked: bool
    type: str
    __baseFields: TokenFieldsProps

    def __init__(self, token=None, **kwargs):
        if type(token) is str:
            token = {"access_token": token} 
        (cls_object, keys, data_args) = init_class_kwargs(self, token, STANDARD_FIELDS, TokenFieldsProps, TOKEN_COLLECTION, ['id'], **kwargs)
        super().__init__(**data_args);
        for key in keys:
            setattr(self, key, cls_object[key]) 


    @staticmethod
    def generate_model(_key_="default_value"):
        grant = {};
        props = TokenFieldsProps
        for k in DictUtils.get_keys(props):
            grant[k] = props[k][_key_];
        return grant;

    @staticmethod
    def from_dict(token: Any=None, db=None, collection_name=None) -> 'OAuthToken':
        cls_object, keys = get_object_model_class(token, OAuthToken, TokenFieldsProps);
        _client = OAuthToken(cls_object, db=db, collection_name=collection_name)
        return _client

    def query(self, query_params: list, first=False, limit=None):
        result = [];
        query_result = self.custom_query(query_params, first=first, limit=limit)
        if bool(query_result):
            if first is True:
                return OAuthToken.from_dict(token=query_result, db=self.db, collection_name=self.collection_name)
            else:
                for doc in query_result:
                    result.append(OAuthToken.from_dict(token=doc, db=self.db, collection_name=self.collection_name))
                return result
        if first:
                return None
        return [];

    def getOAuthToken(self) -> 'OAuthToken':
        if bool(self.id):
            doc = self.document_reference().get();
            if doc.exists is False:
                return None;
            return OAuthToken.from_dict(doc.to_dict(), db=self.db, collection_name=self.collection_name);
        if bool(self.access_token):
            return self.query([{"key": TokenFields.access_token, "comp": "==", "value": self.access_token}], True)

    @staticmethod
    def generate(**kwargs) -> 'ApiResponse':
        data_dict = DictUtils.pick_fields(kwargs, TokenFields.filtered_keys('pickable', True));
        token_model = OAuthToken.from_dict(DictUtils.merge_dict(data_dict, OAuthToken.generate_model()));
        
        if bool(token_model.to_json()) is False:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("Empty request","INVALID_REQUEST", 1)).to_json()
        
        if bool(token_model.access_token) is False:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("name required","INVALID_REQUEST", 1));

        token_model.id = Crypto().generate_id(token_model.uid+"~"+token_model.client_id+"~"+token_model.type);
        return ApiResponse(ResponseStatus.OK, StatusCode.status_200, token_model, None);
    

    def save(self, token, request):
        model = {**token, "client_id": request.client.client_id, "uid": request.user.uid, "revoked": False}
        if 'type' not in model:
            model['type'] = 'app_token'
        print('saving token', model)
        token_generate = OAuthToken.generate(**model);
        if token_generate.status == ResponseStatus.ERROR:
            return token_generate
        token_model: OAuthToken = token_generate.data;
        docRef = OAuthToken(token_model.to_json()).document_reference();
        # if docRef.get().exists:
        #     return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"Location with name {token_generate.data.id} already exist","INVALID_REQUEST", 1));
        
        docRef.set({**token_model.to_json(), "createdAt": getTimestamp()}, merge=True);
        created_token = token_model.getOAuthToken()
        return ApiResponse(ResponseStatus.OK, StatusCode.status_200, created_token.to_json(), None);
    
    def update(self, data):
        try:
            last_value = self.to_json();
            filtered_value = pydash.pick(data, TokenFields.filtered_keys('editable', True));
            new_value = DictUtils.merge_dict(filtered_value, self.to_json());
            changed_fields = DictUtils.get_changed_field(last_value, new_value);
            data_update = DictUtils.dict_from_keys(filtered_value, changed_fields);
            if bool(data_update) is False:
                return None;
            self.document_reference().set(data_update, merge=True)
            return DictUtils.dict_from_keys(self.getOAuthToken().to_json(), changed_fields);
        except Exception as e:
            print(e)
            return None;
    
    def remove(self):
        try:
            if self.id is None:
                return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"Cannot identify token with id {self.id} to delete","INVALID_REQUEST", 1));
            deleted = self.document_reference().delete();
            return ApiResponse(ResponseStatus.OK, StatusCode.status_200, {"message": f"Token {self.id} deleted"}, None);
        except:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"An error occurated while removing authorization code with id {self.id}","INVALID_REQUEST", 1));


    def is_expired(self):
        return is_expired(self.expired_at)
    
    def is_revoked(self):
        return self.revoked
    

class TokenValidator(BearerTokenValidator):
    def authenticate_token(self, token_string):
        token_request = OAuthToken().query([{"key":"access_token", "comp": "==", "value": token_string}], True)
        return token_request
    
    def validate_token(self, token, scopes, request):
        token_scopes = scope_to_list(token.scope);
        insufficient = self.scope_insufficient(token_scopes, scopes);
        if insufficient:
            response = ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("Insufficient privilegies","INVALID_REQUEST", 1)).to_json()
            return abort(Response(response=json.dumps(response), status=401, mimetype='application/json'))        
        return None

class TokenRevocationEndpoint(RevocationEndpoint):
    def query_token(self, token, token_type_hint, client):
        q: list = OAuthToken().query([{"key":"client_id", "comp": "==", "value": client.clent_id}], False)
        if token_type_hint == 'access_token':
            return pydash.find(q, lambda x: x.access_token==token);
        elif token_type_hint == 'refresh_token':
            return pydash.find(q, lambda x: x.refresh_token==token);
        # without token_type_hint
        item = pydash.find(q, lambda x: x.access_token==token);
        if item:
            return item
        return pydash.find(q, lambda x: x.refresh_token==token);

    def revoke_token(self, _token):
        token = OAuthToken.from_dict(_token);
        token.revoked = True
        token.update(_token);

class RefreshTokenGrant(grants.RefreshTokenGrant):
    def authenticate_refresh_token(self, refresh_token):
        token = OAuthToken().query([{"key":"refresh_token", "comp": "==", "value": refresh_token}], True);
        return token;
        # if token and token.is_refresh_token_active():
        #     return token

    def authenticate_user(self, credential):
        return User({"uid": credential.user_id}).get()

    # def revoke_old_credential(self, credential):
    #     credential.revoked = True
    #     db.session.add(credential)
    #     db.session.commit()


DEFAULT_EXPIRES_IN = 3600
class TokenGenerator(BearerTokenGenerator):
    @staticmethod
    def generate(grant_type, client, user=None, scope=None, expires_in=None, include_refresh_token=True):
        if expires_in is None:
            expires_in = DEFAULT_EXPIRES_IN
        uid = client.uid;
        if user is not None:
            uid = user.uid
        expires_at = get_token_expire_at(expires_in).isoformat()
        token = {'token_type': 'Bearer', "client_id": client.client_id, "uid": uid, 'scope': scope, 'scopes': scope_to_list(scope), 'expires_in': expires_in, "grant_type": grant_type, 'expired_at': expires_at}
        access_token = Crypto().generate_token("access_token~"+json.dumps(token));
        token['access_token'] = access_token;
        if include_refresh_token:
            token['refresh_token'] = Crypto().generate_token("refresh_token~"+json.dumps(token));
        if grant_type == 'implicit':
            return {"access_token": access_token, "scope": scope, "expires_in": expires_in}
        print('token generated', access_token)
        return token
import os
import json
from authlib.jose import jwt
import time
from datetime import datetime, timedelta
from joserfc.jwk import RSAKey
import requests


def read_private_key():
    pem_url = os.environ.get('OIDC_PEM_URL', None)
    json_url = os.environ.get('OIDC_JSON_URL', None)
    local_pem_file = os.environ.get('LOCAL_OIDC_PEM_URL', None)
    local_json_file = os.environ.get('LOCAL_OIDC_JSON_URL', None)
    # print('private key search', {"local_pem": local_pem_file, "pem_url": pem_url, "local_json": local_json_file, "json_url": json_url})
    if local_pem_file is not None:
        try:
            fp = os.getcwd() + "/" + local_pem_file
            # print('file for local pem', fp)
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
            # print('file for local json', fp)
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
        # print('pem request response status code ', response.status_code)
        if response.status_code == 200:
            val = json.loads(response.content)
            # print('val', val)
            # print('type val', type(val))
            return val
    if json_url is not None and len(json_url) > 0:
        response = requests.get(json_url)
        # print('json request response status code ', response.status_code)
        if response.status_code == 200:
            return json.loads(response.content)
    return None

def read_jwks():
    """
    Reads JWKS from either a local file or a URL.

    First it looks for a local file specified in the environment variable
    LOCAL_OIDC_JWKS_URL. If not found, it looks for a URL specified in the
    environment variable OIDC_JWKS_URL. If neither is found, it returns None.

    If a local file is found, it reads and parses the content as JSON.
    If a URL is found, it sends a GET request to the URL and parses the
    response content as JSON.

    If an exception occurs while reading the file or sending the request,
    it prints an error message and returns None.

    :return: JWKS as a JSON object
    :rtype: dict or None
    """
    url = os.environ.get('OIDC_JWKS_URL', None)
    local_jwks_file = os.environ.get('LOCAL_OIDC_JWKS_URL', None)
    if local_jwks_file is not None:
        try:
            fp = os.getcwd() + "/" + local_jwks_file
            content = open(fp, 'r').read()
            return json.loads(content)
        except Exception as e:
            print(f'exception occurated while loading jwk from local file {local_jwks_file} ', e)
            return None
    if url is not None and len(url) > 0:
        response = requests.get(url)
        # print('jwks fetch response code', response.status_code)
        if response.status_code == 200:
            return response.json()


class JwtTokenGenerator(JWTBearerTokenGenerator):
    GRANT_TYPES_EXPIRES_IN = {
        "authorization_code": 864000,
        "implicit": 3600,
        "password": 864000,
        "client_credentials": 864000,
    }
    def get_jwks(self):
        print('reading jwks for generator [JwtTokenGenerator]')
        return read_private_key()


    # def access_token_generator(self, client, grant_type, user, scope):
    #     # now = datetime.now()
    #     # exp = now + timedelta(seconds=3600)
    #     # expires_in = now + self._get_expires_in(client, grant_type)
    #     now = int(time.time())
    #     exp = self._get_expires_in(client, grant_type)
    #     expires_in = now + self._get_expires_in(client, grant_type)
    #     print('now', now)
    #     print('exp', exp)
    #     print('expires_in', expires_in)

    #     token_data = {
    #         'iss': self.issuer,
    #         'exp': expires_in,
    #         'client_id': client.get_client_id(),
    #         'iat': now,
    #         'jti': self.get_jti(client, grant_type, user, scope),
    #         'scope': scope,
    #     }

    #     # In cases of access tokens obtained through grants where a resource owner is
    #     # involved, such as the authorization code grant, the value of 'sub' SHOULD
    #     # correspond to the subject identifier of the resource owner.

    #     if user:
    #         token_data['sub'] = user.get_user_id()

    #     # In cases of access tokens obtained through grants where no resource owner is
    #     # involved, such as the client credentials grant, the value of 'sub' SHOULD
    #     # correspond to an identifier the authorization server uses to indicate the
    #     # client application.

    #     else:
    #         token_data['sub'] = client.get_client_id()

    #     # If the request includes a 'resource' parameter (as defined in [RFC8707]), the
    #     # resulting JWT access token 'aud' claim SHOULD have the same value as the
    #     # 'resource' parameter in the request.

    #     # TODO: Implement this with RFC8707
    #     if False:  # pragma: no cover
    #         ...

    #     # If the request does not include a 'resource' parameter, the authorization
    #     # server MUST use a default resource indicator in the 'aud' claim. If a 'scope'
    #     # parameter is present in the request, the authorization server SHOULD use it to
    #     # infer the value of the default resource indicator to be used in the 'aud'
    #     # claim. The mechanism through which scopes are associated with default resource
    #     # indicator values is outside the scope of this specification.

    #     else:
    #         token_data['aud'] = self.get_audiences(client, user, scope)

    #     # If the values in the 'scope' parameter refer to different default resource
    #     # indicator values, the authorization server SHOULD reject the request with
    #     # 'invalid_scope' as described in Section 4.1.2.1 of [RFC6749].
    #     # TODO: Implement this with RFC8707

    #     if auth_time := self.get_auth_time(user):
    #         token_data['auth_time'] = auth_time

    #     # The meaning and processing of acr Claim Values is out of scope for this
    #     # specification.

    #     if acr := self.get_acr(user):
    #         token_data['acr'] = acr

    #     # The definition of particular values to be used in the amr Claim is beyond the
    #     # scope of this specification.

    #     if amr := self.get_amr(user):
    #         token_data['amr'] = amr

    #     # Authorization servers MAY return arbitrary attributes not defined in any
    #     # existing specification, as long as the corresponding claim names are collision
    #     # resistant or the access tokens are meant to be used only within a private
    #     # subsystem. Please refer to Sections 4.2 and 4.3 of [RFC7519] for details.

    #     token_data.update(self.get_extra_claims(client, grant_type, user, scope))

    #     # This specification registers the 'application/at+jwt' media type, which can
    #     # be used to indicate that the content is a JWT access token. JWT access tokens
    #     # MUST include this media type in the 'typ' header parameter to explicitly
    #     # declare that the JWT represents an access token complying with this profile.
    #     # Per the definition of 'typ' in Section 4.1.9 of [RFC7515], it is RECOMMENDED
    #     # that the 'application/' prefix be omitted. Therefore, the 'typ' value used
    #     # SHOULD be 'at+jwt'.

    #     header = {'alg': self.alg, 'typ': 'at+jwt'}
    #     jwks = self.get_jwks()
    #     access_token = jwt.encode(
    #         header,
    #         token_data,
    #         key=jwks,
    #         check=False,
    #     )
    #     return access_token.decode()
    # def generate_token(self, client, grant_type, user=None, scope=None):
    #     """Generate a JWT as a bearer token."""
    #     now = int(time.time())
    #     header = {"alg": self.algorithm}
    #     print('generate token grant type', grant_type)
        
    #     # Define payload for the JWT
    #     payload = {
    #         'iss': self.issuer,
    #         'aud': self.audience,
    #         'iat': now,
    #         'exp': now + 3600,  # Token expiration (1 hour)
    #         'client_id': client.client_id,
    #         'scope': scope,
    #     }
        
    #     if user:
    #         payload['uid'] = user.uid
        
    #     # Create the JWT
    #     json_url = os.environ.get('OIDC_JSON_URL', None)
    #     response = requests.get(json_url)
    #     # rsa = RSAKey.import_key(open(os.getcwd()+"/"+os.getenv('OAUTH_PRIVATE_KEY'), 'r').read())
    #     rsa = RSAKey.import_key(response.json(), **{"use": "sig"})
    #     private_jwk = rsa.as_dict(is_private=True)
    #     token = jwt.encode(header, payload, private_jwk)
    #     return token.decode('utf-8')  # Return token as string
    # # @staticmethod
    # def generate(self, grant_type, client, user=None, scope=None,
    #         expires_in=None, include_refresh_token=True):
    #     """Generate a bearer token for OAuth 2.0 authorization token endpoint.

    #     :param client: the client that making the request.
    #     :param grant_type: current requested grant_type.
    #     :param user: current authorized user.
    #     :param expires_in: if provided, use this value as expires_in.
    #     :param scope: current requested scope.
    #     :param include_refresh_token: should refresh_token be included.
    #     :return: Token dict
    #     """
    #     print('generating new token')
    #     scope = self.get_allowed_scope(client, scope)
    #     access_token = self.access_token_generator(
    #         client=client, grant_type=grant_type, user=user, scope=scope)
    #     if expires_in is None:
    #         expires_in = self._get_expires_in(client, grant_type)

    #     token = {
    #         'token_type': 'Bearer',
    #         'access_token': access_token,
    #     }
    #     if expires_in:
    #         token['expires_in'] = expires_in
    #     if include_refresh_token and self.refresh_token_generator:
    #         token['refresh_token'] = self.refresh_token_generator(
    #             client=client, grant_type=grant_type, user=user, scope=scope)
    #     if scope:
    #         token['scope'] = scope
    #     return token

class JwtTokenValidator(JWTBearerTokenValidator):
    def get_jwks(self):
        # print('reding jwks for validator [JwtTokenValidator]')
        return read_private_key()
        # jwks = read_jwks()
        # for k in jwks['keys']:
        #     if k['kty'] == 'RSA':
        #         print('find rsa for validator', k)
        #         return RSAKey.import_key(k).as_dict(private=False)
        # return None

    def authenticate_token(self, token_string):
        token_request = OAuthToken().query([{"key":"access_token", "comp": "==", "value": token_string}], True)
        return token_request
    
    def validate_token(self, token, scopes, request):
        if token is None:
            response = ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("Insufficient privilegies","ACCESS_DENIED", 1)).to_json()
            return abort(Response(response=json.dumps(response), status=401, mimetype='application/json')) 
        token_scopes = scope_to_list(token.scope);
        insufficient = self.scope_insufficient(token_scopes, scopes);
        if insufficient:
            response = ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("Insufficient privilegies","ACCESS_DENIED", 1)).to_json()
            return abort(Response(response=json.dumps(response), status=401, mimetype='application/json'))        
        return None
# Define your JWT bearer token generator
# class JWTBearerTokenGenerator(BearerToken):
#     def __init__(self, private_key, algorithm='RS256', issuer=None, audience=None):
#         self.private_key = private_key
#         self.algorithm = algorithm
#         self.issuer = issuer
#         self.audience = audience

#     def generate(self, grant_type, client, user=None, scope=None, expires_in=None, include_refresh_token=True):
#         v = self.generate()
#     def generate_token(self, client, grant_type, user=None, scope=None):
#         """Generate a JWT as a bearer token."""
#         now = int(time.time())
#         header = {"alg": self.algorithm}
        
#         # Define payload for the JWT
#         payload = {
#             'iss': self.issuer,
#             'aud': self.audience,
#             'iat': now,
#             'exp': now + 3600,  # Token expiration (1 hour)
#             'client_id': client.client_id,
#             'scope': scope,
#         }
        
#         if user:
#             payload['uid'] = user.uid
        
#         # Create the JWT
#         token = jwt.encode(header, payload, self.private_key)
#         return token.decode('utf-8')  # Return token as string

#     def get_token(self, client, grant_type, user=None, scope=None):
#         """Generate a token and set token type as Bearer."""
#         access_token = self.generate_token(client, grant_type, user, scope)
#         return {
#             'access_token': access_token,
#             'token_type': 'Bearer',
#             'expires_in': 3600,  # Token validity duration
#             'scope': scope
#         }