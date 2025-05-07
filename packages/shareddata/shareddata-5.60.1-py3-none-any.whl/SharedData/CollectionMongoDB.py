import pandas as pd
import numpy as np
import datetime
import math
import bson
from bson import ObjectId
import hashlib
import json


from SharedData.Database import *
from SharedData.Utils import datetype
from pymongo import ASCENDING, DESCENDING,UpdateOne
from SharedData.Logger import Logger

class CollectionMongoDB:

    # TODO: create partitioning option yearly, monthly, daily
    def __init__(self, shareddata, database, period, source, tablename,
                 records=None, names=None, formats=None, size=None, hasindex=True,
                 overwrite=False, user='master', tabletype=1, partitioning=None):
        # tabletype 1: DISK, 2: MEMORY
        self.type = tabletype

        self.shareddata = shareddata
        self.user = user
        self.database = database
        self.period = period
        self.source = source
        self.tablename = tablename
        self.subscription_thread = None
        self.publish_thread = None

        self.names = names
        self.formats = formats
        self.size = size
        if not size is None:
            if size == 0:
                self.hasindex = False
        self.hasindex = hasindex
        self.overwrite = overwrite
        self.partitioning = partitioning
                
        self._collection = None

        self.mongodb = self.shareddata.mongodb
        self.mongodb_client = self.mongodb.client[self.user]
        
        self.path = f'{user}/{database}/{period}/{source}/collection/{tablename}'
        self.relpath = f'{database}/{period}/{source}/collection/{tablename}'
        self.pkey_columns = DATABASE_PKEYS[self.database]
        self.exists = self.relpath in self.mongodb_client.list_collection_names()
        if not self.exists:
            # Create collection
            self.mongodb_client.create_collection(self.relpath)
            self._collection = self.mongodb_client[self.relpath]
            if self.hasindex:
                pkey_fields = [(f"{field}", ASCENDING) for field in self.pkey_columns]
                pkey_name = '_'.join(f"{field}_1" for field in self.pkey_columns)
                self.mongodb_client[self.relpath].create_index(pkey_fields, unique=True, name=pkey_name)
                # Create index on mtime for timestamp queries
                self.mongodb_client[self.relpath].create_index([("mtime", DESCENDING)])
        else:
            self._collection = self.mongodb_client[self.relpath]            
            pkey_fields = [(f"{field}", ASCENDING) for field in self.pkey_columns]
            pkey_name = '_'.join(f"{field}_1" for field in self.pkey_columns)            
            # Get collection indexes information
            index_info = self._collection.index_information()
            # Check for indexes other than the default _id index
            self.hasindex = any(index_name == pkey_name for index_name in index_info)
        
    @property
    def collection(self):
        return self._collection    

    def upsert(self, data):
        """
        Perform upsert operations on the collection. Can handle a single document or multiple documents.

        :param data: A dictionary representing a single document to be upserted,
                     or a list of such dictionaries for multiple documents.
        """
        if not self.hasindex:
            raise ValueError("Upsert operation is not supported for collections without index.")
        
        # If data is a DataFrame, serialize it into a list of dictionaries
        if isinstance(data, pd.DataFrame):
            data = self.df2documents(data)
        # If data is a dictionary, convert it into a list so both cases are handled uniformly
        if isinstance(data, dict):
            data = [data]

        operations = []
        missing_pkey_items = []
        for item in data:
            # Check if the item contains all primary key columns
            if not all(field in item for field in self.pkey_columns):
                missing_pkey_items.append(item)
                continue  # Skip this item if it doesn't contain all primary key columns
            
            # Remove '_id' field if present
            if '_id' in item:
                del item['_id']

            # Add modification time if not present
            if 'mtime' not in item:
                item['mtime'] = pd.Timestamp.utcnow()

            # Check if date needs to be floored to specific intervals
            if 'date' in item:
                if self.period == 'D1':
                    item = item.copy()
                    item['date'] = pd.Timestamp(item['date']).normalize()
                elif self.period == 'M15':
                    item = item.copy()
                    item['date'] = pd.Timestamp(item['date']).floor('15T')                
                elif self.period == 'M1':
                    item = item.copy()
                    item['date'] = pd.Timestamp(item['date']).floor('T')

            # MongoDB does not allow '.' in field names, so replace them with spaces
            item = {k.replace('.', ''): v for k, v in item.items()}
                
            # MongoDB does not allow '' field names, change to ' ' if name == ''
            item = {k if k != '' else ' ': v for k, v in item.items()}

            # Construct the filter condition using the primary key columns
            filter_condition = {field: item[field] for field in self.pkey_columns if field in item}
            
            # Prepare the update operation
            update_data = {'$set': item}

            # Add the upsert operation to the operations list
            operations.append(UpdateOne(filter_condition, update_data, upsert=True))
        
        # Execute all operations in bulk if more than one, otherwise perform single update
        result = []
        if len(operations) > 0:
            result = self._collection.bulk_write(operations)

        if len(missing_pkey_items) > 0:
            Logger.log.error(f"upsert:{self.relpath} {len(missing_pkey_items)}/{len(data)} missing pkey!")
        
        return result
    
    def extend(self, data):
        """
        Appends documents directly to the collection.
        
        :param data: A dictionary representing a single document to be appended,
                    or a list of such dictionaries for multiple documents.
        """
        if self.hasindex:
            raise ValueError("Extend operation is not supported for collections with index.")
        
        # Check if data is a DataFrame and serialize it into a list of dictionaries
        if isinstance(data, pd.DataFrame):
            data = self.serialize(data)
        # Convert a single dictionary into a list for uniform handling
        if isinstance(data, dict):
            data = [data]

        documents_to_insert = []
        for item in data:
            # Remove '_id' field if present
            if '_id' in item:
                del item['_id']
                
            # Add modification time if not present
            if 'mtime' not in item:
                item['mtime'] = pd.Timestamp.utcnow()

            # Check and adjust date if necessary
            if 'date' in item:
                if self.period == 'D1':
                    item = item.copy()
                    item['date'] = pd.Timestamp(item['date']).normalize()
                elif self.period == 'M15':
                    item = item.copy()
                    item['date'] = pd.Timestamp(item['date']).floor('15T')
                elif self.period == 'M1':
                    item = item.copy()
                    item['date'] = pd.Timestamp(item['date']).floor('T')

            documents_to_insert.append(item)

        # Insert all prepared documents into the collection        
        result = []
        if documents_to_insert:
            result = self._collection.insert_many(documents_to_insert)
        
        return result        
    
    def find(self, query, projection=None, sort=None, limit=None, skip=None):
        """
        Find documents in the collection based on the provided query.
        Args:
            query (dict): The query to filter documents.
            projection (dict): The fields to include or exclude in the result.
            sort (list): The fields to sort the result by.
            limit (int): The maximum number of documents to return.
            skip (int): The number of documents to skip before returning results.
        Returns:
            list: A list of documents that match the query.
        """
        if projection:
            cursor = self._collection.find(query, projection)
        else:
            cursor = self._collection.find(query)
        
        if sort:
            cursor = cursor.sort(sort)
        elif self.hasindex:
            # If no sort is specified, sort by the primary key(s) to ensure consistent order.
            sort = [(pkey, 1) for pkey in DATABASE_PKEYS[self.database]]
            cursor = cursor.sort(sort)
        elif not self.hasindex:
            # If no sort is specified, sort by the primary key(s) to ensure consistent order.
            sort = {'_id': 1}
            cursor = cursor.sort(sort)

        if skip:
            cursor = cursor.skip(skip)
        
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    def delete(self, query):
        """
        Delete documents from the collection based on the provided query.
        Args:
            query (dict): The query to filter documents to be deleted.
        Returns:
            int: The number of documents deleted.
        """
        result = self._collection.delete_many(query)
        return result.deleted_count
    
    @staticmethod
    def serialize(obj, iso_dates=False):
        """
        Recursively serialize any Python object into a nested dict/list structure,
        removing "empty" values as defined by is_empty().
        """

        # 1) Special-case Timestamps so they don't get recursed:
        if isinstance(obj, pd.Timestamp):
            # Return None if it's considered 'empty' (e.g. NaT),
            # otherwise treat it as a scalar (string, raw Timestamps, etc.)
            if iso_dates:
                return None if CollectionMongoDB.is_empty(obj) else obj.isoformat()
            else:
                return None if CollectionMongoDB.is_empty(obj) else obj

        # # Handle Python datetime.datetime objects
        if isinstance(obj, datetime.datetime):
            if iso_dates:        
                return None if CollectionMongoDB.is_empty(obj) else obj.isoformat()
            else:
                return None if CollectionMongoDB.is_empty(obj) else obj
        
        # 2) Dict
        if isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                # Recurse
                serialized_v = CollectionMongoDB.serialize(v, iso_dates)
                # Only keep non-empty values
                if serialized_v is not None and not CollectionMongoDB.is_empty(serialized_v):
                    new_dict[k] = serialized_v

            # If the resulting dict is empty, return None instead of {}
            return new_dict if new_dict else None

        # 3) DataFrame
        if isinstance(obj, pd.DataFrame):
            records = obj.to_dict(orient='records')
            # Each record is a dict, so we re-serialize it
            return [
                r for r in (CollectionMongoDB.serialize(rec, iso_dates) for rec in records)
                if r is not None and not CollectionMongoDB.is_empty(r)
            ]

        # 4) List/tuple/set
        if isinstance(obj, (list, tuple, set)):
            new_list = [
                CollectionMongoDB.serialize(item, iso_dates)
                for item in obj
                if not CollectionMongoDB.is_empty(item)
            ]
            # If the list ends up empty, return None
            return new_list if new_list else None

        # 5) For other objects with __dict__, treat them like a dict
        if hasattr(obj, "__dict__"):
            return CollectionMongoDB.serialize(vars(obj), iso_dates)
        
        # 6) Convert ObjectId to string for JSON serialization
        if isinstance(obj, ObjectId):
            return str(obj)

        # 7) Otherwise, just return the raw value if it's not "empty"
        return obj if not CollectionMongoDB.is_empty(obj) else None

    EMPTY_VALUES = {
        str: ["", "1.7976931348623157E308", "0.0", "nan", "NaN",],
        int: [0, 2147483647],
        float: [0.0, 1.7976931348623157e+308, np.nan, np.inf, -np.inf],
        datetime.datetime: [datetime.datetime(1, 1, 1, 0, 0)],
        pd.Timestamp: [pd.Timestamp("1970-01-01 00:00:00")],
        pd.NaT: [pd.NaT],
        pd.Timedelta: [pd.Timedelta(0)],
        pd.Interval: [pd.Interval(0, 0)],
        type(None): [None],
        bool: [False],
    }

    @staticmethod
    def is_empty(value):
        """
        Returns True if 'value' is a known sentinel or should be treated as empty.
        """
        # Special handling for floats
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return True
            if value in (0.0, 1.7976931348623157e+308):
                return True

        # If it's a Timestamp and is NaT, treat as empty
        if isinstance(value, pd.Timestamp):
            if pd.isna(value):  # True for pd.NaT
                return True

        # Check if value is in our known empty sets
        value_type = type(value)
        if value_type in CollectionMongoDB.EMPTY_VALUES:
            if value in CollectionMongoDB.EMPTY_VALUES[value_type]:
                return True

        # Empty containers
        if isinstance(value, (list, tuple, set)) and len(value) == 0:
            return True
        if isinstance(value, dict) and len(value) == 0:
            return True
        if isinstance(value, pd._libs.tslibs.nattype.NaTType):
            return True

        return False

    def flatten_dict(self, d, parent_key='', sep='->'):
        """
        Flatten a nested dictionary.
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def documents2df(self, documents, flatten=True, drop_empty=True, serialize=True):
        """
        Convert a list of documents into a pandas DataFrame.
        """
        if len(documents) == 0:
            return pd.DataFrame()
        # Serialize ObjectId and datetime objects
        if serialize:
            documents = self.serialize(documents)
        # Flatten each document
        if flatten:
            documents = [self.flatten_dict(doc) for doc in documents]
        
        # Convert the list of dictionaries into a DataFrame 
        df = pd.DataFrame(documents)
        
        if drop_empty:
            # Remove columns with all None values
            df = df.dropna(axis=1, how='all')
        
        # Set primary key as index        
        pkey_columns = DATABASE_PKEYS[self.database]
        if all(col in df.columns for col in pkey_columns):
            df.set_index(pkey_columns, inplace=True)

        return df
    
    def df2documents(self, df, unflatten=True, drop_empty=True):
        """
        Convert a pandas DataFrame into a list of documents.
        """
        if df.empty:
            return []
        # Retrieve the expected primary key columns for this database
        pkey_columns = DATABASE_PKEYS[self.database]
        # Convert index to columns
        df = df.reset_index()
        if len(df.columns) >= len(pkey_columns):
            for icol, col in enumerate(pkey_columns):
                if df.columns[icol]!=pkey_columns[icol]:
                    raise ValueError(f"df2documents:Expected primary key column {pkey_columns}!")


        # MongoDB does not allow '.' in field names, so replace them with spaces
        df.columns = [str(s).replace('.','') for s in df.columns]

        # Drop rows and columns with all None/NaN values
        if drop_empty:
            df = df.dropna(axis=0, how='all').dropna(axis=1, how='all')

        # Convert DataFrame to list of dictionaries
        documents = df.to_dict(orient='records')

        if drop_empty:
            # Remove empty fields in the documents
            for doc in documents:
                keys_to_remove = [key for key, value in doc.items() if CollectionMongoDB.is_empty(value)]
                for key in keys_to_remove:
                    del doc[key]

        # Unflatten the documents if needed
        if unflatten:
            documents = [self.unflatten_dict(doc) for doc in documents]

        return documents
    
    def unflatten_dict(self, d, sep='->'):
        """
        Unflatten a dictionary.
        """
        result = {}
        for key, value in d.items():
            parts = key.split(sep)
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                    current = current[part]

                else:
                    if not isinstance(current[part], dict):
                        current[part] = {}
                    current = current[part]
            current[parts[-1]] = value
        return result
            
    def documents2json(self, documents, serialize=True, drop_empty=True):
        """
        Convert a list of documents to a JSON string.
        """
        if len(documents) == 0:
            return json.dumps([])
        # Serialize ObjectId and datetime objects
        if serialize:
            documents = self.serialize(documents, iso_dates=True)

        if drop_empty:
            # Remove empty fields in the documents
            for doc in documents:
                keys_to_remove = [key for key, value in doc.items() if CollectionMongoDB.is_empty(value)]
                for key in keys_to_remove:
                    del doc[key]

        return json.dumps(documents)

    def recursive_update(self, original, updates):
        """
        Recursively update the original dictionary with updates from the new dictionary,
        preserving unmentioned fields at each level of depth.
        """
        for key, value in updates.items():
            if isinstance(value, dict):
                # Get existing nested dictionary or use an empty dict if not present
                original_value = original.get(key, {})
                if isinstance(original_value, dict):
                    # Merge recursively
                    original[key] = self.recursive_update(original_value, value)
                else:
                    # Directly assign if original is not a dict
                    original[key] = value
            else:
                # Non-dict values are directly overwritten
                original[key] = value
        return original
        
    @staticmethod
    def sort_dict(obj: object) -> object:
        """Recursively sort dictionaries by keys to ensure consistent ordering for hashing."""
        if isinstance(obj, dict):
            return {k: CollectionMongoDB.sort_dict(obj[k]) for k in sorted(obj)}
        elif isinstance(obj, list):
            return [CollectionMongoDB.sort_dict(item) for item in obj]
        else:
            return obj
            
    @staticmethod
    def get_hash(obj: dict) -> str:
        obj = CollectionMongoDB.sort_dict(obj)
        return hashlib.sha256(bson.BSON.encode(obj)).hexdigest()