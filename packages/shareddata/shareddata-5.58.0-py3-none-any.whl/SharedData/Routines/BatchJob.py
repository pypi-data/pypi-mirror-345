# SharedData/Routines/BatchJob.py
import argparse
import base64
import bson

from SharedData.SharedData import SharedData

class BatchJob:
    def __init__(self, user='master'):
        _args = self.parse_args()        
        self.hash = _args.hash
        self.args = {}
        if _args.bson:
            self.args = self.decode_bson(_args.bson)                    
        self.shdata = SharedData(f'@{self.hash}', user=user, quiet=True)
    
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description="routine configuration")
        parser.add_argument('--hash', required=True, help='routine hash')
        parser.add_argument('--bson', default=None, help='routine args')
        return parser.parse_args()

    @staticmethod
    def decode_bson(b64_arg):
        if not b64_arg:
            return {}
        bson_data = base64.b64decode(b64_arg)
        return bson.BSON(bson_data).decode()

# Example usage:    
# from SharedData.Logger import Logger
# from SharedData.Routines.BatchJob import BatchJob
# job = BatchJob()
# shdata = job.shdata
# Logger.log.info(f'hash: {job.hash}')
# Logger.log.info(f'args: {job.args}')


