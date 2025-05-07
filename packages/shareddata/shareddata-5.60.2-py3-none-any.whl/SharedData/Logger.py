import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
import glob
import pandas as pd
import numpy as np
from io import StringIO

from pythonjsonlogger.jsonlogger import JsonFormatter
import boto3
import json
import requests
import lz4

from SharedData.IO.AWSKinesis import KinesisLogHandler
from SharedData.IO.LogHandlerAPI import LogHandlerAPI

        
class Logger:

    log = None
    user = 'guest'
    source = 'unknown'
    last_day_read = False

    dflogs = pd.DataFrame(
        [],
        columns=['shardid', 'sequence_number', 'user_name',
                  'asctime', 'logger_name', 'level', 'message']
    )
    dfstarted = pd.DataFrame([])
    dfheartbeats = pd.DataFrame([])
    dfcompleted = pd.DataFrame([])
    dferror = pd.DataFrame([])    
    dflast = pd.DataFrame([])
    dfrun = pd.DataFrame([])

    logfilepath = Path('')
    _logfileposition=0
    _sorted_until = 0
    _max_asctime =  pd.Timestamp('1970-01-01 00:00:00',tz='UTC')

    @staticmethod
    def connect(source, user=None):
        if Logger.log is None:
            if 'SOURCE_FOLDER' in os.environ:
                try:
                    commonpath = os.path.commonpath(
                        [source, os.environ['SOURCE_FOLDER']])
                    source = source.replace(commonpath, '')
                except:
                    pass
            elif 'USERPROFILE' in os.environ:
                try:
                    commonpath = os.path.commonpath(
                        [source, os.environ['USERPROFILE']])
                    source = source.replace(commonpath, '')
                except:
                    pass

            finds = 'site-packages'
            if finds in source:
                cutid = source.find(finds) + len(finds) + 1
                source = source[cutid:]                        
            source = source.replace('\\','/')
            source = source.lstrip('/')
            source = source.replace('.py', '')
            Logger.source = source

            if not user is None:
                Logger.user = user
            
            loglevel = logging.INFO
            if 'LOG_LEVEL' in os.environ:
                if os.environ['LOG_LEVEL'] == 'DEBUG':
                    loglevel = logging.DEBUG                
                
            # Create Logger
            Logger.log = logging.getLogger(source)
            Logger.log.setLevel(logging.DEBUG)
            # formatter = logging.Formatter(os.environ['USER_COMPUTER'] +
            #                               ';%(asctime)s;%(name)s;%(levelname)s;%(message)s',
            #                               datefmt='%Y-%m-%dT%H:%M:%S%z')
            formatter = logging.Formatter(os.environ['USER_COMPUTER'] +
                                          ';%(asctime)s;%(name)s;%(levelname)s;%(message)s',
                                          datefmt='%H:%M:%S')
            # log screen
            handler = logging.StreamHandler()
            handler.setLevel(loglevel)
            handler.setFormatter(formatter)
            Logger.log.addHandler(handler)

            # log to API
            if str(os.environ['LOG_API']).upper()=='TRUE':
                apihandler = LogHandlerAPI()
                apihandler.setLevel(logging.DEBUG)
                jsonformatter = JsonFormatter(os.environ['USER_COMPUTER']+
                                            ';%(asctime)s;%(name)s;%(levelname)s;%(message)s',
                                            datefmt='%Y-%m-%dT%H:%M:%S%z')
                apihandler.setFormatter(jsonformatter)
                Logger.log.addHandler(apihandler)

            # log to file
            if str(os.environ['LOG_FILE']).upper()=='TRUE':
                path = Path(os.environ['DATABASE_FOLDER'])
                path = path / 'Logs'
                path = path / datetime.now().strftime('%Y%m%d')
                path = path / (os.environ['USERNAME'] +
                            '@'+os.environ['COMPUTERNAME'])
                path = path / (source+'.log')
                path.mkdir(parents=True, exist_ok=True)
                fhandler = logging.FileHandler(str(path), mode='a')
                fhandler.setLevel(loglevel)
                fhandler.setFormatter(formatter)
                Logger.log.addHandler(fhandler)
            
            # log to aws kinesis
            if str(os.environ['LOG_KINESIS']).upper()=='TRUE':
                kinesishandler = KinesisLogHandler(user=Logger.user)
                kinesishandler.setLevel(logging.DEBUG)
                jsonformatter = JsonFormatter(os.environ['USER_COMPUTER']+
                                            ';%(asctime)s;%(name)s;%(levelname)s;%(message)s',
                                            datefmt='%Y-%m-%dT%H:%M:%S%z')
                kinesishandler.setFormatter(jsonformatter)
                Logger.log.addHandler(kinesishandler)

    @staticmethod
    def read_last_day_logs():
        Logger.last_day_read = True
        lastlogfilepath = Path(os.environ['DATABASE_FOLDER']) / 'Logs'
        lastlogfilepath = lastlogfilepath / \
            ((pd.Timestamp.utcnow() + timedelta(days=-1)).strftime('%Y%m%d')+'.log')        
        if lastlogfilepath.is_file():
            try:
                _dflogs = pd.read_csv(lastlogfilepath, header=None, sep=';',
                                      engine='python', on_bad_lines='skip')
                _dflogs.columns = ['shardid', 'sequence_number',
                                   'user_name', 'asctime', 'logger_name', 'level', 'message']
                Logger.dflogs = pd.concat([_dflogs, Logger.dflogs], axis=0, ignore_index=True)
                Logger.getLastLog(Logger.dflogs)
                Logger.getStatus(Logger.dflogs)                
            except Exception as e:
                print(f'Error reading last day logs: {e}')

    @staticmethod
    def getLogs(keep_latest_heartbeat=300):
        dfnewlines_sorted = Logger.readLogs()
        if dfnewlines_sorted is None or len(dfnewlines_sorted) == 0:
            return Logger.dflogs
        
        Logger.getLastLog(dfnewlines_sorted)
        Logger.getStatus(dfnewlines_sorted)
        Logger.handleHeartbeats(keep_latest_heartbeat)
        return Logger.dflogs
    
    @staticmethod
    def readLogs():
        dfnewlines = pd.DataFrame(
            [], columns=['shardid', 'sequence_number', 'user_name', 
                         'asctime', 'logger_name', 'level', 'message']
            )
        if not Logger.last_day_read:
            Logger.read_last_day_logs()

        _logfilepath = Path(os.environ['DATABASE_FOLDER']) / 'Logs'
        _logfilepath = _logfilepath / \
            (pd.Timestamp.utcnow().strftime('%Y%m%d')+'.log')
        if Logger.logfilepath != _logfilepath:
            Logger._logfileposition = 0
            Logger.logfilepath = _logfilepath

        if Logger.logfilepath.is_file():
            
            with open(Logger.logfilepath, 'r') as file:
                file.seek(Logger._logfileposition)
                newlines = '\n'.join(file.readlines())
                if not newlines.strip():   # fix: prevent pd.read_csv crash on empty string
                    return dfnewlines
                dfnewlines = pd.read_csv(StringIO(newlines), header=None, sep=';',
                                            engine='python', on_bad_lines='skip')
                if dfnewlines.shape[1] > 7:
                    # Merge all columns from 6 onward into a single message
                    message = dfnewlines.iloc[:, 6:].apply(lambda x: ';'.join(x.dropna().astype(str)), axis=1)
                    dfnewlines = dfnewlines.iloc[:, :7]
                    dfnewlines.iloc[:, 6] = message 
                
                dfnewlines.columns = [
                    'shardid', 'sequence_number', 'user_name', 'asctime', 'logger_name', 'level', 'message'
                ]
                dfnewlines = dfnewlines[dfnewlines['asctime'].notna()]
                if dfnewlines.empty:
                    return dfnewlines
                                    
                dfnewlines['asctime'] = pd.to_datetime(dfnewlines['asctime'],errors='coerce')
                
                # Use cached max asctime
                max_asctime = Logger._max_asctime

                need_full_sort = False
                if Logger._sorted_until == 0 or max_asctime is None:
                    need_full_sort = True
                elif (dfnewlines['asctime'].min() - max_asctime).total_seconds() <=  -15:
                    need_full_sort = True

                dfnewlines_sorted = dfnewlines.sort_values(['asctime', 'sequence_number'])
                if need_full_sort:
                    Logger.dflogs = pd.concat([Logger.dflogs, dfnewlines_sorted], ignore_index=True)
                    Logger.dflogs['asctime'] = pd.to_datetime(Logger.dflogs['asctime'])
                    Logger.dflogs = Logger.dflogs.sort_values(['asctime', 'sequence_number'], ignore_index=True)
                    Logger._sorted_until = len(Logger.dflogs)                                            
                    Logger._max_asctime = pd.to_datetime(Logger.dflogs['asctime']).max()
                else:
                    # Append new lines and sort only the new part
                    Logger.dflogs = pd.concat([Logger.dflogs, dfnewlines_sorted], ignore_index=True)
                    Logger._sorted_until = len(Logger.dflogs)                        
                    Logger._max_asctime = max(
                        max_asctime,
                        dfnewlines_sorted['asctime'].iloc[-1]
                    )                    
                Logger._logfileposition = file.tell()                        
                    
                                                        
                return dfnewlines_sorted
        
        return dfnewlines

    @staticmethod
    def handleHeartbeats(keep_latest=500):
        df = Logger.dflogs
        idxhb = np.array(['#heartbeat#' in s for s in df['message'].astype(str)])
        dflasthb = df[idxhb].groupby(['user_name','logger_name']).last()
        newidx = dflasthb.index.union(Logger.dfheartbeats.index)
        Logger.dfheartbeats = Logger.dfheartbeats.reindex(newidx)
        Logger.dfheartbeats.index.names = ['user_name','logger_name']
        Logger.dfheartbeats.loc[dflasthb.index,dflasthb.columns] = dflasthb.values
        idshb = np.where(idxhb)[0]
        if len(idshb) > keep_latest:
            idshb = idshb[-keep_latest:]
        ids = np.where(~idxhb)[0]
        ids = np.sort([*ids, *idshb])
        df = df.iloc[ids, :]
        Logger.dflogs = df

    @staticmethod
    def getLastLog(df: pd.DataFrame) -> pd.DataFrame:
        """
        Return rows from the last log per (user_name, logger_name) group.
        If 'asctime' is newer, update; if equal, use 'sequence_number' for recency.

        Args:
            df (pd.DataFrame): The dataframe to process.

        Returns:
            pd.DataFrame: Updated last log records.
        """
        _dflast = df.groupby(['user_name', 'logger_name']).last()
        _dflast['asctime'] = pd.to_datetime(_dflast['asctime'])

        notinidx = _dflast.index.difference(Logger.dflast.index)
        Logger.dflast = Logger.dflast.reindex(_dflast.index.union(Logger.dflast.index))
        Logger.dflast.index.names = ['user_name', 'logger_name']
        Logger.dflast.loc[notinidx, _dflast.columns] = _dflast.loc[notinidx].values

        idx = _dflast.index
        asctime_newer = _dflast['asctime'] > Logger.dflast.loc[idx, 'asctime']
        asctime_equal = _dflast['asctime'] == Logger.dflast.loc[idx, 'asctime']
        sequence_higher = _dflast['sequence_number'].astype(str) > Logger.dflast.loc[idx, 'sequence_number'].astype(str)

        idxnew = _dflast.index[asctime_newer | (asctime_equal & sequence_higher)]
        Logger.dflast.loc[idxnew, _dflast.columns] = _dflast.loc[idxnew].values

        idxnew = idxnew.union(notinidx)

        return Logger.dflast.loc[idxnew]
                
    @staticmethod
    def getStatus(df):
        idx = np.array(['ROUTINE COMPLETED!' in s for s in df['message'].astype(str)])
        if any(idx):
            _df = df[idx]
            Logger.dfcompleted = pd.concat([Logger.dfcompleted,_df],ignore_index=True)

        idx = np.array(['ROUTINE STARTED!' in s for s in df['message'].astype(str)])
        if any(idx):
            _df = df[idx]
            Logger.dfstarted = pd.concat([Logger.dfstarted,_df],ignore_index=True)

        idx = np.array(['ROUTINE ERROR!' in s for s in df['message'].astype(str)])
        if any(idx):
            _df = df[idx]
            Logger.dferror = pd.concat([Logger.dferror,_df],ignore_index=True)

        idx = np.array(['Command to run ' in s for s in df['message'].astype(str)])
        if any(idx):
            _df = df[idx].copy()
            idx = ['<-' in s for s in _df['message']]
            if any(idx):
                _df.loc[idx,'message'] = _df.loc[idx,'message'].apply(lambda x: x.split(',')[-1])
            # get the routine name
            _df['routine'] = _df['message'].apply(lambda x: x.replace('Command to run ','').split(' ')[0])
            _df['user_name'] = _df['routine'].apply(lambda x: x.split(':')[0])
            _df['logger_name'] = _df['routine'].apply(lambda x: x.split(':')[1] if ':' in x else '')
            Logger.dfrun = pd.concat([Logger.dfrun,_df],ignore_index=True)