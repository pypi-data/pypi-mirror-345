
import os
from sendgrid.helpers.mail import Email, Personalization
from sendgrid import SendGridAPIClient, Mail as SendGridMail
import urllib.parse

from datetime import datetime
from adafri.v1.user import User
from adafri.utils import generate_random_code, ResponseStatus, ApiResponse, Error, StatusCode
from adafri.v1.auth.oauth import Code
from adafri.utils import (Object, boolean, Crypto)

VALIDATION_FIELD = '_emailValidationSendDate'
PSW_RESET_FIELD = '_pwResetSendDate'
STATUS_FIELD = 'status'

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY');
REGISTRATION_TEMPLATE_ID = os.environ.get('REGISTRATION_TEMPLATE_ID')
PAYMENT_TEMPLATE_ID = os.environ.get('PAYMENT_TEMPLATE_ID')
EMAIL_VERIFICATION_TEMPLATE_ID = os.environ.get('EMAIL_VERIFICATION_TEMPLATE_ID')
try:
    os_value = os.environ.get('DEFAULT_EMAIL_TIME_TO_RESEND');
    if os_value is None:
        DEFAULT_EMAIL_TIME_TO_RESEND = 10
    else:
        DEFAULT_EMAIL_TIME_TO_RESEND = int(str(os_value))
except:
    DEFAULT_EMAIL_TIME_TO_RESEND = 10;



def compareTimes(date_string: str):
    date_format = "%Y-%m-%d, %H:%M:%S"
    date = datetime.strptime(date_string, date_format);
    now = datetime.now();
    difference = now - date;
    days, seconds = difference.days, difference.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if minutes >= DEFAULT_EMAIL_TIME_TO_RESEND:
        return {"status": "ok", "difference": minutes};
    return {"status": "error", "difference": minutes};


def setTimeSended(user: User, field=VALIDATION_FIELD):
    try:
        date_format = "%Y-%m-%d, %H:%M:%S"
        now = datetime.now()
        date_obj = datetime.strftime(now, date_format)
        update_value = {};
        update_value[field] = date_obj
        update = user.document_reference().set(update_value, merge=True)
        return update_value
    except:
        return None;

def getTimeSended(user: User, field=VALIDATION_FIELD):
    statement = {};
    if user is None:
        statement[STATUS_FIELD]='error'
        statement[field]=None
        return statement
    validation = getattr(user, field, None)
    if validation is not None and bool(validation):
        statement[STATUS_FIELD]='ok'
        statement[field]=validation
        return statement
    else:
        statement[STATUS_FIELD]='ok'
        statement[field]='now'
        return statement
    


class Mail:
    def __init__(self, from_text=None, destination=None, subject=None, custom_data=None, link=None):
        self.from_text = from_text;
        self.destination = destination;
        self.subject = subject;
        self.custom_data = custom_data;
        self.link = link;
    
    def sendgrid_client(self, _api_key=None):
        api_key = _api_key;
        if api_key is None:
            api_key = SENDGRID_API_KEY;
        return SendGridAPIClient(api_key);

    def get_user(self):
        user_model = User().query([{"key": "email", "value": self.destination, "comp": "=="}], True);
        if user_model is not None and user_model.uid is None:
            return None;
        return user_model;

    def check_time_send(self, check=True, field=VALIDATION_FIELD):
        user_model = self.get_user()
        if user_model is not None and user_model.uid is None:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error('User not exist', 'USER_NOT_EXIST'))
        if check:
            print('field', field)
            time_sended = getTimeSended(user_model, field=field);
            if time_sended['status']=='error':
                return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error('User not exist', 'USER_NOT_EXIST'))
            if time_sended[field]!='now':
                compare = compareTimes(time_sended[field]);
                if compare['status'] == 'error':
                    minutes = DEFAULT_EMAIL_TIME_TO_RESEND - compare['difference']
                    return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, {"minutes": minutes}, Error(f"Please wait {minutes} minutes and retry", 'WAIT_FEW_MINUTES'))

        return ApiResponse(ResponseStatus.OK, StatusCode.status_200, user_model, None)
    
    def sendMailRegistration(self, domain, _api_key=None, _template_id=None, bccs=[]):
        if domain is None:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error('Invalid domain', 'INVALID_REQUEST'))
        result = None
        template_id = _template_id;
        if template_id is None:
            template_id = REGISTRATION_TEMPLATE_ID
        message = Mail(
            from_email=self.from_text+'@'+domain,
            to_emails=[self.destination],
            )
        try:
            message.template_id = template_id
            personalization = Personalization()
            for bcc in bccs:
                personalization.add_bcc(Email(bcc))
            message.add_personalization(personalization)
            response = self.sendgrid_client(_api_key=_api_key).send(message)
            if response.status_code==200 or response.status_code==202:
                result = ApiResponse(ResponseStatus.OK, response.status_code, {"message": "Email sent successfully"}, None)
                print(result)
            else:
                result = ApiResponse(ResponseStatus.ERROR, response.status_code, None, Error('An error occurated', 'INVALID_REQUEST'))
        except Exception as e:
            print(e)
            result = ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(str(e), 'INVALID_REQUEST'))
        
        return result
    
    def sendMailPaymentSuccess(self, domain, _api_key=None, _template_id=None, bccs=[]):
        if domain is None:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error('Invalid domain', 'INVALID_REQUEST'))
        result = None
        message = SendGridMail()
        try:
            template_id = _template_id;
            if template_id is None:
                template_id = PAYMENT_TEMPLATE_ID
            message.from_email = self.from_text+'@'+domain
            message.template_id = template_id
            personalization = Personalization()
            personalization.dynamic_template_data = self.custom_data
            personalization.add_to(Email(self.destination))
            personalization.subject = self.subject
            for bcc in bccs:
                personalization.add_bcc(Email(bcc))
            message.add_personalization(personalization)
        
            response = self.sendgrid_client(_api_key).send(message) 
            if response.status_code==200 or response.status_code==202:
                result = ApiResponse(ResponseStatus.OK, response.status_code, {"message": "Email sent successfully"}, None)
            else:
                result = ApiResponse(ResponseStatus.ERROR, response.status_code, None, Error('An error occurated', 'INVALID_REQUEST'))
        except Exception as e:
            print(e)
            result = ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(str(e), 'INVALID_REQUEST'))
        
        return result
    
    def sendMailEmailVerfication(self, domain, _api_key=None, _template_id=None, bccs=[], check=False, field=VALIDATION_FIELD) -> 'ApiResponse':
        if domain is None:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error('Invalid domain', 'INVALID_REQUEST'))
        result = None
        message = SendGridMail()
        time_sended = self.check_time_send(check);
        if time_sended.status==ResponseStatus.ERROR:
            return time_sended
        u: User = time_sended.data
        user_model = User(u.to_json())
        try:
            template_id = _template_id;
            if template_id is None:
                template_id = os.environ.get('EMAIL_VERIFICATION_TEMPLATE_ID')
            custom_data = self.custom_data;
            if self.link is not None:
                c_data = {'link': urllib.parse.unquote(self.link)}
                if custom_data is not None:
                    custom_data = {**custom_data, **c_data}
                else:
                    custom_data = c_data
            message.from_email = self.from_text+'@'+domain
            message.template_id = template_id
            personalization = Personalization()
            if self.custom_data is not None:
                personalization.dynamic_template_data = custom_data
            personalization.add_to(Email(self.destination))
            personalization.subject = self.subject
            for bcc in bccs:
                personalization.add_bcc(Email(bcc))
            message.add_personalization(personalization)
            email_test_mode = boolean(os.environ.get('EMAIL_TEST_MODE'))
            if email_test_mode is None or email_test_mode is True:
                response = Object(status_code=200, message="success")
            else:
                response = self.sendgrid_client(_api_key).send(message) 
            if response.status_code==200 or response.status_code==202:
                setTimeSended(user_model, field=field);
                result = ApiResponse(ResponseStatus.OK, response.status_code, {"message": "Email sent successfully"}, None)
            else:
                result = ApiResponse(ResponseStatus.ERROR, response.status_code, None, Error('An error occurated that\'s why your email were not sent', 'EMAIL_NOT_SENT', 1))
        except Exception as e:
            print(e)
            result = ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error(str(e), 'INVALID_REQUEST'))
        
        return result
    

class MailSetting(Mail):
    DEFAULT_CODE_VALIDATION_BODY = "Vous êtes prêts pour commencer. Saisissez le code ci dessous pour valider votre email."
    DEFAULT_RESET_PSW_BODY = "Cliquez sur le lien ci dessous pour réinitialiser votre mot de passe "
    CODE_VALIDATION_TEMPLATE_ID = os.environ.get('CODE_VALIDATION_TEMPLATE_ID')
    RESET_PASSWORD_TEMPLATE_ID = os.environ.get('RESET_PASSWORD_TEMPLATE_ID')
    def __init__(self, from_text=None, destination=None, subject=None, custom_data=None, link=None):
        super().__init__(from_text, destination, subject, custom_data, link);
    
    def generate_code(self, code_type="email_validation", field=VALIDATION_FIELD):
        user_model = self.get_user();
        code = None;
        if user_model is None:
            return ApiResponse(ResponseStatus.ERROR, StatusCode.status_400, None, Error('User not found', 'INVALID_REQUEST'))
        init = Code({"id": Code.get_id(None, target=user_model.uid, type=code_type)}).getCode();
        time_sended = None;
        u: User = None;
        if init is not None:
            time_sended = self.check_time_send(field=field);
            if time_sended.status==ResponseStatus.ERROR:
                return time_sended
            else:
                if init.is_expired():
                    u = time_sended.data;
                else:
                    code = init;
        else:
            u = user_model
        if code is None:
            user = User(u.to_json())
            uid = user.uid;
            data_code = str(generate_random_code());
            model_ = {
                "target": uid,
                "code_type": code_type,
                "code": data_code
            }
            id = getattr(Code.generate(**model_).data, 'id',None);
            code_model = Code();
            code_model.id = id;
            code_model.code = data_code;
            code_model.code_type = code_type
            code_model.expires_in = 600
            code_model.target = uid;
            code = code_model.getCode()
            if code is None or code.is_expired():
                if code_type=='password_reset':
                    code_model.code = Crypto().hash(code_model.code);
                create = Code().create(**code_model.to_json());
                return create
            
        return ApiResponse(ResponseStatus.OK, StatusCode.status_200, code.to_json(), None)

    def generate_email_validation_code(self, code_type="email_validation", domain=None, bccs=[], template_id=None, _body=None, url=None, query_params=None):
        field = VALIDATION_FIELD;
        link_url = None;
        if code_type == 'password_reset':
            field = PSW_RESET_FIELD
            if template_id is None:
                template_id = self.RESET_PASSWORD_TEMPLATE_ID;
        else:
            if template_id is None:
                template_id = self.CODE_VALIDATION_TEMPLATE_ID;
        code_request = self.generate_code(code_type=code_type, field=field) 
        print('code request', code_request)
        if code_request.status==ResponseStatus.ERROR:
            return link_url, code_request;
        code = Code(code_request.data)
        # print('code data', code_request.data)
        body = _body;
        if body is None:
            if field==PSW_RESET_FIELD:
                body = self.DEFAULT_RESET_PSW_BODY
            else:
                body = self.DEFAULT_CODE_VALIDATION_BODY
        self.custom_data = {"body": body}
        if field == VALIDATION_FIELD:
            self.custom_data['code']=code.code
            link_url = code.code
        elif field == PSW_RESET_FIELD:
            if url is None:
                url = os.environ.get('BASE_URL')
            query = {"code": code.code, "target": code.target};
            if query_params is  not None:
                query = {**query, **query_params}
            params = urllib.parse.urlencode(query=query)
            link_url = f"{url}/reset/?{params}";
            self.custom_data['link'] = link_url
            print('link', link_url)
        print('code', code.code)
        response = ApiResponse(ResponseStatus.OK, 200, {"message": "Email sent successfully", "code": code.code}, None)
        email_test_mode = boolean(os.environ.get('EMAIL_TEST_MODE'))
        if bool(email_test_mode) is True:
            response = self.sendMailEmailVerfication(domain=domain, _template_id=template_id, bccs=bccs, check=False, field=field)
        # return ApiResponse(ResponseStatus.OK, StatusCode.status_200, code.to_json(), None)
        return link_url, response