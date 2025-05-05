import json
import pydash
from typing import List, Iterable, Any, Union
import hashlib
from cryptography.fernet import Fernet
import os
import base64
from datetime import (date, datetime, time)
from urllib.parse import urlparse, parse_qs
import re
import random
from google.cloud.firestore_v1.document import Timestamp
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from datetime import timedelta

hash = hashlib.sha1(str(os.getenv('CRYPTO_KEY')).encode())
ENCRYPTION_KEY = base64.b64encode(hash.hexdigest()[:32].encode()).decode();
from urllib.parse import unquote

camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')


def boolean(data):
    if type(data) is bool:
        return data;
    if type(data) is str:
        if data.lower() == 'true':
            return True;
        if data.lower() == 'false':
            return False;
    return None;

class Object:
    def __init__(self, **kwargs):
        if kwargs is not None:
            for k, v in kwargs.items():
                setattr(self, k, v);

def split_by_crlf(s):
    return [v for v in s.splitlines() if v]

def split_by_comma(s):
    sp = s.split(',')
    if len(sp) > 0:
        splitted = [];
        for split in sp:
            splitted.append(str(split).lstrip())
        return splitted;
    return []


def read_file(_filename=None, isJson=False):
    filename = _filename
    fp = filename
    if filename is None:
        return None
    if os.path.isabs(filename) is False:
        fp = os.getcwd() + "/" + filename
    content = open(fp, 'r').read()
    try:
        if isJson is True:
            return json.loads(content)
        else:
            return content
    except Exception as e:
        return None

def isBase64(data):
    try:
        decoded = decode_base64(data)
        return decoded != data
    except Exception:
            return False

def encode_if_not_base64(data) -> 'str | None':
    try:
        if isBase64(data):
            return data
        return encode_base64(data)
    except Exception as e:
        return None;
 
def decode_if_base64(data) -> 'str | None':
    try:
        if isBase64(data):
            return decode_base64(data)
        return data;
    except Exception as e:
        print('base 64 decode error', e)
        return None

def generate_random_code():
    start = random.randint(2000, 5000)
    start1 = random.randint(6000, 9000)
    end = random.randint(start, random.randint(start, start1))
    return random.randint(start, end)

def format_query_filter(key: str, value: any, comparator: str):
    """
        key A key existing in document data
        @{value} The value used to compare
        comparator The method used to compare (==, in...)
    """
    query = {};
    query["key"] = key
    query["value"] = value
    query['comp'] = comparator
    return query

def camel_to_underscore(name):
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)

def underscore_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)

def convert_to_camelcase(obj):
    data = {}
    for key in pydash.keys(obj):
        data[underscore_to_camel(key)] = obj[key];
    return data;
def convert_to_underscore(obj):
    data = {}
    for key in pydash.keys(obj):
        data[camel_to_underscore(key)] = obj[key];
    return data;

def add_param_to_url(input_url,  params):
    import urllib.parse as urlparse
    from urllib.parse import urlencode
    url_parts = list(urlparse.urlparse(input_url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)

def get_url_params(url):
    try:
        parse_result = urlparse(url)
        query_params_dict = parse_qs(parse_result.query);
        query_params = {};
        for key in pydash.keys(query_params_dict):
            query_params[key] = ' '.join(map(str, query_params_dict[key]));
        return query_params;
    except:
        return None;


def encode_base64(data: str):
    string_bytes = data.encode("ascii")
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string;

def decode_base64(data_base64: str):
    base64_bytes = data_base64.encode("ascii")
    string_bytes = base64.b64decode(base64_bytes)
    decoded_string = string_bytes.decode("ascii")
    return unquote(decoded_string)

class Crypto:

    
    # print(hash.hexdigest())
    fernet = Fernet(ENCRYPTION_KEY);
    def encrypt(self, message:str):
        return self.fernet.encrypt(message.encode()).decode();

    def decrypt(self, encrypted:str):
        return self.fernet.decrypt(encrypted).decode();

    def hash(self, message:str):
        return hashlib.sha256(str(message).encode()).hexdigest();
    
    def generate_id(self, message:str):
        return hashlib.md5(str(message).encode()).hexdigest();

    def generate_token(self, message:str):
        encrypted_token = self.encrypt("token~"+message);
        hash_token = hashlib.md5(str(encrypted_token).encode()).hexdigest();
        return encode_base64(hash_token)
    
    def decrypt_token(self, message:str):
        try:
            d = self.decrypt(decode_base64(message));
            token_split = d.split('~');
            token = json.loads(token_split[1])
            return token
        except:
            return None;


class RequestFields:
    data = 'data';
    fields = 'fields';

def get_request_fields(field_string, fields, default_fields):
    if type(field_string) is list:
        return field_string
    
    request_fields =[];
    load_fields = [];
    if type(field_string) is list:
        load_fields = field_string
    else:
        load_fields = ArrayUtils.join_string_to_array(field_string,',');
    # print('load_fields', load_fields)
    # print('load_fields', fields)
    hasObjective = False
    if bool(load_fields):
        for f in load_fields:
            parts = parts = f.split('.')
            attr = parts[0]
            if attr == 'objective':
                # print('attr', attr)
                # print('parts', parts)
                # print('fields', fields)
                hasObjective = True
            if attr in fields:
                request_fields.append(f)
            # if len(parts) > 1:
            #     if attr in fields:
            # else:
            #     if attr in:
            #         request_fields.append(f)

        # request_fields = ArrayUtils.pick(fields, load_fields);
    
    if bool(request_fields) is False:
        request_fields = [fields[0]]
    if default_fields is not None:
        for f in default_fields:
            if f not in request_fields:
                request_fields.append(f);
    
    response = [];
    for f in request_fields:
        response.append(str(f).strip())
    
    return response;

import inspect
def get_class_properties(cls, property='__match_args__'):
        inspected = inspect.getmembers(cls, lambda a:not(inspect.isroutine(a)))
        # attr = [a for a in inspected if not(a[0].startswith('__') and a[0].endswith('__'))]
        attr = [a[1] for a in inspected if a[0]=='__match_args__']
        if(len(attr)>0):
            if type(attr[0]) is tuple:
                return list(attr[0])
        return list(attr)

def get_object_model_class(object_model, cls, fields=None, property='__match_args__'):
        obj = object_model
        if obj is None:
            obj = {};
        attributes = get_class_properties(cls, property);
        for key in attributes:
            if key not in obj:
                try:
                    obj[key] = getattr(cls, key, None)
                except Exception as err:
                    obj[key] = None

        data_object = obj.copy()
        keys = DictUtils.get_keys(data_object);
        if fields is not None:
            for key in keys:
                if key in fields:
                    # print(data_object[key])
                    if key not in data_object or data_object[key] is None or data_object[key] == 'None':
                        if 'default_value' in fields[key]:
                            data_object[key] = fields[key]['default_value']
        return data_object, keys

def init_class_kwargs(cls, obj, class_fields, class_fields_props, class_collection_name, ids_key: list[str], **kwargs):
        cls_object, keys = get_object_model_class(obj, cls, class_fields_props);
        kwargs['fields'] = class_fields
        kwargs['fields_props'] = class_fields_props

        for key in ids_key:
            documentId = None;
            if key in cls_object:
                documentId = cls_object[key]
            if documentId is not None and bool(documentId):
                # print('docId', documentId)
                kwargs['id'] = documentId;
                break;
        
        collection_name = getattr(kwargs, 'collection_name', None)
        if collection_name is None or bool(collection_name) is False:
            if class_collection_name is not None:
                kwargs['collection_name'] = class_collection_name;
        return cls_object, keys, kwargs;

class BaseClass:

    @staticmethod
    def from_dict(element, db=None, collection_name=None) -> 'Any':
        return NotImplementedError('from_json  static method must be implemented')
    def __init__(self, fields=None, fields_props=None):
        self.fields = fields;
        self.fields_props = fields_props;
    def toListDict(self, elements, fields=['id']):
        if not isinstance(elements, list):
            return None;
        result = []
        for element in elements:
            if getattr(self, 'to_dict', None) is not None:
                if fields is not None and type(fields) is list and len(fields)>0:
                    result.append(DictUtils.filter_by_fields(element.to_dict(), fields))
                else:
                    result.append(element.to_dict())
            elif getattr(self, 'to_json', None) is not None:
                result.append(element.to_json(fields))
        return result


    def fromListDict(self, elements, cls=None):
        if elements is None:
            return None
        result = []
        for element in elements:
            if getattr(self, 'from_dict', None) is not None:
                result.append(self.from_dict(element))
        return result
        
    def to_json(self, _fields=None):
        fields = None
        if getattr(self, 'fields', None) is not None:
            fields = self.fields
        else:
            fields = self.__dict__.items()
        if _fields is not None and type(_fields) is list and len(_fields)>0:
            fields = get_request_fields(_fields, fields, [fields[0]]);
            
        json_object, keys = get_object_model_class({}, self, getattr(self, "fields_props", None));
        if fields is None or type(fields) is not list or len(fields)==0:
            return json.loads(json.dumps(json_object, cls=JsonEncoder))
        return json.loads(json.dumps(DictUtils.filter_by_fields(json_object, fields), cls=JsonEncoder, fields=fields))
    
class BaseFieldsClass:
    class_fields_props: dict
    def __init__(self, fields_props=None, **kwargs):
        self.class_fields_props = fields_props
            
    def keys(self):
        return DictUtils.get_keys(self.class_fields_props);

    def filtered_keys(self, field, condition=True):
        mutable = DictUtils.filter(self.class_fields_props, DictUtils.get_keys(self.class_fields_props), field, condition)
        return DictUtils.get_keys(mutable);

    def check_create_fields(self, request_data, fieldsProps = None):
        result = {}
        fields = fieldsProps
        if fieldsProps is None:
            fields = self.class_fields_props
        if not request_data or not isinstance(request_data, dict):
            return {"error": "Invalid request data"}
        
        for field in fields:
            if field in request_data:
                # if isinstance(request_data[field], fields[field]['type']):
                types = fields[field]['type']
                if not isinstance(types,list):
                    types = [types]
                if type(request_data[field]) in types:
                    if fields[field]['mutable']:
                        result[field] = request_data[field]
                else:
                    if fields[field]['required']:
                        return {"error": f"Invalid type for field: {field} {type(request_data[field])}"}
            else:
                if fields[field]['required']:
                    return {"error": f"Missing required field: {field}"}
        return result

    @staticmethod
    def merge_model_data(model, data):
        if not isinstance(data, dict) or not isinstance(model, dict):
            return None
        result = data
        for key in model:
            if key not in data:
                result[key] = model[key]
        return result

class JsonEncoder(json.JSONEncoder):
    def __init__(self, *args, fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = fields
    def default(self, obj):
        # try:
        #     iterable = iter(obj)
        # except TypeError:
        #     pass
        # else:
        #     return list(iterable)
        # Let the base class default method raise the TypeError
        #return json.JSONEncoder.default(self, obj)
 
        attr = getattr(obj, '__dict__', None)
        to_json = getattr(obj, 'to_json', None)
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, "to_dict"):
            # return {k: v for k, v in obj.__dict__.items()}
            return obj.to_dict(self.fields)
        elif hasattr(obj, "__dict__"):
            # return {k: v for k, v in obj.__dict__.items()}
            return obj.__dict__
        else:
            return None

        # if to_json is not None:
        #     # return obj.__dict__
        #     print('to json',obj.) 
        #     return obj
        # return None

class DateUtils:

    @staticmethod
    def get_current_date_time():
        return datetime.now();

    @staticmethod
    def reset_date_time(_date: datetime):
        # new_date = _date.replace(hour=0, minute=0, second=0, microsecond=0)
        return datetime.combine(_date.date(), time(0, 0, 0, 0));
    @staticmethod
    def is_past_date(date):
        try:
            now = DateUtils.reset_date_time(datetime.now())
            return now > DateUtils.reset_date_time(date);
        except Exception as e:
            print('e', e)
            return None;
    @staticmethod
    def is_superior(date: datetime, date2: datetime):
        try:
            return DateUtils.reset_date_time(date) > DateUtils.reset_date_time(date2);
        except Exception as e:
            return None;
    @staticmethod
    def is_equal(date: datetime, date2: datetime):
        try:
            return DateUtils.reset_date_time(date) == DateUtils.reset_date_time(date2);
        except Exception as e:
            return None;
    @staticmethod
    def from_iso(date_str):
        try:
            return date.fromisoformat(date_str);
        except Exception as e:
            return None;

    @staticmethod
    def from_timestamp(date_str):
        try:
            return datetime.fromtimestamp(float(date_str));
        except Exception as e:
            return None;
    @staticmethod
    def isExpired(date_str):
        try:
            return datetime.fromisoformat(date_str) < datetime.now();
        except Exception as e:
            return None;
    @staticmethod
    def convert_firestore_timestamp_to_str(firestore_timestamp: Timestamp, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Convert Firestore Timestamp to a formatted string.

        Args:
            firestore_timestamp (Timestamp): The Firestore Timestamp to convert.
            fmt (str): The format for the output string (default is "%Y-%m-%d %H:%M:%S").

        Returns:
            str: The formatted string representation of the timestamp.
        """

        dt = None
        if isinstance(firestore_timestamp, Timestamp) is True:
            # Convert Firestore Timestamp to a datetime object
            dt = firestore_timestamp.to_datetime()
        elif isinstance(firestore_timestamp, DatetimeWithNanoseconds) is True:
            dt = DateUtils.from_timestamp(firestore_timestamp.timestamp())
        
        if dt is None:
            return firestore_timestamp
        
        # Format the datetime object to a string
        return dt.strftime(fmt)
    @staticmethod
    def getDateFromEn(date_string: str):
        slashes = len(str(date_string).split('/')) == 3
        date_string = str(date_string).replace('/', '-')
        try:
            date_format = "%Y-%m-%d"
            date_obj = datetime.strptime(date_string, date_format)
            return {"status": "ok", "date": date_obj, "format": "en", "isSlash": slashes}
        except ValueError as e:
            try:
                date_format = "%d-%m-%Y"
                date_obj = datetime.strptime(date_string, date_format)
                return {"status": "ok", "date": date_obj, "format": "fr", "isSlash": slashes}
            except:
                return {"status": "error", "date": None, "error": {'message': f"Incorrect data format {date_string}, should be YYYY-MM-DD"}}

    @staticmethod
    def format_campaign_date(data: dict, set_end_date = True):
        if not isinstance(data, dict):
            return {"error": {"message":"Invalid data"}}
        start = None
        end = None
        for key, value in data.items():
            if key =='startDate':
                start = value
            elif key == 'endDate':
                end = value
        try:
            _DATE_FORMAT_GOOGLE = "%Y%m%d"
            _DATE_FORMAT_FR = "%d/%m/%Y"
            _DATE_FORMAT_EN = "%Y-%m-%d"
            campaign = {};
            startDate = None;
            endDate = None
            startDateFormat = None;
            endDateFormat = None;
            slashes = []

            if start is not None:
                date_object = DateUtils.getDateFromEn(start);
                if date_object['status']=='error':
                    return {"status": "error", "campaign": None, "error": date_object['error']};
                
                startDate = date_object['date']
                if DateUtils.is_past_date(startDate) is True:
                    return {"status": "error", "campaign": None, "error": {'message': 'Start date cannot be in the past'}};
                startDateFormat = date_object['format']
                slashes.append(date_object['isSlash'])
                campaign['startDateFormattedGoogle'] = datetime.strftime(startDate, _DATE_FORMAT_GOOGLE);
                campaign['startDateFrench'] = datetime.strftime(startDate, _DATE_FORMAT_FR);
                campaign['startDateEnglish'] = datetime.strftime(startDate, _DATE_FORMAT_EN);

            # Optional: Set the end date.
            if startDate is not None and set_end_date is True:
                endDate = startDate + timedelta(weeks=10)
            # end_time = date + timedelta(weeks=10);
            if end is not None and bool(end) is True:
                date_object = DateUtils.getDateFromEn(end);
                if date_object['status']=='error':
                    return {"status": "error", "campaign": None, "error": date_object['error']};
                endDate = date_object['date'];
            
            if endDate is not None:
                if DateUtils.is_past_date(endDate) is True:
                    return {"status": "error", "campaign": None, "error": {'message': 'End date cannot be in the past'}};
                if DateUtils.is_superior(startDate, endDate) is True:
                    return {"status": "error", "campaign": None, "error": {'message': 'Start date cannot be superior to end date'}};
                if DateUtils.is_equal(startDate, endDate) is True:
                    return {"status": "error", "campaign": None, "error": {'message': 'Start date cannot be equal to end date'}};
                endDateFormat = date_object['format']
                campaign['endDateFormattedGoogle'] = datetime.strftime(endDate, _DATE_FORMAT_GOOGLE);
                campaign['endDateFrench'] = datetime.strftime(endDate, _DATE_FORMAT_FR);
                campaign['endDateEnglish'] = datetime.strftime(endDate, _DATE_FORMAT_EN);
                if 'endDate' not in data:
                    format = None
                    if startDateFormat == 'fr' or endDateFormat == 'fr':
                        format = datetime.strftime(endDate, _DATE_FORMAT_FR);
                    else:
                        format = datetime.strftime(endDate, _DATE_FORMAT_EN);
                    if True in slashes:
                        format = format.replace('-', '/')
                    campaign['endDate'] = format;

            

            return {"status": "ok", "campaign": campaign, "error": None};
        except Exception as e:
            print(e);
            return {"status": "error", "campaign": None, "error": {'message': str(e)}};

class DictUtils:

    @staticmethod
    def pick_object_values(obj, keys: list[str]):
        cls_object = {};
        for attr in keys:
            cls_object[attr] = pydash.get(obj, attr, None)
        return cls_object
    @staticmethod
    def every_match(element, exceptions=[]):
        if element is None:
            return False;
    
        data = pydash.omit(element, exceptions);
        keys = pydash.keys(data);
        if bool(keys) == False:
            return False;
    
        for key in keys:
            if bool(data[key]) is False:
                print("key", key);
                print("data", data[key]);
                return False;
        return True;

    @staticmethod
    def difference(first_dict, second_dict):
        return { k : second_dict[k] for k in set(second_dict) - set(first_dict) }

    @staticmethod
    def compare_nested_objects(obj1: dict, obj2: dict, path: str = '') -> dict:
        """
        Compare two nested dictionaries and return the changed fields, including lists.

        Args:
            obj1 (dict): The first dictionary to compare.
            obj2 (dict): The second dictionary to compare.
            path (str): The current path in the nested structure (used for recursion).

        Returns:
            dict: A dictionary containing the paths of changed fields and their values.
        """
        changes = {}

        # Get all keys from both dictionaries
        all_keys = set(obj1.keys()).union(set(obj2.keys()))

        for key in all_keys:
            # Create the current path
            current_path = f"{path}.{key}" if path else key

            # Check if the key exists in both dictionaries
            if key in obj1 and key in obj2:
                if isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
                    # If both values are dictionaries, recurse
                    nested_changes = DictUtils.compare_nested_objects(obj1[key], obj2[key], current_path)
                    changes.update(nested_changes)
                elif isinstance(obj1[key], list) and isinstance(obj2[key], list):
                    # If both values are lists, compare them
                    list_changes = ArrayUtils.compare_lists(obj1[key], obj2[key], current_path)
                    changes.update(list_changes)
                elif obj1[key] != obj2[key]:
                    # If values are different, record the change
                    changes[current_path] = {'old_value': obj1[key], 'new_value': obj2[key]}
            elif key in obj1:
                # Key exists only in obj1
                changes[current_path] = {'old_value': obj1[key], 'new_value': None}
            else:
                # Key exists only in obj2
                changes[current_path] = {'old_value': None, 'new_value': obj2[key]}

        return changes



    @staticmethod
    def get_changed_field(a, b):
        keys_a = pydash.keys(a);
        keys_b = pydash.keys(b);
        changed_a = [];
        changed_b = [];
        for k in keys_a:
            if k in b:
                if isinstance(b[k], dict):
                    changed = DictUtils.get_changed_field(b[k], a[k]);
                    if k == "phoneInfo":
                        print('changed e', changed)
                    if len(changed)>0:
                        changed_a.append(k);
                        continue;

                if a[k]!=b[k]:
                    changed_a.append(k);
            else:
                changed_a.append(k);
        
        for k in keys_b:
            if k in a:
                if b[k]!=a[k]:
                    if isinstance(a[k], dict):
                        changed = DictUtils.get_changed_field(a[k], b[k]);
                        if len(changed)>0:
                            changed_b.append(k);
                            continue;
                    changed_b.append(k);
            else:
                changed_b.append(k);
        
        changed_fields = pydash.uniq(changed_a + changed_b);
        return changed_fields;

    @staticmethod
    def dict_from_keys(a, keys):
        return pydash.pick(a, keys);

    @staticmethod
    def get_keys(a):
        return pydash.keys(a);
    
    @staticmethod
    def merge_dict(current_dict, target_dict, force=False):
        final_dict = target_dict.copy()
        for key in pydash.keys(current_dict):
            if force is True or key not in final_dict or final_dict[key]!=current_dict[key]:
                final_dict[key] = current_dict[key]
        return final_dict;

    @staticmethod
    def string_to_json(element):
        try:
            return json.loads(element);
        except Exception as e:
            print(e)
            return None;
    
    @staticmethod
    def json_to_string(element):
        try:
            return json.dumps(element);
        except:
            return None;

    @staticmethod
    def pick_fields(element, array):
        return pydash.pick(element, array);

    @staticmethod
    def filter(element, keys, path, condition):
        result = {}
        for key in keys:
            if element[key][path] == condition:
                result[key] = element[key]
        return result;
    @staticmethod
    def pick(element, key, data_type, default_value=None):
            if data_type == str:
                if element is not None and key in element:
                    if bool(str(element[key])) is False:
                        if default_value is not None:
                            return default_value
                    return str(element[key]);
                else:
                    if default_value is not None:
                        return default_value
                    return '';
            if data_type == bool:
                if element is not None and key in element:
                    return bool(element[key]);
                else:
                    if default_value is not None:
                        return default_value
                    return False;
    
            if data_type == list:
                if element is not None and key in element:
                    if element[key] is None or bool(list(element[key])) is False:
                        if default_value is not None:
                            return default_value
                        else:
                            return []
                    return list(element[key]);
                else:
                    if default_value is not None:
                        return default_value
                    return [];
            if data_type == dict:
                if element is not None and key in element:
                    if element[key] is not None and bool(dict(element[key])) is False:
                        if default_value is not None:
                            return default_value
                    if element[key] is not None:
                        return dict(element[key]);
                    return None;
                else:
                    if default_value is not None:
                        return default_value
                    return None;
            if data_type == int:
                if element is not None and key in element:
                    return int(element[key]);
                else:
                    if default_value is not None:
                        return default_value
                    return 0;
            if data_type == round:
                if element is not None and key in element:
                    return round(int(str(element[key])));
                else:
                    if default_value is not None:
                        return default_value
                    return 0;
    
            if data_type == float:
                if element is not None and key in element:
                    r = float(str(element[key]))
                    print(f"{key} {r} {type(r)} {element[key]}")
                    if pydash.is_nan(r) or str(r).lower()=='nan':
                        return 0.0
                    return r;
                else:
                    if default_value is not None:
                        return default_value
                    return 0.0;
            return None;

    @staticmethod
    def filter_by_fields_(data, fields: list[str]) -> dict:
        """Filter dictionary by keeping only specified fields, including nested paths"""
        if not data or not fields:
            return {}
        if isinstance(data, list):
            return [DictUtils.filter_by_fields(item, fields) for item in data]
        
        if not isinstance(data, dict):
            return data;
        result = {}
        for field in fields:
            if '.' in field:
                # Handle nested fields
                parts = field.split('.')
                value = DictUtils.remove_none_values(data)
                for part in parts:
                    value = value.get(part, {}) if isinstance(value, dict) else {}
                if value:
                    pydash.set_(result, field, value)
            else:
                # Handle top-level fields
                if field in data:
                    result[field] = data[field]
        return DictUtils.remove_none_values(result)
    @staticmethod
    def remove_none_values(obj, keep_empty=False):
        """
        Recursively remove all None values from dictionaries and lists
        
        Args:
            obj: Dict, list, or other object to clean
            keep_empty: Boolean to determine if empty dicts/lists should be kept
            
        Returns:
            Cleaned object with all None values removed
        """
        if isinstance(obj, dict):
            cleaned = {
                key: DictUtils.remove_none_values(value, keep_empty)
                for key, value in obj.items()
                if value is not None and DictUtils.remove_none_values(value, keep_empty) is not None
            }
            return cleaned if cleaned or keep_empty else None
        
        if isinstance(obj, list):
            cleaned = [
                DictUtils.remove_none_values(item, keep_empty)
                for item in obj
                if item is not None and DictUtils.remove_none_values(item, keep_empty) is not None
            ]
            return cleaned if cleaned or keep_empty else None
        
        if isinstance(obj, (str, int, float, bool)):
            return obj
            
        return None
    @staticmethod
    def filter_by_fields_(obj, path):
        """
        Extract a value from a nested object using a dot-separated path.
        
        Args:
            obj: The object to extract from (dict, list, or any nested structure)
            path: String with dot-separated path (e.g., "user.address.street")
        
        Returns:
            The value at the specified path or None if path doesn't exist
        """
        keys = path.split('.')
        result = obj
        
        try:
            for key in keys:
                if isinstance(result, (dict, list)):
                    # Handle array indices
                    if key.isdigit() and isinstance(result, list):
                        result = result[int(key)]
                    else:
                        result = result[key]
                else:
                    return None
            return result
        except (KeyError, IndexError, TypeError):
            return None
    def filter_by_fields(obj: Any, paths: Union[List[str], str]) -> Any:
        # Convert single path to list
        if isinstance(paths, str):
            paths = [paths]
        
        # Convert paths to set for O(1) lookup
        path_set = set(paths)
            
        def should_include_value(value: Any) -> bool:
            """Check if value should be included in output"""
            return isinstance(value, (str, int, float, bool, DatetimeWithNanoseconds)) or value is None
        
        def pick_nested(obj: Any, current_path: str = '') -> Any:
            """Recursively pick values from nested structure"""
            # Handle lists
            if isinstance(obj, list):
                picked_list = [pick_nested(item, current_path) for item in obj]
                return [item for item in picked_list if item not in (None, {}, [])]
                
            # Handle non-dict values
            if not isinstance(obj, dict):
                return obj if should_include_value(obj) else None
                
            # Handle dict
            result = {}
            for key, value in obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                
                # Check if this exact path is requested
                if new_path in path_set:
                    if should_include_value(value):
                        result[key] = value
                    continue
                    
                # Check if this path is a prefix of any requested path
                if any(p.startswith(new_path + '.') for p in path_set):
                    picked = pick_nested(value, new_path)
                    if picked not in (None, {}, []):
                        result[key] = picked
                        
            return result
        
        return pick_nested(obj)

def get_nested_value(data, path):
    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    return value

class ArrayUtils:

    @staticmethod
    def compare_lists(list1: list, list2: list, path: str) -> dict:
        """
        Compare two lists and return the changes.

        Args:
            list1 (list): The first list to compare.
            list2 (list): The second list to compare.
            path (str): The current path in the nested structure.

        Returns:
            dict: A dictionary containing the paths of changed fields and their values.
        """
        changes = {}
        max_length = max(len(list1), len(list2))

        for index in range(max_length):
            current_path = f"{path}[{index}]"
            value1 = list1[index] if index < len(list1) else None
            value2 = list2[index] if index < len(list2) else None

            if value1 != value2:
                changes[current_path] = {'old_value': value1, 'new_value': value2}

        return changes
    @staticmethod
    def filter_array_with_another(array_to_filter, filter):
        return pydash.filter_(array_to_filter, lambda x: pydash.find(filter, lambda y: x==y) is not None);

    def filter(array, filter):
        return pydash.filter_(array, filter);

    @staticmethod
    def get_uniq_value(elements, _key, _key_=None, parse=False):
        keys = [];
        for element in elements:
            if parse is False:
                print('type', type(element[_key]))
                if type(element[_key]) == str or type(element[_key]) == dict:
                    keys.append(element[_key]);
                elif type(element[_key]) == list:
                    keys = pydash.arrays.concat(keys, element[_key])
                    print('here', keys)
            else:
                data = json.loads(JsonEncoder().encode(element))[_key]
                if type(element[_key]) == str or type(element[_key]) == dict:
                    keys.append(data)
                elif type(element[_key]) == list:
                    keys = pydash.arrays.concat(keys, data)
        if _key_ is None:
            return pydash.uniq(keys);
        else:
            return pydash.uniq_by(keys, _key_);
    @staticmethod
    def group_elements_by_key(elements, _key, parse=False):
        keys = ArrayUtils.get_uniq_value(elements, _key, parse);
        result = {};
        for key in keys:
            e = None;
            if parse is False:
                e = pydash.filter_(elements, lambda x: x[_key]==key);
            else:
                e = pydash.filter_(elements, lambda x: json.loads(JsonEncoder().encode(x))[_key]==key);
            if key not in result:
                result[key] = pydash.flatten([e]);
            else:
                result[key] = pydash.flatten(result[key].append(e));
        return result;
    
    @staticmethod
    def sum_grouped_by_key(elements, _key):
        result = []
        for key in pydash.keys(elements):
            sum = pydash.sum_by(elements[key], _key);
            result.append({'key': key, "sum": sum})
        return result;

    @staticmethod
    def string_to_array(element) -> 'list':
        try:
            return json.loads(element);
        except:
            return None;
    
    @staticmethod
    def join_string_to_array(element, separator='') -> 'Iterable[str]':
        try:
            split = str(element).split(separator);
            if len(split) == 0:
                if len(element) > 0:
                    return [element];
                return []
            else:
                return split;
        except:
            return [];
    
    @staticmethod
    def array_include_array(element, array_check, x = None, y = None) -> 'bool':
        
        def check_filter(check_data, filter_data):
            if x is None or bool(x) is False:
                if y is None or bool(y) is False:
                    return check_data == filter_data
                else:
                    if y in check_data:
                        return check_data[y] == filter_data
                    return False
            else:
                if y is None or bool(y) is False:
                    if x in filter_data:
                        return check_data == filter_data[x]
                    return False
                else:
                    if x in filter_data and y in check_data:
                        return filter_data[x] == check_data[y]
                    return False
                
        def filter(filter_data):
            return pydash.filter_(array_check, lambda arr: check_filter(arr,filter_data))
                 
        return pydash.filter_(element,  lambda element_data: filter(element_data))

    @staticmethod
    def array_to_string(element) -> 'str':
        try:
            return json.dumps(element);
        except:
            return None;
    @staticmethod
    def pick(element, pickable_fields) -> 'list':
        return pydash.filter_(element, lambda x: pydash.includes(pickable_fields, x))
    
    @staticmethod
    def pick_iterable_childs_with_key(iterable, pickable_fields) -> 'list':
        values = [];
        
        if iterable is None or type(iterable) is not list:
            return [];
    
        for element in iterable:
            picked = pydash.pick(element,  pickable_fields);
            if picked is not None and bool(picked) is True:
                values.append(picked);
        return values
    
    @staticmethod
    def pick_iterable_values_with_key(iterable, field) -> 'list':
        values = [];
        
        if iterable is None or type(iterable) is not list:
            return [];
    
        for element in iterable:
            if field in element and bool(element[field]) is True:
                values.append(element[field]);
        return values;

    @staticmethod
    def class_list_to_list_dict(classes):
        values = [];
        for class_object in classes:
            to_json = getattr(class_object, "to_json", None)
            if callable(to_json):
                values.append(class_object.to_json());
        return values;
    @staticmethod
    def find(array, predicate):
        return pydash.find(array, predicate)


class RequestUtils:
    @staticmethod
    def get_data(request):
        print(request.data.decode())
        data_request = DictUtils.string_to_json(request.data.decode())
        print("data request",data_request)
        return data_request;