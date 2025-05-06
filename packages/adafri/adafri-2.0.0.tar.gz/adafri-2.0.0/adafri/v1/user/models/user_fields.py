from dataclasses import dataclass
from  ....utils.utils import DictUtils, BaseFieldsClass 
import os

USERS_COLLECTION = os.environ.get('USER_COLLECTION');
@dataclass
class PhoneInfosFields(BaseFieldsClass):
    countryCode = "countryCode";
    dialCode = "dialCode";
    e164Number = "e164Number";
    internationalNumber = "internationalNumber";
    nationalNumber = "nationalNumber";
    number = "number";
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.class_fields_props = PhoneInfosFieldProps

PhoneInfosFieldProps = {
    PhoneInfosFields.countryCode: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    PhoneInfosFields.dialCode: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    PhoneInfosFields.e164Number: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    PhoneInfosFields.nationalNumber: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    PhoneInfosFields.internationalNumber: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    PhoneInfosFields.number: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
}

@dataclass
class UserFields(BaseFieldsClass):
    uid = "uid";
    email = 'email';
    password = 'password';
    displayName = 'displayName';
    firstName = 'firstName';
    lastName = 'lastName';
    first_name = 'first_name';
    last_name = 'last_name';
    provider = 'provider';
    entrepriseName = 'entrepriseName';
    entrepriseUrl = 'entrepriseUrl';
    isConnectWithMailAndPassword = 'isConnectWithMailAndPassword';
    address = 'addresse';
    photoURL = 'photoURL';
    profileCompleted = 'profileCompleted';
    telephone = 'telephone';
    postalCode = 'postalCode';
    token = 'token';
    deviceInfo = 'deviceInfo';
    phoneInfo = 'phoneInfo';
    country = 'country';
    showPushToken = 'showPushToken'
    authorizedPush = 'authorizedPush';
    hasApprouvedPolicy = 'hasApprouvedPolicy';
    _emailValidationSendDate = 'emailValidationSendDate'
    status = 'status'
    businessType = 'businessType'
    user_type = 'user_type'
    phoneVerified = 'phoneVerified'
    emailVerified = 'emailVerified'
    postal = 'postal'
    _pwResetSendDate = '_pwResetSendDate'
    auth_code = 'auth_code'
    plateformRole = "plateformRole"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.class_fields_props = UserFieldProps



UserFieldProps = {
    UserFields.uid: {
        "type": str,
        "required": True,
        "mutable": False,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    UserFields.email: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": False,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    UserFields.address: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": None,
        "pickable": True,
    },
    UserFields.password: {
        "type": str,
        "required": True,
        "mutable": True,
        "editable": True,
        "interactive": False,
        "default_value": "",
        "pickable": True,
    },
    UserFields.firstName: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    UserFields.lastName: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    UserFields.first_name: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    UserFields.last_name: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    UserFields.displayName: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    UserFields.postalCode: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    UserFields.telephone: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    UserFields.authorizedPush: {
        "type": bool,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": False,
        "pickable": True,
    },
    UserFields.hasApprouvedPolicy: {
        "type": bool,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": False,
        "pickable": True,
    },
    UserFields.profileCompleted: {
        "type": bool,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": False,
        "pickable": True,
    },
    UserFields.entrepriseUrl: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    UserFields.entrepriseName: {
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    UserFields.photoURL:{
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": True,
        "default_value": "",
        "pickable": True,
    },
    UserFields.provider:{
        "type": str,
        "required": False,
        "mutable": True,
        "editable": False,
        "interactive": False,
        "default_value": "https://adafri.app",
        "pickable": True,
    },
    UserFields.isConnectWithMailAndPassword:{
        "type": bool,
        "required": False,
        "mutable": False,
        "editable": False,
        "interactive": False,
        "default_value": False,
        "pickable": True,
    },
    UserFields.token:{
        "type": list[str],
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": False,
        "default_value": [],
        "pickable": True,
    },
    UserFields.phoneInfo:{
        "type": dict,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": False,
        "default_value": None,
        "pickable": True,
    },
    UserFields.deviceInfo:{
        "type": dict,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": False,
        "default_value": None,
        "pickable": True,
    },
    UserFields.status:{
    "type": str,
    "required": False,
    "mutable": True,
    "editable": True,
    "interactive": False,
    "default_value": "",
    "pickable": True,
    },
    UserFields._emailValidationSendDate:{
    "type": str,
    "required": False,
    "mutable": True,
    "editable": True,
    "interactive": False,
    "default_value": "",
    "pickable": True,
    },
    UserFields._pwResetSendDate:{
    "type": str,
    "required": False,
    "mutable": True,
    "editable": True,
    "interactive": False,
    "default_value": "",
    "pickable": True,
    },
    UserFields.businessType:{
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": False,
        "default_value": None,
        "pickable": True,
        },
    UserFields.user_type:{
    "type": str,
    "required": False,
    "mutable": True,
    "editable": True,
    "interactive": False,
    "default_value": "",
    "pickable": True,
    },
    UserFields.postal:{
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": False,
        "default_value": None,
        "pickable": True,
    },
    UserFields.auth_code:{
        "type": str,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": False,
        "default_value": None,
        "pickable": True,
    },
    UserFields.phoneVerified:{
        "type": bool,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": False,
        "default_value": False,
        "pickable": True,
    },
    UserFields.emailVerified:{
        "type": bool,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": False,
        "default_value": False,
        "pickable": True,
    },   
    UserFields.country:{
        "type": dict or None,
        "required": False,
        "mutable": True,
        "editable": True,
        "interactive": False,
        "default_value": False,
        "pickable": True,
    }    
}

USER_FIELDS = UserFields(fields_props=UserFieldProps).filtered_keys('pickable', True)
PHONE_FIELDS = PhoneInfosFields(fields_props=PhoneInfosFieldProps).filtered_keys('pickable', True)
