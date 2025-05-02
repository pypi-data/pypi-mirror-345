# implements a decentralized routines worker
# connects to worker pool
# broadcast heartbeat
# listen to commands
# environment variables:
# SOURCE_FOLDER
# WORKERPOOL_STREAM
# GIT_SERVER
# GIT_USER
# GIT_ACRONYM
# GIT_TOKEN

import os
import time
import sys
import numpy as np
import importlib.metadata
import argparse


from SharedData.Routines.WorkerLib import *
from SharedData.IO.AWSKinesis import *
from SharedData.SharedData import SharedData
shdata = SharedData('SharedData.Routines.Worker', user='worker')
from SharedData.Logger import Logger
from SharedData.Routines.WorkerPool import WorkerPool

parser = argparse.ArgumentParser(description="Worker configuration")
parser.add_argument('--schedules', default='', help='Schedules to start')
parser.add_argument('--server', type=bool, default=False, help='Server port number')
parser.add_argument('--port', type=int, default=8088, help='Server port number')
parser.add_argument('--nthreads', type=int, default=8, help='Number of server threads')
args = parser.parse_args()

if args.server:
    start_server(args.port, args.nthreads)    
    start_logger()
    
SCHEDULE_NAMES = args.schedules
if SCHEDULE_NAMES != '':
    Logger.log.info('SharedData Worker schedules:%s STARTED!' % (SCHEDULE_NAMES))
    start_schedules(SCHEDULE_NAMES)    


# consumer = KinesisStreamConsumer(os.environ['WORKERPOOL_STREAM'])
consumer = WorkerPool()
lastheartbeat = time.time()

SLEEP_TIME = int(os.environ['SLEEP_TIME'])
try:
    SHAREDDATA_VERSION = importlib.metadata.version("shareddata")
    Logger.log.info('SharedData Worker version %s STARTED!' % (SHAREDDATA_VERSION))
except:
    Logger.log.info('SharedData Worker STARTED!')
Logger.log.info('ROUTINE STARTED!')

routines = []
while True:    

    if not consumer.consume():
        # consumer.get_stream()
        Logger.log.error('Cannot consume workerpool messages!')
        time.sleep(5)
    
    update_routines(routines)
    for command in consumer.stream_buffer:
        print('\nReceived:'+str(command)+'\n')
                
        if ('job' in command) & ('target' in command):
            if ((command['target'].upper() == os.environ['USER_COMPUTER'].upper())
                    | (command['target'] == 'ALL')):                                
                process_command(command,routines)                

    routines = remove_finished_routines(routines)

    consumer.stream_buffer = []

    if (time.time()-lastheartbeat > 15):
        lastheartbeat = time.time()
        Logger.log.debug('#heartbeat#')
    
    time.sleep(SLEEP_TIME * np.random.rand())