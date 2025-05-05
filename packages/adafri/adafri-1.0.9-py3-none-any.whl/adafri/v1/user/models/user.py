from ...base.firebase_collection import FirebaseCollectionBase, getTimestamp
from ....utils import (DictUtils, get_object_model_class, init_class_kwargs, Crypto, get_request_fields, BaseClass)
from ....utils.response import ApiResponse, Error, ResponseStatus, StatusCode
from .user_fields import UserFields, UserFieldProps, PhoneInfosFields, PhoneInfosFieldProps, PHONE_FIELDS, USER_FIELDS, USERS_COLLECTION
from typing import List
from typing import Any
from dataclasses import dataclass
from firebase_admin import auth as admin_auth
from adafri.v1.auth.firebase_auth import create_firebase_user
from firebase_admin.exceptions import FirebaseError
import pydash


def filter_user_request_fields(fields, default_fields = USER_FIELDS):
    request_fields = get_request_fields(fields, default_fields, [default_fields[0]])
    if request_fields is None or bool(request_fields) is False:
        request_fields = [default_fields[0]]
    return request_fields
@dataclass
class Account:
    canManageClients: bool
    childs: List[object]
    currenyCode: str
    customerId: int
    dateTimeZone: str
    name: str
    testAccount: bool

    @staticmethod
    def from_dict(obj: Any) -> 'Account':
        _canManageClients = DictUtils.pick(obj, "canManageClients", bool)
        _childs = [y for y in DictUtils.pick(obj, "childs", list)]
        _currenyCode = str(DictUtils.pick(obj, "currenyCode", str))
        _customerId = int(DictUtils.pick(obj, "customerId", int))
        _dateTimeZone = str(DictUtils.pick(obj, "dateTimeZone",str))
        _name = str(DictUtils.pick(obj, "name", str))
        _testAccount = bool(DictUtils.pick(obj, "testAccount", bool))
        return Account(_canManageClients, _childs, _currenyCode, _customerId, _dateTimeZone, _name, _testAccount)

@dataclass
class Country:
    areaCodes: List[object]
    dialCode: str
    flagClass: str
    htmlId: str
    iso2: str
    name: str
    placeHolder: str
    priority: int

    @staticmethod
    def from_dict(obj: Any) -> 'Country':
        _areaCodes = [y for y in DictUtils.pick(obj, "areaCodes", list)]
        _dialCode = str(DictUtils.pick(obj, "dialCode", str))
        _flagClass = str(DictUtils.pick(obj, "flagClass",str))
        _htmlId = str(DictUtils.pick(obj, "htmlId", str))
        _iso2 = str(DictUtils.pick(obj, "iso2", str))
        _name = str(DictUtils.pick(obj, "name", str))
        _placeHolder = str(DictUtils.pick(obj, "placeHolder", str))
        _priority = int(DictUtils.pick(obj, "priority", int))
        return Country(_areaCodes, _dialCode, _flagClass, _htmlId, _iso2, _name, _placeHolder, _priority)

@dataclass
class Credential:
    refresh_token: str
    scopes: List[str]
    token: str
    token_uri: str

    @staticmethod
    def from_dict(obj: Any) -> 'Credential':
        _refresh_token = str(DictUtils.pick(obj, "refresh_token", str))
        _scopes = [y for y in DictUtils.pick(obj, "scopes", list)]
        _token = str(DictUtils.pick(obj, "token", str))
        _token_uri = str(DictUtils.pick(obj, "token_uri", str))
        return Credential(_refresh_token, _scopes, _token, _token_uri)

@dataclass
class DeviceInfo:
    browser: str
    browser_version: str
    device: str
    os: str
    os_version: str
    userAgent: str

    @staticmethod
    def from_dict(obj: Any) -> 'DeviceInfo':
        _browser = str(DictUtils.pick(obj, "browser", str))
        _browser_version = str(DictUtils.pick(obj, "browser_version", str))
        _device = str(DictUtils.pick(obj, "device", str))
        _os = str(DictUtils.pick(obj, "os", str))
        _os_version = str(DictUtils.pick(obj, "os_version", str))
        _userAgent = str(DictUtils.pick(obj, "userAgent", str))
        return DeviceInfo(_browser, _browser_version, _device, _os, _os_version, _userAgent)

@dataclass
class PartenerData:
    id: str
    text: str

    @staticmethod
    def from_dict(obj: Any) -> 'PartenerData':
        _id = str(DictUtils.pick(obj, "id", str))
        _text = str(DictUtils.pick(obj, "text", str))
        return PartenerData(_id, _text)

@dataclass(init=False)
class PhoneInfo(BaseClass):
    countryCode: str
    dialCode: str
    e164Number: str
    internationalNumber: str
    nationalNumber: str
    number: str
    __baseFields: PhoneInfosFieldProps

    def __init__(self, phoneInfo=None, **kwargs):
        (cls_object, keys, data_args) = init_class_kwargs(self, phoneInfo, PHONE_FIELDS, PhoneInfosFieldProps, None, [], **kwargs)
        super().__init__(**data_args);
        for key in keys:
            setattr(self, key, cls_object[key]) 


    @staticmethod
    def from_dict(obj: Any) -> 'PhoneInfo':
        cls_object, keys = get_object_model_class(obj, PhoneInfo, PhoneInfosFieldProps);
        _phone = PhoneInfo(cls_object)
        return _phone
    
    def to_dict(self, field=None):
        # print('to dict', self)
        return DictUtils.remove_none_values({
            "countryCode": self.countryCode,
            "dialCode": self.dialCode,
            "e164Number": self.e164Number,
            "internationalNumber": self.internationalNumber,
            "nationalNumber": self.nationalNumber,
            "number": self.number
        })

@dataclass
class PlateformRole:
    id: str
    partenerData: PartenerData
    text: str

    @staticmethod
    def from_dict(obj: Any) -> 'PlateformRole':
        _id = str(DictUtils.pick(obj, "id", str))
        _partenerData = PartenerData.from_dict(DictUtils.pick(obj, "partenerData", dict))
        _text = str(DictUtils.pick(obj, "text", str))
        return PlateformRole(_id, _partenerData, _text)


@dataclass(init=False)
class User(FirebaseCollectionBase):
    account_value: int = None;
    addresse: str
    auth_code: str
    authorizedPush: bool
    country: Country
    deviceInfo: DeviceInfo
    displayName: str
    email: str
    entrepriseName: str
    entrepriseUrl: str
    first_name: str
    hasApprouvedPolicy: bool
    isConnectWithMailAndPassword: bool
    isCorporate: bool
    isDesktopDevice: bool
    isMobile: bool
    isParticular: bool
    isTablet: bool
    last_name: str
    phoneInfo: PhoneInfo
    photoURL: str
    plateformRole: PlateformRole
    postal: str
    profileCompleted: bool
    showPushToken: bool
    telephone: str
    token: List[str]
    uid: str
    user_type: str
    password: str
    provider: str
    status: str
    _emailValidationSendDate: str
    _pwResetSendDate: str
    businessType: str
    phoneVerified: bool
    emailVerified: bool
    postalCode: str
    __baseFields: UserFieldProps

    def __init__(self, user=None, **kwargs):
        value = user;
        if type(user) is str:
            value = {"uid": user, "id": user}
        (cls_object, keys, data_args) = init_class_kwargs(self, value, USER_FIELDS, UserFieldProps, USERS_COLLECTION, ['id','uid'], **kwargs)

        super().__init__(**data_args);
        for key in keys:
            if key in cls_object:
                if key == "phoneInfo":
                    if bool(cls_object[key]) is False:
                        setattr(self, key, None)
                    else:
                        # print('is phone info', cls_object[key])
                        setattr(self, key, PhoneInfo.from_dict(cls_object[key]))
                else:
                    # print('set attr for', key)
                    setattr(self, key, cls_object[key]);
            else:
                setattr(self, key, None)
                
    


    @staticmethod
    def generate_model(_key_="default_value"):
        user = {};
        props = UserFieldProps
        for k in DictUtils.get_keys(props):
            user[k] = props[k][_key_];
        return user;

    @staticmethod
    def from_dict(user: Any=None, db=None, collection_name=USERS_COLLECTION) -> 'User':
        cls_object, keys = get_object_model_class(user, User, UserFieldProps);
        # print('from dict ===>', cls_object)
        if "firstName" in cls_object:
            cls_object["first_name"] = cls_object["firstName"]
        if "lastName" in cls_object:
            cls_object["last_name"] = cls_object["lastName"]
            
        _user = User(cls_object, db=db, collection_name=collection_name)
        return _user
    
    def to_dict(self, fields=None):
        # base = super().to_dict(fields)
        # print('base', base['ages']);
        if(getattr(self, 'telephone', None) is None):
            return {}
        telephone = getattr(self, 'telephone', None);
        postal = getattr(self, 'postalCode', None);
        provider = getattr(self, 'provider', None);
        phoneInfo = None;
        firstName = None;
        lastName = None;
        if getattr(self, 'phoneInfo', None) is not None:
            phoneInfo = self.phoneInfo.to_dict();
        if bool(provider) is False:
            provider = "https://adafri.com"
        if phoneInfo is not None and (bool(telephone) is False or telephone!=phoneInfo['number'].strip().replace(' ', '')):
            # print('f self', self)
            # print('f', str(self.phoneInfo))
            telephone = str(phoneInfo['number']).strip().replace(' ', '');
        if bool(postal) is False and bool(self.postal) is True:
            postal = self.postal
        
        if getattr(self, 'firstName', None) is not None:
            firstName = self.firstName
        if getattr(self, 'lastName', None) is not None:
            lastName = self.lastName
        values = {
            "uid": self.uid,
            "email": self.email,
            "password": self.password,
            "displayName": self.displayName,
            "firstName": firstName,
            "lastName": lastName,
            "provider": provider,
            "entrepriseName": self.entrepriseName,
            "entrepriseUrl": self.entrepriseUrl,
            "isConnectWithMailAndPassword": self.isConnectWithMailAndPassword,
            "addresse": self.addresse,
            "photoURL": self.photoURL,
            "profileCompleted": self.profileCompleted,
            "telephone": telephone,
            "postalCode": postal,
            "user_type": self.user_type,
            "authorizedPush": self.authorizedPush,
            "hasApprouvedPolicy": self.hasApprouvedPolicy,
            "emailValidationSendDate": self._emailValidationSendDate,
            "status": self.status,
            "businessType": self.businessType,
            "phoneVerified": self.phoneVerified,
            "emailVerified": self.emailVerified,
            "showPushToken": self.showPushToken,
            "status": self.status,
            "phoneInfo": phoneInfo
        };
        return DictUtils.remove_none_values(values)
    def to_json(self, _fields=None):
        return self.to_dict(_fields)
    
    def get(self):
        doc = self.document_reference().get();
        if doc.exists is False:
            return None;
        # print('user found', doc.to_dict())
        d = pydash.pick(doc.to_dict(), USER_FIELDS)
        new_user = User.from_dict(user=d, db=self.db, collection_name=self.collection_name)
        return new_user;

    def query(self, query_params: list, first=False, limit=None):
        result = [];
        query_result = self.custom_query(query_params, first=first, limit=limit, collection_name=self.collection_name)
        # print('query result', query_result)
        if bool(query_result):
            if first:
                return User.from_dict(user=query_result, db=self.db, collection_name=self.collection_name)
            else:
                for doc in query_result:
                    result.append(User.from_dict(user=doc, db=self.db, collection_name=self.collection_name))
                return result
        if first:
                return None
        return [];
    def get_user_id(self):
        return self.uid
    def create(self, **kwargs):
        data_dict = DictUtils.pick_fields(kwargs, UserFields(fields_props=UserFieldProps).filtered_keys('mutable', True));
        user_model = User().from_dict(DictUtils.merge_dict(data_dict, User.generate_model()));
        if bool(user_model.to_json()) is False:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("Empty request","INVALID_REQUEST", 1))
        
        email = user_model.email
        password = user_model.password
        
        if bool(email) is False:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("Email required","INVALID_REQUEST", 1));
    
        if bool(password) is False:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error("Password required","INVALID_REQUEST", 1));
        docs = User().collection().where('email', '==', email).get();
        found_users = [];
        if len(docs) > 0:
            for doc in docs:
                found_users.append(User.from_dict(doc.to_dict()).to_json());
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"User wiith emaill {user_model.email} already exist","INVALID_REQUEST", 1));
    
    
        try:
            user_model.isConnectWithMailAndPassword = bool(user_model.uid) is False
            if bool(user_model.uid) is False:
                user_record = create_firebase_user(email, password);
                user_model.uid = user_record.uid;
                hashed_password = Crypto().encrypt(password);
                user_model.password = hashed_password;
            User().collection().document(user_model.uid).set({**user_model.to_json(), "createdAt": getTimestamp()}, merge=True)
            return ApiResponse(ResponseStatus.OK, StatusCode.status_200, user_model.to_json(), None);
        except Exception as e:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(str(e),"INVALID_REQUEST", 1));
    
    def update(self, data):
        try:
            last_value = self.to_dict();
            filtered_value = pydash.pick(data, UserFields(fields_props=UserFieldProps).filtered_keys('editable', True));
            new_value = DictUtils.merge_dict(filtered_value, self.to_dict());
            changed_fields = DictUtils.get_changed_field(last_value, new_value);
            # print('last', last_value)
            # print('new', new_value)
            # print('changed', changed_fields)
            # print('data', data)
            data_update = DictUtils.dict_from_keys(filtered_value, changed_fields);
            if bool(data_update) is False:
                return None;
            self.document_reference().set(data_update, merge=True)
            return DictUtils.dict_from_keys(self.get().to_dict(), changed_fields);
        except Exception as e:
            print(e)
            return None;

    def remove(self, only_mark_as_removed=True):
        try:
            if self.id is None:
                return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"Cannot identify User with id {self.id}","INVALID_REQUEST", 1));
            if only_mark_as_removed:
                self.document_reference().set({"is_removed": True})
            else:
                self.document_reference().delete();
            return ApiResponse(ResponseStatus.OK, StatusCode.status_200, {"message": f"User {self.id} deleted"}, None);
        except:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(f"An error occurated while removing authorization code with id {self.id}","INVALID_REQUEST", 1));

    
    def get_firebase_user(self, key: str, value: str) -> 'admin_auth.UserRecord':
        try:
            if key == 'email':
                return admin_auth.get_user_by_email(value)
            elif key == 'uid':
                return admin_auth.get_user(value)
            elif key == 'phone':
                return admin_auth.get_user_by_phone_number(value)
        except ValueError as e:
            raise e
        except FirebaseError as e:
            raise e;    
        except admin_auth.UserNotFoundError as e:
            raise e;  


