from adafri.utils.utils import JsonEncoder, DictUtils, get_object_model_class, BaseClass
from dataclasses import dataclass
import json
import pydash
from firebase_admin.firestore import firestore
from google.cloud.firestore_v1.base_query import FieldFilter, And
from google.cloud.firestore_v1.field_path import FieldPath
import os
from ..auth.firebase_auth import FirestoreApp

def getTimestamp():
    return firestore.SERVER_TIMESTAMP;


@dataclass(init=False)
class FirebaseCollectionBase(BaseClass):
    # _db: firestore.Client = None;
    # _fields_props = None;
    # _collection_name = None;

    def __init__(self, collection_name=None, db: firestore.Client=None, fields=None, fields_props=None, id=None):
        self.collection_name = collection_name;
        self.db = db;
        self.id = id;
        if self.db is None:
            self.db = FirestoreApp().firestore_client()
        super().__init__(fields=fields, fields_props=fields_props);
        
    def print_db(self):
        print('db prtiny',self.db)

    def setFields(self, fields):
        self.fields_props = fields;
    
    def generate_model(self, _key_):
        user = {};
        props = self.fields_props
        for k in DictUtils.get_keys(props):
            user[k] = props[k][_key_];
        return user;

    def collection(self, name=None):
        if name is not None:
            return self.db.collection(name)
        return self.db.collection(self.collection_name)

    def document_reference(self, _id=None) -> 'firestore.DocumentReference':
        id = _id;
        if id is None:
            if self.id is not None:
                id = self.id;
        return self.collection().document(id);

    # def get(self, id):
    #     if id is None or bool(id) is False:
    #          return None;
    #     doc = self.document_reference(id).get();
    #     if doc.exists is False:
    #         return None;
    #     return doc.to_dict();


    
    def update(self, id, data, merge=True):
        if id is None or bool(id) is False:
            return None;
        doc = self.document_reference(id);
        if doc.get().exists is False:
            return None;
        try:
            doc.set(data, merge=merge);
            return data;
        except:
            return None
    
    def remove(self, id):
        if id is None or bool(id) is False:
             return None;
        doc = self.document_reference(id);
        if doc.get().exists is False:
            return None;
        try:
            doc.delete();
            return id;
        except:
            return None

    def batchSingle(self, data_filter, key=FieldPath.document_id(), batch_size = 10):
        results = []
        # Split the user_ids list into batches of 10
        for i in range(0, len(data_filter), batch_size):
            batch_ids = data_filter[i:i + batch_size]
            # Query the "users" collection with `in` filter
            query = self.collection().where(FieldPath.document_id(), "in", batch_ids)
            
            # Fetch and add results
            docs = query.stream()
            results.extend([{"id": doc.id, **doc.to_dict()} for doc in docs])
        return results
    def custom_query(self, query_params, first=True, limit: int=None, collection_name=None):
        i = 0;
        dynamic_query = None;
        filters = []
        keys = []
        values = []
        if bool(query_params) is True:
            while i < len(query_params):
                query = query_params[i];
                
                key = None;
                if 'key' in query:
                    key = query['key'];
                if key not in keys:
                    keys.append(key)
                
                comparator = None;
                if 'comp' in query:
                    comparator = query['comp']

                value = None;
                if 'value' in query:
                    value = query['value'];
                    if value not in values:
                        values.append(value)
                if None not in [key, comparator, value]:
                    filters.append(FieldFilter(key, comparator, value))
                i+=1;
        if len(keys) == 1 and len(values) > 0:
            filters = [FieldFilter(keys[0], 'in', values)]

        dynamic_query = None;
        if bool(filters) is True:
            and_filter = And(filters=filters)
            dynamic_query = self.collection(collection_name).where(filter=and_filter)
                
        else:
            dynamic_query = self.collection(collection_name)
            
        if dynamic_query is None:
            return None
        _limit = limit
        if _limit is not None and _limit > 0 or first:
            if _limit is None:
                _limit = 1
            # print('limit', _limit)
            dynamic_query = dynamic_query.limit(_limit)
        
        data = []
        values = None;
        try:
            values = dynamic_query.get();
        except Exception as query_exception:
            print('query exception', query_exception)
            return None;
        for stream in values:
            data.append({"id": stream.id, **stream.to_dict()});
        if first is False:
            if len(data) == 0:
                return []
            return data;
        else:
            if len(data) == 0:
                return None;
            return data[0]

    def queryBatch(self, cls, key, data_filter, first=False):
        result = [];
        query_result = self.batchSingle(data_filter, 10)
        batch_size = 10
        dict_values = {"db": self.db, "collection_name": self.collection_name}
        if bool(query_result):
            if first:
                return cls.from_dict(**{key: query_result[0], **dict_values})
            else:
                for doc in query_result:
                    result.append(cls.from_dict(**{key: doc, **dict_values}))
                return result
        return [];
    def query(self, cls, key, query_params: list, first=False, limit=None, collection_name=None):
        result = [];
        query_result = self.custom_query(query_params, first=first, limit=limit, collection_name=collection_name)
        collection = collection_name
        if collection is None:
            collection = self.collection_name
        dict_values = {"db": self.db, "collection_name": collection}
        if bool(query_result):
            if first:
                return cls.from_dict(**{key: query_result, **dict_values})
            else:
                for doc in query_result:
                    result.append(cls.from_dict(**{key: doc, **dict_values}))
                return result
        if first:
                return None
        return [];
        
    
    # def to_json(self, _fields=None):
    #     # Convert the class attributes to a dictionary and then to JSON
    #     return json.loads(json.dumps(self, cls=JsonEncoder))
    


