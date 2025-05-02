from flask import Flask, Response, g
from flask import request
from flask import jsonify
from flask import make_response
from flasgger import Swagger, swag_from
import bson
from bson import json_util
from bson.objectid import ObjectId
import pymongo
import os
import datetime
import gzip
import json
import time
import lz4.frame as lz4f
import pandas as pd
import numpy as np
from collections import defaultdict
import threading
from pathlib import Path
from filelock import FileLock
from queue import Queue

from SharedData.IO.MongoDBClient import MongoDBClient
from SharedData.CollectionMongoDB import CollectionMongoDB


MAX_RESPONSE_SIZE_BYTES = int(10*1024*1024)

app = Flask(__name__)
app.config['APP_NAME'] = 'SharedData API'
app.config['FLASK_ENV'] = 'production'
app.config['FLASK_DEBUG'] = '0'
if not 'SHAREDDATA_SECRET_KEY' in os.environ:
    raise Exception('SHAREDDATA_SECRET_KEY environment variable not set')
if not 'SHAREDDATA_TOKEN' in os.environ:
    raise Exception('SHAREDDATA_TOKEN environment variable not set')

app.config['SECRET_KEY'] = os.environ['SHAREDDATA_SECRET_KEY']
app.config['SWAGGER'] = {
    'title': 'SharedData API',
    'uiversion': 3
}
docspath = 'ServerAPIDocs.yml'
swagger = Swagger(app, template_file=docspath)

# Thread-safe in-memory storage for traffic statistics
traffic_stats = {
    'total_requests': 0,
    'endpoints': defaultdict(lambda: {
        'requests': 0,
        'total_response_time': 0.0,
        'status_codes': defaultdict(int),
        'total_bytes_sent': 0,
        'total_bytes_received': 0  
    })
}

traffic_rates = {
    'last_total_requests': 0,
    'last_total_bytes_sent': 0,
    'last_total_bytes_received': 0,  
    'last_timestamp': time.time()
}

# Lock for thread-safe updates to traffic_stats
stats_lock = threading.Lock()

def authenticate(request):
    try:
        token = request.args.get('token')  # Not Optional
        if not token:
            token = request.headers.get('X-Custom-Authorization')
        if token != os.environ['SHAREDDATA_TOKEN']:
            time.sleep(3)
            return False
        return True
    except:
        return False

@app.before_request
def start_timer():
    # Store the start time of the request
    g.start_time = time.time()
    # Store the inbound request size (if available)
    content_length = request.headers.get('Content-Length', 0)
    try:
        g.request_bytes = int(content_length)
    except ValueError:
        g.request_bytes = len(request.get_data()) if request.data else 0

@app.after_request
def log_request(response):
    # Calculate response time
    response_time = time.time() - g.start_time

    # Get endpoint and method
    endpoint = request.endpoint or request.path
    method = request.method

    # Calculate bytes sent (outbound)
    content_length = response.headers.get('Content-Length', 0)
    try:
        bytes_sent = int(content_length)
    except ValueError:
        bytes_sent = len(response.get_data()) if response.data else 0

    # Get bytes received (inbound) from before_request
    bytes_received = g.request_bytes

    # Update statistics in a thread-safe manner
    with stats_lock:
        traffic_stats['total_requests'] += 1
        endpoint_stats = traffic_stats['endpoints'][f"{method} {endpoint}"]
        endpoint_stats['requests'] += 1
        endpoint_stats['total_response_time'] += response_time
        endpoint_stats['status_codes'][response.status_code] += 1
        endpoint_stats['total_bytes_sent'] += bytes_sent
        endpoint_stats['total_bytes_received'] += bytes_received  # Track inbound traffic

    return response

@app.route('/api/traffic_stats', methods=['GET'])
def get_traffic_stats():
    try:
        
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401

        # Prepare statistics for response in a thread-safe manner
        stats_response = {
            'total_requests': 0,
            'endpoints': {}
        }

        with stats_lock:
            stats_response['total_requests'] = traffic_stats['total_requests']
            for endpoint, data in traffic_stats['endpoints'].items():
                stats_response['endpoints'][endpoint] = {
                    'requests': data['requests'],
                    'average_response_time': data['total_response_time'] / data['requests'] if data['requests'] > 0 else 0,
                    'status_codes': dict(data['status_codes']),
                    'total_bytes_sent': data['total_bytes_sent'],
                    'total_bytes_received': data['total_bytes_received']  # Add inbound stats
                }

        response_data = json.dumps(stats_response).encode('utf-8')
        response = Response(response_data, mimetype='application/json')
        response.headers['Content-Length'] = len(response_data)
        return response

    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response
    
@app.route('/api/heartbeat', methods=['GET', 'POST'])
def heartbeat():
    time.sleep(3)
    response_data = json.dumps({'heartbeat': True}).encode('utf-8')
    response = Response(response_data, status=200, mimetype='application/json')
    response.headers['Content-Length'] = len(response_data)
    return response

@app.route('/api/auth', methods=['GET', 'POST'])
def auth():
    try:
        # Check for the token in the header        
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
        
        response_data = json.dumps({'authenticated': True}).encode('utf-8')
        response = Response(response_data, status=200, mimetype='application/json')
        response.headers['Content-Length'] = len(response_data)
        return response
    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response

@app.route('/api/subscribe/<database>/<period>/<source>/<tablename>', methods=['GET'])
def subscribe(database, period, source, tablename):
    try:        
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401

        tablesubfolder = request.args.get('tablesubfolder')  # Optional
        if tablesubfolder is not None:
            table = shdata.table(database, period, source, tablename+'/'+tablesubfolder)
        else:
            table = shdata.table(database, period, source, tablename)

        if table.table.hasindex:
            lookbacklines = request.args.get('lookbacklines', default=1000, type=int)  # Optional
            lookbackid = table.count - lookbacklines
            if 'lookbackdate' in request.args:
                lookbackdate = pd.Timestamp(request.args.get('lookbackdate'))
                lookbackid, _ = table.get_date_loc(lookbackdate)            
            if lookbackid < 0:
                lookbackid = 0

            ids2send = np.arange(lookbackid, table.count)
            if 'mtime' in request.args:
                mtime = pd.Timestamp(request.args.get('mtime'))
                newids = lookbackid + np.where(table['mtime'][ids2send] >= mtime)[0]
                ids2send = np.intersect1d(ids2send, newids)
        else:
            clientcount = request.args.get('count', default=0, type=int)  # Optional
            if clientcount < table.count:
                ids2send = np.arange(clientcount, table.count-1)
            else:
                ids2send = np.array([])
        
        rows2send = len(ids2send)
        if rows2send == 0:
            response = Response(status=204)
            response.headers['Content-Length'] = 0
            return response
        
        # Compress & paginate the response                
        maxrows = np.floor(MAX_RESPONSE_SIZE_BYTES/table.itemsize)
        if rows2send > maxrows:
            # paginate
            page = request.args.get('page', default=1, type=int)
            ids2send = ids2send[int((page-1)*maxrows):int(page*maxrows)]

        compressed = lz4f.compress(table[ids2send].tobytes())
        responsebytes = len(compressed)
        response = Response(compressed, mimetype='application/octet-stream')
        response.headers['Content-Encoding'] = 'lz4'
        response.headers['Content-Length'] = responsebytes        
        response.headers['Content-Pages'] = int(np.ceil(rows2send/maxrows))
        return response
    
    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response
    
@app.route('/api/publish/<database>/<period>/<source>/<tablename>', methods=['GET'])
def publish_get(database, period, source, tablename):
    try:        
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
                
        tablesubfolder = request.args.get('tablesubfolder')  # Optional
        if tablesubfolder is not None:
            table = shdata.table(database, period, source, tablename+'/'+tablesubfolder)
        else:
            table = shdata.table(database, period, source, tablename)

        msg = {'count': int(table.count)}

        if table.table.hasindex:
            lookbacklines = request.args.get('lookbacklines', default=1000, type=int)  # Optional
            lookbackid = table.count - lookbacklines
            if 'lookbackdate' in request.args:
                lookbackdate = pd.Timestamp(request.args.get('lookbackdate'))
                lookbackid, _ = table.get_date_loc(lookbackdate)            
            if lookbackid < 0:
                lookbackid = 0

            ids2send = np.arange(lookbackid, table.count)            
            msg['mtime'] = pd.Timestamp(np.datetime64(np.max(table['mtime'][ids2send]))).isoformat()

        response_data = json.dumps(msg).encode('utf-8')
        response = Response(response_data, mimetype='application/json')
        response.headers['Content-Length'] = len(response_data)
        return response

    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response

@app.route('/api/publish/<database>/<period>/<source>/<tablename>', methods=['POST'])
def publish_post(database, period, source, tablename):
    try:        
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
                
        tablesubfolder = request.args.get('tablesubfolder')  # Optional
        if tablesubfolder is not None:
            table = shdata.table(database, period, source, tablename+'/'+tablesubfolder)
        else:
            table = shdata.table(database, period, source, tablename)
        
        data = lz4f.decompress(request.data)
        buffer = bytearray()
        buffer.extend(data)
        if len(buffer) >= table.itemsize:
            # Determine how many complete records are in the buffer
            num_records = len(buffer) // table.itemsize
            # Take the first num_records worth of bytes
            record_data = buffer[:num_records * table.itemsize]
            # And remove them from the buffer
            del buffer[:num_records * table.itemsize]
            # Convert the bytes to a NumPy array of records
            rec = np.frombuffer(record_data, dtype=table.dtype)
                
            if table.table.hasindex:
                # Upsert all records at once
                table.upsert(rec)
            else:
                # Extend all records at once
                table.extend(rec)
            
            response = Response(status=200)
            response.headers['Content-Length'] = 0
            return response        
        
        response = Response(status=204)
        response.headers['Content-Length'] = 0
        return response

    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response

@app.route('/api/table/<database>/<period>/<source>/<tablename>', methods=['GET', 'POST'])
@swag_from(docspath)
def table(database, period, source, tablename):
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
        
        if request.method == 'POST':
            return post_table(database, period, source, tablename, request)
        elif request.method == 'GET':
            return get_table(database, period, source, tablename, request)
        
    except Exception as e:
        time.sleep(1)  # Sleep for 1 second before returning the error
        sanitized_error = str(e).replace("\n", " ").replace("\r", " ")  # Remove new lines
        error_message = json.dumps({"type": "InternalServerError", "message": sanitized_error})
        response = Response(error_message, status=500, mimetype='application/json')
        response.headers['X-Error-Reason'] = sanitized_error  # Set the sanitized error message
        return response

def get_table(database, period, source, tablename, request):
    tablesubfolder = request.args.get('tablesubfolder')  # Optional
    startdate = request.args.get('startdate')  # Optional
    enddate = request.args.get('enddate')  # Optional
    symbols = request.args.get('symbols')  # Optional
    portfolios = request.args.get('portfolios')  # Optional
    tags = request.args.get('tags')  # Optional
    page = request.args.get('page', default='1')
    page = int(float(page))
    per_page = request.args.get('per_page', default='0')
    per_page = int(float(per_page))
    output_format = request.args.get('format', 'json').lower()  # 'json' by default, can be 'csv' and 'bin'    
    
    query = request.args.get('query')
    if query:
        query = json.loads(query)  # Optional
    else:
        query = {}

    if tablesubfolder is not None:
        tbl = shdata.table(database, period, source, tablename+'/'+tablesubfolder)
    else:
        tbl = shdata.table(database, period, source, tablename)
    
    if startdate is not None:
        startdate = pd.Timestamp(startdate).normalize()
        dti, _ = tbl.get_date_loc(startdate)
        if dti == -1:
            dti = tbl.count
    else:
        dti = 0

    if enddate is not None:
        enddate = pd.Timestamp(enddate).normalize()
        _, dte = tbl.get_date_loc(enddate)
        if dte == -1:
            dte = tbl.count
    else:
        dte = tbl.count

    # filter data
    loc = np.arange(dti, dte)
    if symbols is not None:
        symbols = symbols.split(',')
        symbolloc = []
        for symbol in symbols:
            symbolloc.extend(tbl.get_symbol_loc(symbol))
        symbolloc = np.array(symbolloc)
        if len(symbolloc) > 0:
            loc = np.intersect1d(loc, symbolloc)
        else:
            loc = np.array([])

    if portfolios is not None:
        portfolios = portfolios.split(',')
        portloc = []
        for port in portfolios:
            portloc.extend(tbl.get_portfolio_loc(port))
        portloc = np.array(portloc)
        if len(portloc) > 0:
            loc = np.intersect1d(loc, portloc)
        else:
            loc = np.array([])

    if tags is not None:
        tags = tags.split(',')
        tagloc = []
        for tag in tags:
            tagloc.extend(tbl.get_tag_loc(tag))
        tagloc = np.array(tagloc)
        if len(tagloc) > 0:
            loc = np.intersect1d(loc, tagloc)
        else:
            loc = np.array([])

    # cycle query keys
    if query.keys() is not None:
        for key in query.keys():            
            if pd.api.types.is_string_dtype(tbl[key]):
                idx = tbl[loc][key] == query[key].encode()
            elif pd.api.types.is_datetime64_any_dtype(tbl[key]):
                idx = tbl[loc][key] == pd.Timestamp(query[key])
            else:                    
                idx = tbl[loc][key] == query[key]
            loc = loc[idx]
    
    if len(loc) == 0:
        response = Response(status=204)
        response.headers['Content-Length'] = 0
        return response
    
    
    # filter columns
    pkey = DATABASE_PKEYS[database]
    columns = request.args.get('columns')  # Optional
    if columns:
        columns = columns.split(',')
        columns = np.array([c for c in columns if not c in pkey])
        columns = pkey + list(np.unique(columns))
        names = columns
        formats = [tbl.dtype.fields[name][0].str for name in names]
        dtype = np.dtype(list(zip(names, formats)))
        # Apply pagination    
        maxrows = int(np.floor(MAX_RESPONSE_SIZE_BYTES/dtype.itemsize))
        maxrows = min(maxrows,len(loc))
        if (per_page > maxrows) | (per_page == 0):
            per_page = maxrows        
        startpage = (page - 1) * per_page
        endpage = startpage + per_page        
        content_pages = int(np.ceil(len(loc) / per_page))
        recs2send = tbl[loc[startpage:endpage]]
        # Create new array
        arrays = [recs2send[field] for field in columns]
        recs2send = np.rec.fromarrays(arrays, dtype=dtype)
    else:
        # Apply pagination    
        maxrows = int(np.floor(MAX_RESPONSE_SIZE_BYTES/tbl.itemsize))
        maxrows = min(maxrows,len(loc))
        if (per_page > maxrows) | (per_page == 0):
            per_page = maxrows
        startpage = (page - 1) * per_page
        endpage = startpage + per_page        
        content_pages = int(np.ceil(len(loc) / per_page))
        recs2send = tbl[loc[startpage:endpage]]    


    
    # send response
    accept_encoding = request.headers.get('Accept-Encoding', '')
    if output_format == 'csv':
        # Return CSV
        df = tbl.records2df(recs2send)
        df = df.reset_index()
        csv_data = df.to_csv(index=False)
        if 'gzip' in accept_encoding:
            response_csv = csv_data.encode('utf-8')
            response_compressed = gzip.compress(response_csv, compresslevel=1)
            response = Response(response_compressed, mimetype='text/csv')
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response_compressed)
            response.headers['Content-Pages'] = content_pages
            return response
        else:
            response_data = csv_data.encode('utf-8')
            response = Response(response_data, mimetype='text/csv')
            response.headers['Content-Length'] = len(response_data)
            return response
    elif output_format == 'json':
        # Return JSON
        df = tbl.records2df(recs2send)
        pkey = df.index.names
        df = df.reset_index()
        df = df.applymap(lambda x: x.isoformat() if isinstance(x, datetime.datetime) else x)
        response_data = {
            'page': page,
            'per_page': per_page,
            'total': len(loc),
            'pkey': pkey,
            'data': df.to_dict(orient='records')
        }
        if 'gzip' in accept_encoding:
            response_json = json.dumps(response_data).encode('utf-8')
            response_compressed = gzip.compress(response_json, compresslevel=1)
            response = Response(response_compressed, mimetype='application/json')
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response_compressed)
            response.headers['Content-Pages'] = content_pages
            return response
        else:
            response_data_json = json.dumps(response_data).encode('utf-8')
            response = Response(response_data_json, mimetype='application/json')
            response.headers['Content-Length'] = len(response_data_json)
            return response
    else:  # output_format=='bin'
        names = list(recs2send.dtype.names)
        formats = [recs2send.dtype.fields[name][0].str for name in names]
        compressed = lz4f.compress(recs2send.tobytes())
        responsebytes = len(compressed)        
        response = Response(compressed, mimetype='application/octet-stream')
        response.headers['Content-Encoding'] = 'lz4'
        response.headers['Content-Length'] = responsebytes
        response.headers['Content-Pages'] = content_pages
        response.headers['Meta-Field-Names'] = json.dumps(names)
        response.headers['Meta-Field-Formats'] = json.dumps(formats)
        response.headers['Meta-Field-Pkey'] = json.dumps(DATABASE_PKEYS[database])
        return response

def post_table(database, period, source, tablename, request):
    tablesubfolder = request.args.get('tablesubfolder')  # Optional
    names = request.args.get('names')  # Optional
    if names:
        names = json.loads(names)        
    formats = request.args.get('formats')  # Optional
    if formats:
        formats = json.loads(formats)
    size = request.args.get('size')  # Optional
    if size:
        size = int(size)
    overwrite = request.args.get('overwrite', False)  # Optional
    user = request.args.get('user', 'master')  # Optional
    value = None
    if request.data:
        content_encoding = request.headers.get('Content-Encoding', "")
        if content_encoding == 'lz4':
            meta_names = json.loads(request.headers['Meta-Field-Names'])
            meta_formats = json.loads(request.headers['Meta-Field-Formats'])
            dtype = np.dtype(list(zip(meta_names, meta_formats)))                    
            data = lz4f.decompress(request.data)        
            value = np.frombuffer(data, dtype=dtype).copy()
        else:
            value = pd.DataFrame(json.loads(request.data))  # Optional
            pkey_columns = DATABASE_PKEYS[database]
            if 'date' in pkey_columns:
                value['date'] = pd.to_datetime(value['date'])
            if all(col in value.columns for col in pkey_columns):
                value.set_index(pkey_columns, inplace=True)
            else:
                raise Exception(f'Primary key columns {pkey_columns} not found in value')
                        
    if tablesubfolder is not None:
        tablename = tablename+'/'+tablesubfolder
            
    tbl = shdata.table(database, period, source, tablename,
                       names=names, formats=formats, size=size,
                       overwrite=overwrite, user=user, value=value)
    if value is not None:
        tbl.upsert(value)
            
    response = Response(status=201)
    response.headers['Content-Length'] = 0
    return response

@app.route('/api/collection/<database>/<period>/<source>/<tablename>', methods=['GET', 'POST', 'PATCH'])
@swag_from(docspath)
def collection(database, period, source, tablename):
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
        
        if request.method == 'POST':
            return post_collection(database, period, source, tablename, request)
        elif request.method == 'GET':
            return get_collection(database, period, source, tablename, request)
        elif request.method == 'PATCH':
            return patch_collection(database, period, source, tablename, request)
        
    except Exception as e:
        time.sleep(1)  # Sleep for 1 second before returning the error        
        sanitized_error = str(e).replace("\n", " ").replace("\r", " ")  # Remove new lines
        error_message = json.dumps({"type": "InternalServerError", "message": sanitized_error})
        response = Response(error_message, status=500, mimetype='application/json')
        response.headers['X-Error-Reason'] = sanitized_error  # Set the sanitized error message
        return response
    
def get_collection(database, period, source, tablename, request):
    # Get the collection    
    user = request.args.get('user', 'master')  # Optional
    tablesubfolder = request.args.get('tablesubfolder')  # Optional
    query = request.args.get('query')
    if query:
        query = json_util.loads(query)  # Optional
    else:
        query = {}        
    sort = request.args.get('sort')  # Optional        
    if sort:
        sort = json_util.loads(sort)
    else:
        sort = {}
    columns = request.args.get('columns')  # Optional
    projection = None
    if columns:
        columns = json_util.loads(columns)
        projection = {f.strip(): 1 for f in columns.split(',')}
        for pkey in DATABASE_PKEYS[database]:
            projection[pkey] = 1

    page = request.args.get('page', default='1')
    page = int(float(page))
    per_page = request.args.get('per_page', default='10000')
    per_page = int(float(per_page))
    output_format = request.args.get('format', 'bson').lower()  # 'json' by default, can be 'csv'
    accept_encoding = request.headers.get('Accept-Encoding', '')
    
    if tablesubfolder is not None:
        tablename = tablename+'/'+tablesubfolder
    collection = shdata.collection(database, period, source, tablename, user=user)

    for key in query:
        if key == '_id':
            query[key] = ObjectId(query[key])
        elif key == 'date':
            if isinstance(query[key], dict):
                for subkey in query[key]:
                    try:
                        query[key][subkey] = pd.Timestamp(query[key][subkey])
                    except:
                        pass
            else:
                try:
                    query[key] = pd.Timestamp(query[key])
                except:
                    pass

    result = collection.find(query, sort=sort, limit=per_page, skip=(page-1)*per_page, projection=projection)
    if len(result) == 0:
        response = Response(status=204)
        response.headers['Content-Length'] = 0
        return response
    
    if output_format == 'bson':
        bson_data = bson.encode({'data': list(result)})
        compressed_data = lz4f.compress(bson_data)

        response = Response(compressed_data, mimetype='application/octet-stream')
        response.headers['Content-Encoding'] = 'lz4'
        response.headers['Content-Length'] = len(compressed_data)
        response.headers['Content-Type'] = 'application/octet-stream'
        return response

    elif output_format == 'csv':
        # Return CSV
        df = collection.documents2df(result)
        csv_data = df.to_csv()
        if 'gzip' in accept_encoding:
            response_csv = csv_data.encode('utf-8')
            response_compressed = gzip.compress(response_csv, compresslevel=1)
            response = Response(response_compressed, mimetype='text/csv')
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response_compressed)
            return response
        else:
            response_data = csv_data.encode('utf-8')
            response = Response(response_data, mimetype='text/csv')
            response.headers['Content-Length'] = len(response_data)
            return response
    else:
        pkey = ''
        if database in DATABASE_PKEYS:
            pkey = DATABASE_PKEYS[database]
        # Return JSON
        response_data = {
            'page': page,
            'per_page': per_page,
            'total': len(result),
            'pkey': pkey,
            'data': collection.documents2json(result)
        }

        if 'gzip' in accept_encoding:
            response_json = json.dumps(response_data).encode('utf-8')
            response_compressed = gzip.compress(response_json, compresslevel=1)
            response = Response(response_compressed, mimetype='application/json')
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response_compressed)
            return response
        else:
            response_json = json.dumps(response_data).encode('utf-8')
            response = Response(response_json, mimetype='application/json')
            response.headers['Content-Length'] = len(response_json)
            return response

def post_collection(database, period, source, tablename, request):    
    # 1. Parse query parameters
    tablesubfolder = request.args.get('tablesubfolder')  # Optional
    user = request.args.get('user', 'master')            # Default to 'master'

    if tablesubfolder:
        tablename = f"{tablename}/{tablesubfolder}"

    # 2. Acquire collection object
    collection = shdata.collection(database, period, source, tablename, user=user)

    # 3. Ensure data is present
    if not request.data:
        Response({'message':'No data'}, status=400)
    
    # 4. Handle input data (lz4+BSON or JSON)
    # Check for binary, compressed upload
    if request.headers.get('Content-Encoding', '').lower() == 'lz4':
        decompressed = lz4f.decompress(request.data)
        documents = bson.decode(decompressed)['data']
    else:
        # fallback: assume JSON
        documents = json.loads(request.data)

    if not isinstance(documents, list):
        Response({'message':'Data must be a list'}, status=400)
    
    # 5. Insert/Upsert
    # (Assume upsert method supports list input)
    collection.upsert(documents)

    # 6. Prepare and return response
    response_data = json.dumps({'status': 'success'}).encode('utf-8')
    response = Response(response_data, status=201, mimetype='application/json')
    response.headers['Content-Length'] = str(len(response_data))
    return response   

def patch_collection(database, period, source, tablename, request):
    # Get the collection    
    pkey = ''
    if database in DATABASE_PKEYS:
        pkey = DATABASE_PKEYS[database]
    else:
        error_data = json.dumps({'error': 'database not found'}).encode('utf-8')
        response = Response(error_data, status=400, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response
    
    user = request.args.get('user', 'master')  # Optional    
    tablesubfolder = request.args.get('tablesubfolder', None)  # Optional
    if tablesubfolder is not None:
        tablename = tablename+'/'+tablesubfolder
    collection = shdata.collection(database, period, source, tablename, user=user)
    
    filter = request.args.get('filter')
    if filter is None:
        error_data = json.dumps({'error': 'filter is required'}).encode('utf-8')
        response = Response(error_data, status=400, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response    
    filter = json.loads(filter)
    for key in filter:
        if key == '_id':
            filter[key] = ObjectId(filter[key])
        elif key == 'date':
            if isinstance(filter[key], dict):
                for subkey in filter[key]:
                    try:
                        filter[key][subkey] = pd.Timestamp(filter[key][subkey])
                    except:
                        pass
            else:
                try:
                    filter[key] = pd.Timestamp(filter[key])
                except:
                    pass

    update = request.args.get('update')
    if update is None:
        error_data = json.dumps({'error': 'update is required'}).encode('utf-8')
        response = Response(error_data, status=400, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response
    update = json.loads(update)

    sort = request.args.get('sort')    
    if sort:
        sort = json.loads(sort)
    else:
        sort = {}
    
    coll = collection.collection
    res = coll.find_one_and_update(
        filter=filter, 
        update=update, 
        sort=sort, 
        return_document=pymongo.ReturnDocument.AFTER)
    
    if res:
        if '_id' in res:
            res['_id'] = str(res['_id'])
        
        for key in res:
            if pd.api.types.is_datetime64_any_dtype(res[key]) or isinstance(res[key], datetime.datetime):
                res[key] = res[key].isoformat()
        # Return JSON
        response_data = {
            'pkey': pkey,
            'data': json.dumps(res),
        }
        response_json = json.dumps(response_data).encode('utf-8')
        response = Response(response_json, mimetype='application/json')
        response.headers['Content-Length'] = len(response_json)
        return response
    else:
        response = Response('', status=204)
        response.headers['Content-Length'] = 0
        return response
       
@app.route('/api/rss', methods=['GET'])
def news():
    try:
        
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401
        
        # Get query parameters
        filter = {}

        startdate = request.args.get('startdate')
        if startdate is not None:
            filter['time_published'] = {'$gte': startdate}

        news_text = request.args.get('news_text')
        if news_text is not None and news_text != '':
            filter["title"] = {"$regex": str(news_text), "$options": "i"}

        collection = shdata.mongodb['rss_feeds']

        docs = collection.find(filter).sort({'time_published': -1}).limit(20)
        docs = list(docs)

        response_json = CollectionMongoDB.documents2json(CollectionMongoDB, docs)
        response_data = response_json.encode('utf-8')
        response = Response(response_data, mimetype='application/json')
        response.headers['Content-Length'] = len(response_data)
        return response

    except Exception as e:
        error_data = json.dumps({'error': str(e)}).encode('utf-8')
        response = Response(error_data, status=500, mimetype='application/json')
        response.headers['Content-Length'] = len(error_data)
        return response

log_queue = Queue()

@app.route('/api/logs', methods=['POST'])
def logs():
    try:
        if not authenticate(request):
            return jsonify({'error': 'unauthorized'}), 401

        data = lz4f.decompress(request.data)
        rec = json.loads(data.decode('utf-8'))
        log_queue.put(rec)
        
        return Response(status=201)

    except Exception as e:
        time.sleep(1)  # Sleep for 1 second before returning the error        
        sanitized_error = str(e).replace("\n", " ").replace("\r", " ")  # Remove new lines
        error_message = json.dumps({"type": "InternalServerError", "message": sanitized_error})
        response = Response(error_message, status=500, mimetype='application/json')
        response.headers['X-Error-Reason'] = sanitized_error  # Set the sanitized error message
        return response

def log_writer():
    _log_sequence = 0

    mongodb = MongoDBClient()
    db = mongodb.client['SharedData']
    if 'logs' not in db.list_collection_names():
        # Create logs collection as timeseries collection
        db.create_collection("logs", 
            timeseries={
            'timeField': "asctime",
            'metaField': "metadata",
            'granularity': "seconds"
            },
            expireAfterSeconds=604800    # <-- 7 days in seconds
        )
        

    while True:
        rec = log_queue.get()
        
        _log_sequence += 1        
        _log_sequence_str = str(int(_log_sequence)).zfill(12)

        line = '%s;%s;%s;%s;%s;%s;%s' % (os.environ['USER_COMPUTER'],_log_sequence_str,
                rec['user_name'], rec['asctime'],
                rec['logger_name'], rec['level'], str(rec['message']).replace(';', ',')
            )
        dt = datetime.datetime.strptime(
            rec['asctime'][:-5], '%Y-%m-%dT%H:%M:%S')

        logfilepath = Path(os.environ['DATABASE_FOLDER']) / 'Logs'
        logfilepath = logfilepath / (dt.strftime('%Y%m%d')+'.log')
        if not logfilepath.parents[0].is_dir():
            os.makedirs(logfilepath.parents[0])
                        
        lock_path = str(logfilepath) + ".lock"
        with FileLock(lock_path):  # This acquires an OS-level lock
            with open(logfilepath, 'a+', encoding='utf-8') as f:
                f.write(line.replace('\n', ' ').replace('\r', ' ')+'\n')
                f.flush()
        
        # Parse asctime string to datetime with timezone info
        asctime_str = rec['asctime']
        asctime = datetime.datetime.strptime(asctime_str, '%Y-%m-%dT%H:%M:%S%z')
        # Insert into MongoDB
        document = {
            "asctime": asctime,
            "metadata": {
                "user_name": rec['user_name'].replace('\\','/'),
                "logger_name": rec['logger_name'].replace('\\','/'),
                "level": rec['level']
            },
            "message": rec['message'],
            "shard_id": os.environ['USER_COMPUTER'],
            "sequence_number": _log_sequence_str
        }        
        try:
            db.logs.insert_one(document)
        except Exception as e:
            print(f"An error occurred inserting  a log to mongodb: {e}")

from SharedData.Routines.WorkerPool import WorkerPool
worker_pool = WorkerPool()

@app.route('/api/workerpool', methods=['GET','POST','PATCH'])
def workerpool():
    try:        
        if request.method == 'POST':
            return post_workerpool(request)
        elif request.method == 'GET':
            return get_workerpool(request)
        elif request.method == 'PATCH':
            return patch_workerpool(request)

    except Exception as e:
        time.sleep(1)  # Sleep for 1 second before returning the error        
        sanitized_error = str(e).replace("\n", " ").replace("\r", " ")  # Remove new lines
        error_message = json.dumps({"type": "InternalServerError", "message": sanitized_error})
        response = Response(error_message, status=500, mimetype='application/json')
        response.headers['X-Error-Reason'] = sanitized_error  # Set the sanitized error message
        return response

def get_workerpool(request):
    if not authenticate(request):
        return jsonify({'error': 'unauthorized'}), 401
    jobs = worker_pool.get_jobs(request.args.get('workername'))
    if len(jobs)==0:
        return Response(status=204)
    else:
        bson_data = bson.encode({'jobs':jobs})
        compressed = lz4f.compress(bson_data)
        return Response(
            compressed, 
            mimetype='application/octet-stream', 
            headers={'Content-Encoding': 'lz4'}
        )        

def post_workerpool(request):
    if not authenticate(request):
        return jsonify({'error': 'unauthorized'}), 401
    
    bson_data = lz4f.decompress(request.data)
    record = bson.decode(bson_data)
    if worker_pool.new_job(record):        
        return Response(status=201)

def patch_workerpool(request):
    if not authenticate(request):
        return jsonify({'error': 'unauthorized'}), 401
        
    return Response(status=400)


if __name__ == '__main__':
    from waitress import serve
    import logging
    # Suppress Waitress logs
    waitress_logger = logging.getLogger('waitress')
    waitress_logger.setLevel(logging.CRITICAL)
    waitress_logger.addHandler(logging.NullHandler())

    import threading
    import sys
    import time  
    import argparse

    from SharedData.SharedData import SharedData
    shdata = SharedData('SharedData.IO.ServerAPI', user='master',quiet=True)
    from SharedData.Logger import Logger
    from SharedData.Database import *    
        
    parser = argparse.ArgumentParser(description="Server configuration")
    parser.add_argument('--host', default='0.0.0.0', help='Server host address')
    parser.add_argument('--port', type=int, default=8088, help='Server port number')
    parser.add_argument('--nthreads', type=int, default=8, help='Number of server threads')

    args = parser.parse_args()
    host = args.host
    port = args.port
    nthreads = args.nthreads

    heartbeat_running = True  # Flag to control the heartbeat thread

    def send_heartbeat():
        global heartbeat_running, traffic_rates
        heartbeat_interval = 15
        time.sleep(15)
        Logger.log.info('ROUTINE STARTED!')
        while heartbeat_running:
            current_time = time.time()
            with stats_lock:
                current_total_requests = traffic_stats['total_requests']
                current_total_bytes_sent = sum(ep['total_bytes_sent'] for ep in traffic_stats['endpoints'].values())
                current_total_bytes_received = sum(ep['total_bytes_received'] for ep in traffic_stats['endpoints'].values())
                
                # Calculate time elapsed since last heartbeat
                time_elapsed = current_time - traffic_rates['last_timestamp']
                if time_elapsed > 0:
                    # Calculate rates
                    requests_delta = current_total_requests - traffic_rates['last_total_requests']
                    bytes_sent_delta = current_total_bytes_sent - traffic_rates['last_total_bytes_sent']
                    bytes_received_delta = current_total_bytes_received - traffic_rates['last_total_bytes_received']
                    requests_per_sec = requests_delta / time_elapsed
                    bytes_sent_per_sec = bytes_sent_delta / time_elapsed
                    bytes_received_per_sec = bytes_received_delta / time_elapsed
                else:
                    requests_per_sec = 0.0
                    bytes_sent_per_sec = 0.0
                    bytes_received_per_sec = 0.0
                
                # Update the last values for the next iteration
                traffic_rates['last_total_requests'] = current_total_requests
                traffic_rates['last_total_bytes_sent'] = current_total_bytes_sent
                traffic_rates['last_total_bytes_received'] = current_total_bytes_received
                traffic_rates['last_timestamp'] = current_time

            # Log the heartbeat with rates
            Logger.log.debug('#heartbeat#host:%s,port:%i,reqs:%i,reqps:%.2f,download:%.2fMB/s,upload:%.2fMB/s' % 
                            (host, port, current_total_requests, requests_per_sec, 
                             bytes_received_per_sec/(1024**2), bytes_sent_per_sec/(1024**2)))
            time.sleep(heartbeat_interval)

    t = threading.Thread(target=send_heartbeat, args=(), daemon=True)
    t.start()    

    log_thread = threading.Thread(target=log_writer, daemon=True)
    log_thread.start()

    try:
        serve(
            app, 
            host=host, 
            port=port,  
            threads=nthreads,
            expose_tracebacks=False,
            asyncore_use_poll=True,
            _quiet=True,
            ident='SharedData'
        )
    except Exception as e:
        Logger.log.error(f"Waitress server encountered an error: {e}")
        heartbeat_running = False  # Stop the heartbeat thread
        t.join()  # Wait for the heartbeat thread to finish
        sys.exit(1)  # Exit the program with an error code
    finally:
        # This block will always execute, even if an exception occurs.
        # Useful for cleanup if needed.
        Logger.log.info("Server shutting down...")
        heartbeat_running = False  # Ensure heartbeat stops on normal shutdown
        t.join()  # Wait for heartbeat thread to finish
        Logger.log.info("Server shutdown complete.")