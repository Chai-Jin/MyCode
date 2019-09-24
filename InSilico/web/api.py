# -*- coding: utf-8 -*-
# api by @lazykuna

import os
import web


job_list = {}

class Job:
        def __init__(self):
                self.job_path = ""
                self.job_status = 0             # 0 : Error, 1 : Pending, 2: Done
                self.job_url = ""
        def CheckStatus(self):          # Check is current job is done or not
                if (os.path.exists(os.path.join(self.job_path, 'DONE'))):
                        self.job_status = 2
                elif (os.path.exists(os.path.join(self.job_path, 'ERROR'))):
                        self.job_status = 0
                else:
                        self.job_status = 1
                return self.job_status



def CreateJob(job_id, job_path=None):
        job = Job()
        if (job_path == None):
                #curworkdir = os.path.join('./WORK', job_id)
                curworkdir = os.path.join(web.app.config['WORK_DIR'], job_id)
                job_path = curworkdir
        job.job_path = job_path
        job.job_status = 1
        job.job_url = "http://epigenomics.snu.ac.kr:9090/result/%s" % job_id
        job_list[job_id] = job

def GetJob(job_id):
        if (job_id not in job_list):
                CreateJob(job_id)
                #return 0
        job = job_list[job_id]
        job.CheckStatus()
        return job
