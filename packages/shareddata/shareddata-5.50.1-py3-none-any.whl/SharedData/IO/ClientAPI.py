import json
import bson
from bson import json_util
from bson.objectid import ObjectId
import requests
import os
import pandas as pd
import numpy as np
import time
import lz4.frame
import lz4.frame as lz4f
import math
import datetime
import os
import logging
import threading


from SharedData.IO.SyncTable import SyncTable
from SharedData.Logger import Logger
from SharedData.Database import *


class ClientAPI:
    
    @staticmethod
    def table_subscribe_thread(table, host, port,
            lookbacklines=1000, lookbackdate=None, snapshot=False,
            bandwidth=1e6, protocol='http'):

        apiurl = f"{protocol}://{host}:{port}"
        
        records = table.records
        
        params = {                    
            'token': os.environ['SHAREDDATA_TOKEN'],            
        }

        tablename = table.tablename
        tablesubfolder = None
        if '/' in table.tablename:
            tablename = table.tablename.split('/')[0]
            tablesubfolder = table.tablename.split('/')[1] 

        url = apiurl+f"/api/subscribe/{table.database}/{table.period}/{table.source}/{tablename}"
        
        lookbackid = records.count - lookbacklines
        if tablesubfolder:
            params['tablesubfolder'] = tablesubfolder        
        if lookbacklines:
            params['lookbacklines'] = lookbacklines
        if lookbackdate:
            params['lookbackdate'] = lookbackdate
            lookbackdate = pd.Timestamp(lookbackdate)
            lookbackid, _ = records.get_date_loc(lookbackdate)
        if bandwidth:
            params['bandwidth'] = bandwidth
                
        hasindex = records.table.hasindex           
        lastmtime = pd.Timestamp('1970-01-01')
        if hasindex:
            lastmtime = np.max(records[lookbackid:]['mtime'])
            lastmtime = pd.Timestamp(np.datetime64(lastmtime))
        while True:
            try:
                params['page'] = 1
                if hasindex:
                    params['mtime'] = lastmtime
                params['count'] = records.count
                params['snapshot'] = snapshot
                snapshot = False

                response = requests.get(url, params=params)
                if response.status_code != 200:
                    if response.status_code == 204:
                        time.sleep(1)
                        continue
                    else:
                        raise Exception(response.status_code, response.text)
                
                data = lz4.frame.decompress(response.content)
                buffer = bytearray()
                buffer.extend(data)
                if len(buffer) >= records.itemsize:
                    # Determine how many complete records are in the buffer
                    num_records = len(buffer) // records.itemsize
                    # Take the first num_records worth of bytes
                    record_data = buffer[:num_records *
                                                records.itemsize]
                    # And remove them from the buffer
                    del buffer[:num_records *
                                        records.itemsize]
                    # Convert the bytes to a NumPy array of records
                    rec = np.frombuffer(
                        record_data, dtype=records.dtype)
                    if hasindex:
                        recmtime = pd.Timestamp(np.max(rec['mtime']))
                        if recmtime > lastmtime:
                            lastmtime = recmtime
                        
                    if records.table.hasindex:
                        # Upsert all records at once
                        records.upsert(rec)
                    else:
                        # Extend all records at once
                        records.extend(rec)

                pages = int(response.headers['Content-Pages'])
                if pages > 1:
                    # paginated response
                    for i in range(2, pages+1):
                        params['page'] = i                        
                        response = requests.get(url, params=params)
                        if response.status_code != 200:
                            raise Exception(response.status_code, response.text)
                        data = lz4.frame.decompress(response.content)
                        buffer = bytearray()
                        buffer.extend(data)
                        if len(buffer) >= records.itemsize:
                            # Determine how many complete records are in the buffer
                            num_records = len(buffer) // records.itemsize
                            # Take the first num_records worth of bytes
                            record_data = buffer[:num_records *
                                                        records.itemsize]
                            # And remove them from the buffer
                            del buffer[:num_records *
                                                records.itemsize]
                            # Convert the bytes to a NumPy array of records
                            rec = np.frombuffer(
                                record_data, dtype=records.dtype)
                            if hasindex:
                                recmtime = pd.Timestamp(np.max(rec['mtime']))
                                if recmtime > lastmtime:
                                    lastmtime = recmtime
                                
                            if records.table.hasindex:
                                # Upsert all records at once
                                records.upsert(rec)
                            else:
                                # Extend all records at once
                                records.extend(rec)
                        time.sleep(0.5)

                time.sleep(1)

            except Exception as e:
                msg = 'Retrying API subscription %s,%s,%s,table,%s!\n%s' % \
                    (table.database, table.period,
                     table.source, table.tablename, str(e))
                Logger.log.warning(msg)
                time.sleep(15)

    @staticmethod
    def table_publish_thread(table, host, port, lookbacklines, 
        lookbackdate, snapshot,bandwidth, protocol='http', max_requests_per_minute=100):

        if port is None:
            apiurl = f"{protocol}://{host}"
        else:
            apiurl = f"{protocol}://{host}:{port}"
        
        while True:
            try:
                records = table.records
                
                params = {                    
                    'token': os.environ['SHAREDDATA_TOKEN'],            
                }

                tablename = table.tablename
                tablesubfolder = None
                if '/' in table.tablename:
                    tablename = table.tablename.split('/')[0]
                    tablesubfolder = table.tablename.split('/')[1] 

                url = apiurl+f"/api/publish/{table.database}/{table.period}/{table.source}/{tablename}"
                                
                if tablesubfolder:
                    params['tablesubfolder'] = tablesubfolder        
                if lookbacklines:
                    params['lookbacklines'] = lookbacklines
                if lookbackdate:
                    params['lookbackdate'] = lookbackdate
                    lookbackdate = pd.Timestamp(lookbackdate)            
                if bandwidth:
                    params['bandwidth'] = bandwidth
                
                
                # ask for the remote table mtime and count

                response = requests.get(url, params=params)

                if response.status_code != 200:
                    raise Exception(response.status_code, response.text)

                response = response.json()
                remotemtime = None
                if 'mtime' in response:
                    remotemtime = pd.Timestamp(response['mtime']).replace(tzinfo=None)
                remotecount = response['count']

                client = {}
                client.update(params)
                if 'mtime' in response:
                    client['mtime'] = remotemtime.timestamp()
                client['count'] = remotecount
                client = SyncTable.init_client(client,table)

                while True:
                    try:
                        time.sleep(60/max_requests_per_minute)
                        
                        client, ids2send = SyncTable.get_ids2send(client)
                        if len(ids2send) == 0:
                            time.sleep(0.001)                            
                        else:
                            rows2send = len(ids2send)
                            sentrows = 0
                            msgsize = min(client['maxrows'], rows2send)
                            bandwidth = client['bandwidth']
                            tini = time.time_ns()
                            bytessent = 0
                            while sentrows < rows2send:
                                t = time.time_ns()
                                message = records[ids2send[sentrows:sentrows +
                                                        msgsize]].tobytes()
                                compressed = lz4f.compress(message)
                                msgbytes = len(compressed)
                                bytessent+=msgbytes                        
                                msgmintime = msgbytes/bandwidth                        
                                
                                # create a post request
                                response = requests.post(url, params=params, data=compressed)
                                if response.status_code != 200:
                                    raise Exception('Failed to publish data remote!=200 !')

                                sentrows += msgsize
                                msgtime = (time.time_ns()-t)*1e-9
                                ratelimtime = max(msgmintime-msgtime, 0)
                                if ratelimtime > 0:
                                    time.sleep(ratelimtime)

                            totalsize = (sentrows*records.itemsize)/1e6
                            totaltime = (time.time_ns()-tini)*1e-9
                            if totaltime > 0:
                                transfer_rate = totalsize/totaltime
                            else:
                                transfer_rate = 0
                            client['transfer_rate'] = transfer_rate
                            client['upload'] += msgbytes
                        
                    except:
                        break

            except Exception as e:
                msg = 'Retrying API publish %s,%s,%s,table,%s!\n%s' % \
                    (table.database, table.period,
                        table.source, table.tablename, str(e))
                Logger.log.warning(msg)
                time.sleep(15)

    @staticmethod
    def records2df(records, pkey):
        df = pd.DataFrame(records, copy=False)
        dtypes = df.dtypes.reset_index()
        dtypes.columns = ['tag', 'dtype']
        # convert object to string
        string_idx = pd.Index(['|S' in str(dt) for dt in dtypes['dtype']])
        string_idx = (string_idx) | pd.Index(dtypes['dtype'] == 'object')
        tags_obj = dtypes['tag'][string_idx].values
        for tag in tags_obj:
            try:
                df[tag] = df[tag].str.decode(encoding='utf-8', errors='ignore')
            except:
                pass
        df = df.set_index(pkey)
        return df
    
    @staticmethod
    def df2records(df, pkeycolumns, recdtype=None):
        check_pkey = True
        if len(pkeycolumns) == len(df.index.names):
            for k in range(len(pkeycolumns)):
                check_pkey = (check_pkey) & (
                    df.index.names[k] == pkeycolumns[k])
        else:
            check_pkey = False
        if not check_pkey:
            raise Exception('First columns must be %s!' % (pkeycolumns))
        
        if recdtype is None:
            df = df.reset_index()
            dtypes = df.dtypes.reset_index()
            dtypes.columns = ['tag', 'dtype']
        
            # Convert datetime columns with timezone to UTC naive datetime
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    if df[col].dt.tz is not None:
                        df[col] = df[col].dt.tz_convert('UTC').dt.tz_localize(None)
            
            # convert object to string
            tags_obj = dtypes['tag'][dtypes['dtype'] == 'object'].values
            for tag in tags_obj:
                try:
                    df[tag] = df[tag].astype(str)
                    df[tag] = df[tag].str.encode(encoding='utf-8', errors='ignore')
                except Exception as e:
                    Logger.log.error(f'df2records(): Could not convert {tag} : {e}!')
                df[tag] = df[tag].astype('|S')
                
            rec = np.ascontiguousarray(df.to_records(index=False))
            type_descriptors = [field[1] for field in rec]
            if '|O' in type_descriptors:
                errmsg = 'df2records(): Could not convert type to binary'
                Logger.log.error(errmsg)
                raise Exception(errmsg)
                    
            return rec
        else:
            df = df.reset_index()
            # Convert datetime columns with timezone to UTC naive datetime
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    if df[col].dt.tz is not None:
                        df[col] = df[col].dt.tz_convert('UTC').dt.tz_localize(None)
            
            dtypes = recdtype
            
            rec = np.full((df.shape[0],), fill_value=np.nan, dtype=dtypes)
            for col in dtypes.names:
                try:
                    if col in df.columns:
                        if pd.api.types.is_integer_dtype(dtypes[col])\
                            or pd.api.types.is_unsigned_integer_dtype(dtypes[col]):
                            df[col] = df[col].fillna(0)
                            
                        rec[col] = df[col].astype(dtypes[col])
                        
                except Exception as e:
                    Logger.log.error('df2records(): Could not convert %s!\n%s' % (col, e))

            return rec

    @staticmethod
    def get_table(database, period, source, tablename, 
            endpoint=None,
            startdate=None, enddate=None, 
            symbols=None, portfolios=None, tags=None, query=None,
            columns=None, output_dataframe=True,
            page=None, per_page=None, load_all_pages=False,
            token=None, user=None):
            
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/table/{database}/{period}/{source}/{tablename}'
        url += route
        
        if not token is None: 
            params['token'] = token 
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')

        if startdate:
            params['startdate'] = startdate
        if enddate:
            params['enddate'] = enddate
        if symbols:
            params['symbols'] = symbols
        if portfolios:
            params['portfolios'] = portfolios
        if tags:
            params['tags'] = tags
        if user:
            params['user'] = user
        if query:
            params['query'] = json.dumps(query)
        if per_page:
            params['per_page'] = per_page
        if page:
            params['page'] = page
        if columns:
            params['columns'] = columns
        
        params['format'] = 'bin'

        # Make the GET request
        # Request LZ4-encoded response
        headers = {
            'Accept-Encoding': 'lz4'
        }

        if load_all_pages:
            # Start with page 1 to get total pages from headers
            params['page'] = 1
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            if response.status_code == 204:
                return pd.DataFrame([])

            # Get total pages from headers
            total_pages = int(response.headers.get('Content-Pages', 1))
            
            # Process first page
            names = json.loads(response.headers.get('Meta-Field-Names'))
            formats = json.loads(response.headers.get('Meta-Field-Formats'))
            pkey = json.loads(response.headers.get('Meta-Field-Pkey'))
            dtype = np.dtype(list(zip(names, formats)))
            decompressed = lz4f.decompress(response.content)
            all_recs = np.frombuffer(decompressed, dtype=dtype)

            # Fetch remaining pages if there are more
            for current_page in range(2, total_pages + 1):
                params['page'] = current_page
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                
                if response.status_code != 204:
                    decompressed = lz4f.decompress(response.content)
                    page_recs = np.frombuffer(decompressed, dtype=dtype)
                    all_recs = np.concatenate((all_recs, page_recs))

            if not output_dataframe:
                return all_recs
                    
            # Convert combined records to DataFrame
            df = ClientAPI.records2df(all_recs, pkey)            
            return df.sort_index()
        else:
            # Original single page request logic
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()

            if response.status_code == 204: 
                return pd.DataFrame([])
            
            # Read field metadata from headers
            names = json.loads(response.headers.get('Meta-Field-Names'))
            formats = json.loads(response.headers.get('Meta-Field-Formats'))
            pkey = json.loads(response.headers.get('Meta-Field-Pkey'))

            # Rebuild dtype
            dtype = np.dtype(list(zip(names, formats)))

            # Decompress LZ4 payload
            decompressed = lz4f.decompress(response.content)

            # Reconstruct numpy structured array
            recs = np.frombuffer(decompressed, dtype=dtype)
            if not output_dataframe:
                return recs
                    
            # Convert to DataFrame
            df = ClientAPI.records2df(recs, pkey)
            return df.sort_index()

    @staticmethod
    def post_table(database, period, source, tablename, 
            endpoint=None, 
            names = None, formats=None, size=None,
            value=None, overwrite=False,
            token=None, user=None):
            
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/table/{database}/{period}/{source}/{tablename}'
        url += route
        
        if not token is None: 
            params['token'] = token 
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')
        
        if user:
            params['user'] = user
        if names:
            params['names'] = json.dumps(names)
        if formats:
            params['formats'] = json.dumps(formats)
        if size:
            params['size'] = int(size)
        if overwrite:
            params['overwrite'] = overwrite
        
        if not value is None:
            if isinstance(value, pd.DataFrame):
                if names and formats:
                    hdrdtype = np.dtype({'names': names, 'formats': formats})
                    value = ClientAPI.df2records(value,DATABASE_PKEYS[database],recdtype=hdrdtype)
                else:
                    value = ClientAPI.df2records(value,DATABASE_PKEYS[database])
            elif isinstance(value, np.ndarray):
                pass
            else:
                raise Exception('value must be a pandas DataFrame')
                        
            meta_names = list(value.dtype.names)
            meta_formats = [value.dtype.fields[name][0].str for name in meta_names]
            compressed = lz4f.compress(value.tobytes())
            responsebytes = len(compressed)
            
            headers = {}
            headers['Content-Encoding'] = 'lz4'
            headers['Content-Length'] = json.dumps(responsebytes)
            headers['Meta-Field-Names'] = json.dumps(meta_names)
            headers['Meta-Field-Formats'] = json.dumps(meta_formats)
            headers['Meta-Field-Pkey'] = json.dumps(DATABASE_PKEYS[database])

            # Make the POST request
            response = requests.post(
                url,
                params=params,
                data=compressed,
                headers=headers
            )
        else:
            response = requests.post(url, params=params)

        response.raise_for_status()
        
        return response.status_code
    
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
                return None if ClientAPI.is_empty(obj) else obj.isoformat()
            else:
                return None if ClientAPI.is_empty(obj) else obj

        # # Handle Python datetime.datetime objects
        if isinstance(obj, datetime.datetime):
            if iso_dates:        
                return None if ClientAPI.is_empty(obj) else obj.isoformat()
            else:
                return None if ClientAPI.is_empty(obj) else obj
        
        # 2) Dict
        if isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                # Recurse
                serialized_v = ClientAPI.serialize(v, iso_dates)
                # Only keep non-empty values
                if serialized_v is not None and not ClientAPI.is_empty(serialized_v):
                    new_dict[k] = serialized_v

            # If the resulting dict is empty, return None instead of {}
            return new_dict if new_dict else None

        # 3) DataFrame
        if isinstance(obj, pd.DataFrame):
            records = obj.to_dict(orient='records')
            # Each record is a dict, so we re-serialize it
            return [
                r for r in (ClientAPI.serialize(rec, iso_dates) for rec in records)
                if r is not None and not ClientAPI.is_empty(r)
            ]

        # 4) List/tuple/set
        if isinstance(obj, (list, tuple, set)):
            new_list = [
                ClientAPI.serialize(item, iso_dates)
                for item in obj
                if not ClientAPI.is_empty(item)
            ]
            # If the list ends up empty, return None
            return new_list if new_list else None

        # 5) For other objects with __dict__, treat them like a dict
        if hasattr(obj, "__dict__"):
            return ClientAPI.serialize(vars(obj), iso_dates)
        
        # 6) Convert ObjectId to string for JSON serialization
        if isinstance(obj, ObjectId):
            return str(obj)

        # 7) Otherwise, just return the raw value if it's not "empty"
        return obj if not ClientAPI.is_empty(obj) else None

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
        if value_type in ClientAPI.EMPTY_VALUES:
            if value in ClientAPI.EMPTY_VALUES[value_type]:
                return True

        # Empty containers
        if isinstance(value, (list, tuple, set)) and len(value) == 0:
            return True
        if isinstance(value, dict) and len(value) == 0:
            return True
        if isinstance(value, pd._libs.tslibs.nattype.NaTType):
            return True

        return False

    @staticmethod
    def flatten_dict(d, parent_key='', sep='->'):
        """
        Flatten a nested dictionary.
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(ClientAPI.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def unflatten_dict(d, sep='->'):
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
            
    @staticmethod
    def documents2df(documents, database, flatten=True, drop_empty=True, serialize=True):
        """
        Convert a list of documents into a pandas DataFrame.
        """
        if len(documents) == 0:
            return pd.DataFrame()
        # Serialize ObjectId and datetime objects
        if serialize:
            documents = ClientAPI.serialize(documents)
        # Flatten each document
        if flatten:
            documents = [ClientAPI.flatten_dict(doc) for doc in documents]
        
        # Convert the list of dictionaries into a DataFrame 
        df = pd.DataFrame(documents)
        
        if drop_empty:
            # Remove columns with all None values
            df = df.dropna(axis=1, how='all')
        
        # Set primary key as index        
        pkey_columns = DATABASE_PKEYS[database]
        if all(col in df.columns for col in pkey_columns):
            df.set_index(pkey_columns, inplace=True)

        return df
    
    @staticmethod
    def df2documents(df, database, unflatten=True, drop_empty=True):
        """
        Convert a pandas DataFrame into a list of documents.
        """
        if df.empty:
            return []
        # Retrieve the expected primary key columns for this database
        pkey_columns = DATABASE_PKEYS[database]
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
                keys_to_remove = [key for key, value in doc.items() if ClientAPI.is_empty(value)]
                for key in keys_to_remove:
                    del doc[key]

        # Unflatten the documents if needed
        if unflatten:
            documents = [ClientAPI.unflatten_dict(doc) for doc in documents]

        return documents
    
    @staticmethod
    def get_collection(database, period, source, tablename, 
                        endpoint=None, query=None, sort=None,columns=None, 
                        page=None, per_page=None,load_all_pages=False,
                        output_dataframe=True, 
                        token=None, user=None):
        
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/collection/{database}/{period}/{source}/{tablename}'
        url += route

        if not token is None:
            params['token'] = token
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')

        if user:
            params['user'] = user
        if sort:
            params['sort'] = json_util.dumps(sort)
        if query:
            params['query'] = json_util.dumps(query)
        if columns:
            params['columns'] = json_util.dumps(columns)

        if page:
            params['page'] = page
        if per_page:
            params['per_page'] = per_page  
        
        params['format'] = 'bson'
        if load_all_pages:
            all_data = []
            current_page = 1
            while True:
                if not per_page:
                    per_page = 50000

                params['page'] = current_page
                params['per_page'] = per_page
                
                # Make the API request for the current page
                response = requests.get(url, params=params)
                response.raise_for_status()

                if response.status_code == 204:
                    break

                decompressed_content = lz4f.decompress(response.content)
                bson_data = bson.BSON(decompressed_content).decode()
                data = bson_data.get('data', [])
                
                if not data:
                    break

                all_data.extend(data)

                # If less data than per_page is returned, we have reached the last page
                if len(data) < per_page:
                    break
                
                current_page += 1
            
            if not output_dataframe:
                return all_data
            
            return ClientAPI.documents2df(all_data, database)

        else:

            response = requests.get(url, params=params)
            response.raise_for_status()

            if response.status_code == 204: 
                if not output_dataframe:
                    return []
                else:
                    return pd.DataFrame()
            
            decompressed_content = lz4f.decompress(response.content)
            bson_data = bson.BSON(decompressed_content).decode()  # Decode BSON to a dictionary

            data = bson_data.get('data', [])
            if not output_dataframe:
                return data
            
            df = ClientAPI.documents2df(data,database)
            return df

    @staticmethod
    def post_collection(database, period, source, tablename, 
            endpoint=None, 
            value=None, 
            token=None, user=None):
            
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/collection/{database}/{period}/{source}/{tablename}'
        url += route

        if not token is None: 
            params['token'] = token 
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')

        if user:
            params['user'] = user

        if isinstance(value, pd.DataFrame):            
            value = ClientAPI.serialize(value.reset_index())
        else:
            value = ClientAPI.serialize(value)
        bson_data = bson.encode({'data': value})
        compressed_data = lz4f.compress(bson_data)
        headers = {}
        headers['Content-Encoding'] = 'lz4'
        headers['Content-Type'] = 'application/octet-stream'

        # Make the POST request
        response = requests.post(url, headers=headers, params=params, data=compressed_data)
        response.raise_for_status()

        return response.json()
    
    @staticmethod
    def patch_collection(database, period, source, tablename, 
            filter, update, endpoint=None,
            token=None, user=None, sort=None):     
        
        url = os.environ['SHAREDDATA_ENDPOINT'] if not endpoint else endpoint

        params = {}
        if '/' in tablename:
            tablename_split = tablename.split('/')
            tablename = tablename_split[0]
            params['tablesubfolder'] = tablename_split[1]

        route = f'/api/collection/{database}/{period}/{source}/{tablename}'
        url += route

        if not token is None: 
            params['token'] = token 
        else:
            params['token'] = os.getenv('SHAREDDATA_TOKEN')
            if not params['token']:
                raise Exception('SHAREDDATA_TOKEN not found in environment variables')

        if user:
            params['user'] = user
        
        params['filter'] = json.dumps(filter)  # Convert filter to JSON string
        params['update'] = json.dumps(update)  # Convert update to JSON string
        if sort:
            params['sort'] = json.dumps(sort)  # Convert sort to JSON string

        try:
            response = requests.patch(url, params=params)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            if response.status_code == 200:
                # Default to JSON
                rjson = json.loads(response.content)
                if not 'data' in rjson:
                    return pd.DataFrame([])
                df = pd.DataFrame([json.loads(rjson['data'])])
                if df.empty:
                    return df
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                pkey = rjson['pkey']
                df = df.set_index(pkey).sort_index()
                
                return df
            elif response.status_code == 204:
                return pd.DataFrame([])
        
        except Exception as e:
            Logger.log.error(f"ClientAPI patch_collection Error: {e}")
            raise e



