import lz4.frame
import pandas as pd
import os
import threading
import json
import requests
import lz4
import bson
import hashlib
import pymongo
import time

from SharedData.IO.MongoDBClient import MongoDBClient
from SharedData.IO.AWSKinesis import KinesisStreamProducer
from SharedData.Logger import Logger


class WorkerPool:

    def __init__(self, kinesis=False):
        self.kinesis = kinesis
        self.jobs = {}
        self.lock = threading.Lock()
        self.stream_buffer = []

        if kinesis:
            self.producer = KinesisStreamProducer(os.environ['WORKERPOOL_STREAM'])
        else:
            if not 'SHAREDDATA_ENDPOINT' in os.environ:
                raise Exception('SHAREDDATA_ENDPOINT not in environment variables')            

            if not 'SHAREDDATA_TOKEN' in os.environ:
                raise Exception('SHAREDDATA_TOKEN not in environment variables')            

            self.producer = self

    def acquire(self):
        self.lock.acquire()
    
    def release(self):
        self.lock.release()

    def produce(self, record, partitionkey=None):
        if not 'sender' in record:
            raise Exception('sender not in record')
        if not 'target' in record:
            raise Exception('target not in record')
        if not 'job' in record:
            raise Exception('job not in record')
        try:            
            self.acquire()
            bson_data = bson.encode(record)
            compressed = lz4.frame.compress(bson_data)
            headers = {
                'Content-Type': 'application/octet-stream',
                'Content-Encoding': 'lz4',
                'X-Custom-Authorization': os.environ['SHAREDDATA_TOKEN'],
            }
            response = requests.post(
                os.environ['SHAREDDATA_ENDPOINT']+'/api/workerpool',
                headers=headers,
                data=compressed,
                timeout=15
            )
            response.raise_for_status()
        except Exception as e:
            # self.handleError(record)
            print(f"Could not send command to server:{record}\n {e}")
        finally:            
            self.release()

    def new_job(self, record):
        if not 'sender' in record:
            raise Exception('sender not in record')
        if not 'target' in record:
            raise Exception('target not in record')
        if not 'job' in record:
            raise Exception('job not in record')
        
        targetkey = str(record['target']).upper()
        if not targetkey in self.jobs.keys():
            self.jobs[targetkey] = []

        if not 'date' in record:
            record['date'] = pd.Timestamp.utcnow().tz_localize(None)
        try:
            self.acquire()
            self.jobs[targetkey].append(record)
        except Exception as e:
            Logger.log.error(f"Could not add job to workerpool:{record}\n {e}")
        finally:
            self.release()
        
        return True
    
    def consume(self, fetch_jobs=0):
        success = False
        try:
            self.acquire()
            workername = os.environ['USER_COMPUTER']
            headers = {                
                'Accept-Encoding': 'lz4',                
                'X-Custom-Authorization': os.environ['SHAREDDATA_TOKEN'],
            }
            params = {
                'workername': workername,                
            }
            if fetch_jobs > 0:
                params['fetch_jobs'] = fetch_jobs
            response = requests.get(
                os.environ['SHAREDDATA_ENDPOINT']+'/api/workerpool',
                headers=headers,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            success = True
            if response.status_code == 204:
                return success
            response_data = lz4.frame.decompress(response.content)
            record = bson.decode(response_data)            
            self.stream_buffer.extend(record['jobs'])            
        except Exception as e:
            Logger.log.error(f"Could not consume workerpool:{e}")            
        finally:
            self.release()
        return success
    
    def get_jobs(self, workername):
        try:
            self.acquire()
            tnow = pd.Timestamp.utcnow().tz_localize(None)
            _jobs = []
            workername = str(workername).upper()
            if workername in self.jobs.keys():
                # Clean up broadcast jobs older than 60 seconds
                self.jobs[workername] = [
                    job for job in self.jobs[workername]
                    if 'date' in job and tnow - pd.Timestamp(job['date']) < pd.Timedelta(seconds=60)
                ]
                for job in self.jobs[workername]:                    
                    _jobs.append(job)
                
                # Clear the jobs for this worker
                self.jobs[workername] = []
                        
            
            if 'ALL' in self.jobs.keys():
                # Clean up broadcast jobs older than 60 seconds
                self.jobs['ALL'] = [
                    job for job in self.jobs['ALL']
                    if 'date' in job and tnow - pd.Timestamp(job['date']) < pd.Timedelta(seconds=60)
                ]
                for job in self.jobs['ALL']:                    
                    if not 'workers' in job.keys():
                        job['workers'] = {}
                    if not workername in job['workers'].keys():
                        job['workers'][workername] = pd.Timestamp.utcnow().tz_localize(None)
                        _jobs.append(job)                
        except Exception as e:
            Logger.log.error(f"Could not get jobs from workerpool:{e}")
        finally:
            self.release()
        return _jobs
                
    @staticmethod
    def update_jobs_status() -> None:
        """
        Periodically updates job statuses from NEW/WAITING to PENDING if the due date has passed
        and all dependencies are completed.
        """
        while True:
            try:
                now = pd.Timestamp('now', tz='UTC')
                pipeline = [
                    {
                        '$match': {
                            'status': {'$in': ['NEW', 'WAITING']},
                            'date': {'$lt': now}
                        }
                    },
                    {
                        '$lookup': {
                            'from': 'Text/RT/WORKERPOOL/collection/JOBS',
                            'localField': 'dependencies',
                            'foreignField': 'hash',
                            'as': 'deps'
                        }
                    },
                    {
                        '$addFields': {
                            'all_deps_completed': {
                                '$cond': [
                                    {'$gt': [{'$size': {'$ifNull': ['$dependencies', []]}}, 0]},
                                    {
                                        '$allElementsTrue': {
                                            '$map': {
                                                'input': "$deps",
                                                'as': "d",
                                                'in': {'$eq': ["$$d.status", "COMPLETED"]}
                                            }
                                        }
                                    },
                                    True
                                ]
                            }
                        }
                    },
                    {
                        '$match': {'all_deps_completed': True}
                    },
                    {
                        "$project": {"date": 1, "hash": 1}
                    }
                ]
                pipeline.append({
                    "$merge": {
                        "into": "Text/RT/WORKERPOOL/collection/JOBS",
                        "whenMatched": [
                            {"$set": {"status": "PENDING", "mtime": now}}
                        ],
                        "whenNotMatched": "discard"
                    }
                })

                mongodb = MongoDBClient(user='master')
                coll = mongodb['Text/RT/WORKERPOOL/collection/JOBS']
                coll.aggregate(pipeline)

                time.sleep(5)
            except Exception as e:
                Logger.log.error(f"Error in update_jobs_status: {e}")
                time.sleep(60)  # Wait before retrying in case of error
        
    @staticmethod
    def fetch_job(workername, njobs=1):
        user = workername.split('@')[0]
        computer = workername.split('@')[1]
        mongodb= MongoDBClient(user='master')
        coll = mongodb['Text/RT/WORKERPOOL/collection/JOBS']

        filter_query = {
            'user': user,
            'computer': {'$in': [computer, 'ANY']},
            'status': 'PENDING'  # Only fetch jobs that are in 'WAITING' status
        }

        # Define the update operation to set status to 'FETCHED'
        update_query = {
            '$set': {
                'status': 'FETCHED',
                'target': user+'@'+computer,
                'mtime': pd.Timestamp('now', tz='UTC')
            }
        }

        sort_order = [('date', pymongo.DESCENDING)]

        fetched_jobs = []
        for _ in range(njobs):
            # Atomically find and update a single job
            job = coll.find_one_and_update(
                filter=filter_query,
                update=update_query,
                sort=sort_order,
                return_document=pymongo.ReturnDocument.AFTER
            )

            if job:
                fetched_jobs.append(job)
            else:
                # No more jobs available
                break
        
        return fetched_jobs