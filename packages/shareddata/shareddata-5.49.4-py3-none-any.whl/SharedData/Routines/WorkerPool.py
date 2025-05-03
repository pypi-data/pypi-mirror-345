import lz4.frame
import pandas as pd
import os
import threading
import json
import requests
import lz4
import bson

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
    
    def consume(self):
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
        
    def patch_job(self, workername):
        pass