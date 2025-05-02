import os
import logging
from datetime import datetime, timezone
import requests
import json
import pandas as pd
import lz4

class LogHandlerAPI(logging.Handler):
    def __init__(self):
        super().__init__()
        if not 'SHAREDDATA_ENDPOINT' in os.environ:
            raise Exception('SHAREDDATA_ENDPOINT not in environment variables')
        self.endpoint = os.environ['SHAREDDATA_ENDPOINT']+'/api/logs'

        if not 'SHAREDDATA_TOKEN' in os.environ:
            raise Exception('SHAREDDATA_TOKEN not in environment variables')
        self.token = os.environ['SHAREDDATA_TOKEN']        

    def emit(self, record):
        try:
            self.acquire()
            user = os.environ['USER_COMPUTER']    
            dt = datetime.fromtimestamp(record.created, timezone.utc)
            asctime = dt.strftime('%Y-%m-%dT%H:%M:%S%z')
            msg = {
                'user_name': user,
                'asctime': asctime,
                'logger_name': record.name,
                'level': record.levelname,
                'message': str(record.msg).replace('\'', '\"'),
            }                                    
            body = json.dumps(msg)
            compressed = lz4.frame.compress(body.encode('utf-8'))
            headers = {
                'Content-Type': 'application/json',
                'Content-Encoding': 'lz4',
                'X-Custom-Authorization': self.token,
            }
            response = requests.post(
                self.endpoint,
                headers=headers,
                data=compressed,
                timeout=15
            )
            response.raise_for_status()

        except Exception as e:
            # self.handleError(record)
            print(f"Could not send log to server:{record}\n {e}")
        finally:            
            self.release()