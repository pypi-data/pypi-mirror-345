import json
import os
import glob
import subprocess
import pytz
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from tzlocal import get_localzone
local_tz = pytz.timezone(str(get_localzone()))
import requests
import lz4
import threading

from SharedData.Logger import Logger
from SharedData.IO.AWSKinesis import KinesisStreamProducer
from SharedData.Metadata import Metadata
from SharedData.Metadata import isnan
from SharedData.Routines.WorkerPool import WorkerPool

#TODO: ADD STOPED STATE TO REALTIME ROUTINES
#TODO: MESSAGES OF PREVIOUS ROUTINES BEING ASINGED TO LATER ROUTINES
class Schedule:

    def __init__(self, schedule_name, kinesis=False):
        self.schedule_name = schedule_name
        self.producer = WorkerPool()        
        self.lastschedule = []
        self.schedule = []        
        self.batch = pd.DataFrame([])
        self.realtime = pd.DataFrame([])
        
        self.load()

    def load(self):
        
        today = datetime.now().date()
        year = today.timetuple()[0]
        month = today.timetuple()[1]
        day = today.timetuple()[2]

        _sched = Metadata('SCHEDULES/'+self.schedule_name).static.reset_index()
        if _sched.empty:
            errmsg = 'Schedule %s not found!' % (self.schedule_name)
            Logger.log.error(errmsg)
            raise Exception(errmsg)
        sched = pd.DataFrame(columns=_sched.columns)
        for i, s in _sched.iterrows():
            if not isnan(s['runtimes']):
                runtimes = s['runtimes'].split(',')
                if len(runtimes) > 1:
                    runtimes = runtimes[0]
                for t in runtimes:
                    hour = int(t.split(':')[0])
                    minute = int(t.split(':')[1])
                    dttm = local_tz.localize(
                        datetime(year, month, day, hour, minute))
                    s['runtimes'] = dttm
                    # sched = sched.reindex(columns=s.index.union(sched.columns))
                    sched = pd.concat([sched, pd.DataFrame(s).T])
            else:
                hour = int(0)
                minute = int(0)
                dttm = local_tz.localize(
                    datetime(year, month, day, hour, minute))
                s['runtimes'] = dttm
                # sched = sched.reindex(columns=s.index.union(sched.columns))
                sched = pd.concat([sched, pd.DataFrame(s).T])

        sched = sched.sort_values(
            by=['runtimes', 'name']).reset_index(drop=True)
        sched['routine'] = [s.replace('\\', '/') for s in sched['routine']]
        sched['computer'] = [s.split(':')[0] for s in sched['routine']]
        sched['script'] = [s.split(':')[-1] for s in sched['routine']]

        sched.loc[sched['dependencies'].isnull(), 'dependencies'] = ''
        sched['dependencies'] = [s.replace('\\', '/')
                                 for s in sched['dependencies']]

        sched['lastmsg'] = 'nan'
        sched['lastmsgts'] = pd.NaT
        sched['lastmsgage'] = np.nan

        sched['runmsgsent'] = False
        sched['runmsgts'] = pd.NaT
        sched['runmsgage'] = np.nan

        if not 'isrealtime' in sched.columns:
            sched['isrealtime'] = False

        sched['status'] = 'nan'
        sched['status'] = sched['status'].astype(str)

        # SAVE ROUTINES SCHEDULE IN EXECUTION SEQUENCE
        uruntimes = sched['runtimes'].unique()
        runtime = uruntimes[0]
        sched_sort = pd.DataFrame(columns=sched.columns)
        for runtime in uruntimes:
            # mark pending routines
            while True:
                idx = runtime.astimezone(tz=local_tz) >= sched['runtimes']
                idx = (idx) & ((sched['status'] == 'nan')
                               | (sched['status'] == 'WAITING DEPENDENCIES'))

                dfpending = sched[idx]
                expiredidx = dfpending.duplicated(['routine'], keep='last')
                if expiredidx.any():
                    expiredids = expiredidx.index[expiredidx]
                    sched.loc[expiredids, 'status'] = 'EXPIRED'
                dfpending = dfpending[~expiredidx]
                i = 0
                for i in dfpending.index:
                    r = dfpending.loc[i]

                    if not isnan(r['dependencies']):
                        run = True
                        sched.loc[i, 'status'] = 'WAITING DEPENDENCIES'
                        dependencies = r['dependencies'].replace(
                            '\n', '').split(',')
                        for dep in dependencies:
                            idx = sched['routine'] == dep
                            idx = (idx) & (
                                sched['runtimes'] <= runtime.astimezone(tz=local_tz))
                            ids = sched.index[idx]
                            if len(ids) == 0:
                                Logger.log.error(
                                    'Dependency not scheduled for '+r['routine'])
                                raise Exception(
                                    'Dependency not scheduled for '+r['routine'])
                            else:
                                if not str(sched.loc[ids[-1], 'status']) == 'COMPLETED':
                                    run = False
                        if run:
                            sched.loc[i, 'status'] = 'PENDING'
                    else:
                        sched.loc[i, 'status'] = 'PENDING'

                idx = sched['status'] == 'PENDING'
                if idx.any():
                    sched_sort = pd.concat([sched_sort, sched[idx]])
                    sched_sort['status'] = 'nan'
                    sched.loc[idx, 'status'] = 'COMPLETED'
                else:
                    break

        sched_sort.index.name = 'sequence'
        self.schedule = sched_sort        
        self.schedule = self.schedule.reset_index(drop=True)

    def update(self):
        self.UpdateLogs()
        self.UpdateBatchStatus()
        self.UpdateRealtimeStatus()
        self.schedule = pd.concat([self.realtime,self.batch]).reset_index()

    def UpdateLogs(self):
        Logger.getLogs()

        local_tz = pytz.timezone(str(get_localzone()))
        now = datetime.now().astimezone(tz=local_tz)

        dfsched = self.schedule.copy().set_index('routine')

        # RUN TIME
        df = Logger.dfrun.copy()
        df['routine'] = df['user_name']+':'+df['logger_name']
        df['asctime'] = pd.to_datetime(df['asctime'])
        df = df.sort_values('asctime')
        df = df.groupby('routine').last()
        idisin = dfsched.index[dfsched.index.isin(df.index)]
        dfsched.loc[idisin,'runmsgts'] = df.loc[idisin,'asctime']
        dfsched.loc[idisin,'runmsgsent'] = True
        dfsched.loc[idisin,'runmsgage'] = (now - dfsched.loc[idisin,'runmsgts']).apply(lambda x: x.total_seconds())

        # STARTED TIME
        df = Logger.dfstarted.copy()
        df['routine'] = df['user_name']+':'+df['logger_name']
        df['asctime'] = pd.to_datetime(df['asctime'])
        df = df.sort_values('asctime')
        df = df.groupby('routine').last()
        idisin = dfsched.index[dfsched.index.isin(df.index)]
        dfsched.loc[idisin,'startedmsgts'] = df.loc[idisin,'asctime']
        dfsched.loc[idisin,'startedmsgage'] = (now - dfsched.loc[idisin,'startedmsgts']).apply(lambda x: x.total_seconds())
        
        # ERROR TIME
        df = Logger.dferror.copy()
        df['routine'] = df['user_name']+':'+df['logger_name']
        df['asctime'] = pd.to_datetime(df['asctime'])
        df = df.sort_values('asctime')
        df = df.groupby('routine').last()
        idisin = dfsched.index[dfsched.index.isin(df.index)]
        dfsched.loc[idisin,'errormsgts'] = df.loc[idisin,'asctime']

        # COMPLETED TIME
        df = Logger.dfcompleted.copy()
        df['routine'] = df['user_name']+':'+df['logger_name']
        df['asctime'] = pd.to_datetime(df['asctime'])
        df = df.sort_values('asctime')
        df = df.groupby('routine').last()
        idisin = dfsched.index[dfsched.index.isin(df.index)]
        dfsched.loc[idisin,'completedmsgts'] = df.loc[idisin,'asctime']

        # LAST MESSAGE
        df = Logger.dflast.copy().reset_index()
        df['routine'] = df['user_name']+':'+df['logger_name']
        df['asctime'] = pd.to_datetime(df['asctime'])
        df = df.sort_values('asctime')
        df = df.groupby('routine').last()
        idisin = dfsched.index[dfsched.index.isin(df.index)]
        dfsched.loc[idisin,'lastmsg'] = df.loc[idisin,'message']
        dfsched.loc[idisin,'lastmsgts'] = df.loc[idisin,'asctime']
        dfsched.loc[idisin,'lastmsgage'] = (now - dfsched.loc[idisin,'lastmsgts']).apply(lambda x: x.total_seconds())

        # HEARTBEAT TIME
        df = Logger.dfheartbeats.copy().reset_index()
        df['routine'] = df['user_name']+':'+df['logger_name']
        df['asctime'] = pd.to_datetime(df['asctime'])
        df = df.sort_values('asctime')
        df = df.groupby('routine').last()
        idisin = dfsched.index[dfsched.index.isin(df.index)]
        dfsched.loc[idisin,'heartbeatmsgts'] = df.loc[idisin,'asctime']
        dfsched.loc[idisin,'heartbeatmsgage'] = (now - dfsched.loc[idisin,'heartbeatmsgts']).apply(lambda x: x.total_seconds())

        self.schedule = dfsched.reset_index()

    def UpdateBatchStatus(self):                
        local_tz = pytz.timezone(str(get_localzone()))
        now = datetime.now().astimezone(tz=local_tz)
        batch = self.schedule[self.schedule['isrealtime']==False].set_index('routine')        

        # STATE MACHINE
        completedidx = batch['completedmsgts'].notnull()
        batch.loc[completedidx,'status'] = 'COMPLETED'

        erroridx = (batch['errormsgts'].notnull()) & (~completedidx)
        batch.loc[erroridx,'status'] = 'ERROR'

        runningidx = (batch['startedmsgts'].notnull()) & (~completedidx) & (~erroridx)
        batch.loc[runningidx,'status'] = 'RUNNING'

        startingidx = (batch['runmsgts'].notnull()) & (~runningidx) & (~completedidx) & (~erroridx)
        batch.loc[startingidx,'status'] = 'STARTING'

        delayedidx = startingidx & (batch['lastmsgage']>300)
        batch.loc[delayedidx,'status'] = 'DELAYED'

        pendingidx = (batch['runtimes']<=now) & (~startingidx) & (~runningidx) & (~completedidx) & (~erroridx)
        waitingidx = pendingidx.copy()
        waitingidx[:] = False
        # check dependencies
        pendingids = batch.index[pendingidx]
        for pid in pendingids:
            dependencies = batch.loc[pid,'dependencies'].split(',')
            for dep in dependencies:
                if dep in batch.index:
                    if batch.loc[dep,'status'] not in ['COMPLETED']:
                        pendingidx[pid] = False
                        waitingidx[pid] = True
                        break
        if pendingidx.any():
            batch.loc[pendingidx,'status'] = 'PENDING'
        
        if waitingidx.any():
            batch.loc[waitingidx,'status'] = 'WAITING DEPENDENCIES'

        externalidx = batch['isexternal']==True
        batch.loc[externalidx,'status'] += ' EXTERNAL'

        self.batch = batch
    
    def UpdateRealtimeStatus(self):       
        local_tz = pytz.timezone(str(get_localzone()))
        now = datetime.now().astimezone(tz=local_tz) 
        realtime = self.schedule[self.schedule['isrealtime']==True].set_index('routine')

        # STATE MACHINE
        runningidx = (realtime['heartbeatmsgage']<=45)
        realtime.loc[runningidx,'status'] = 'RUNNING'

        startedidx = (realtime['startedmsgage'] <= 300) & (realtime['startedmsgage']<realtime['runmsgage']) & (~runningidx)
        realtime.loc[startedidx,'status'] = 'STARTED'

        startingidx =  (realtime['runmsgage'] <= 60) & (~startedidx) & (~runningidx)
        realtime.loc[startingidx,'status'] = 'STARTING'

        pendingidx = (realtime['runtimes']<=now) & (~startedidx) & (~startingidx) & (~runningidx)
        waitingidx = pendingidx.copy()
        waitingidx[:] = False
        # check dependencies
        pendingids = realtime.index[pendingidx]
        for pid in pendingids:
            dependencies = realtime.loc[pid,'dependencies'].split(',')
            for dep in dependencies:
                if dep in realtime.index:
                    if realtime.loc[dep,'status'] not in ['RUNNING']:
                        pendingidx[pid] = False
                        waitingidx[pid] = True
                        break
        if pendingidx.any():
            realtime.loc[pendingidx,'status'] = 'RESTART'
        
        if waitingidx.any():
            realtime.loc[waitingidx,'status'] = 'WAITING DEPENDENCIES'

        externalidx = realtime['isexternal']==True
        realtime.loc[externalidx,'status'] += ' EXTERNAL'

        self.realtime = realtime

    def run(self):
        newcommand = False
        sched = self.schedule

        # Run pending routines
        idx = sched['status'] == 'PENDING'
        idx = (idx) | (sched['status'] == 'START')
        idx = (idx) | (sched['status'] == 'RESTART')
        dfpending = sched[idx]
        for i in dfpending.index:
            r = dfpending.loc[i].copy()
            if (str(r['lastmsg']) == 'nan') | (r['status'] == 'RESTART'):
                newcommand = True
                target = r['computer']

                if 'SharedData' in r['script']:
                    repo = r['script'].split('.')[0]
                    routine = '.'.join(r['script'].split('.')[1:])
                    branch = ''
                else:
                    if '#' in r['script']:  # has branch
                        branch = r['script'].split('/')[0].split('#')[-1]
                        repo = r['script'].split('/')[0].split('#')[0]
                        routine = r['script'].replace(repo, '').\
                            replace('#', '').replace(branch, '')[1:]+'.py'
                    else:
                        branch = ''
                        repo = r['script'].split('/')[0]
                        routine = r['script'].replace(repo, '')[1:]+'.py'

                job = "routine"
                if r['status'] == 'RESTART':
                    job = "restart"

                data = {
                    "sender": "MASTER",
                    "job": job,
                    "target": target,
                    "repo": repo,
                    "routine": routine
                }

                if branch != '':
                    data['branch'] = branch

                if 'args' in r:
                    r['args'] = str(r['args'])
                    if (r['args'] != '') & (r['args'] != 'nan'):
                        data['args'] = r['args']

                self.producer.produce(data, 'command')

                sched.loc[r.name, 'status'] = 'STARTING'
                now = datetime.now().astimezone(tz=local_tz)
                sched.loc[r.name, 'runmsgsent'] = True
                sched.loc[r.name, 'runmsgts'] = now
                sched.loc[r.name, 'lastmsg'] = 'Command to run sent...'
                sched.loc[r.name, 'lastmsgts'] = now
                sched.loc[r.name, 'lastmsgage'] = 0
                Logger.log.info('Command to run %s:%s sent...' %
                                (target, r['script']))

        self.schedule = sched        
        return sched

    def save(self):
        if not self.schedule.equals(self.lastschedule):
            self.lastschedule = self.schedule.copy()            
            today = pd.Timestamp(pd.Timestamp.now().date())
            todaystr = today.strftime('%Y%m%d')
            md = Metadata('SCHEDULES/'+self.schedule_name+'/'+todaystr)
            md.static = self.schedule.copy()
            idx = md.static['runtimes'] != 'nan'
            md.static.loc[idx, 'runtimes'] = [d.replace(tzinfo=None) 
                                            for d in md.static['runtimes'][idx]]
            # md.static.loc[idx, 'runtimes'] = [d.tz_localize(
            #     None) for d in md.static['runtimes'][idx]]
            md.save()
