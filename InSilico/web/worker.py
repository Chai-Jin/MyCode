#!/bin/env python
#-*- coding: utf-8 -*-
import json
import subprocess
# 디렉토리 설정
import os
import shutil
pid = os.getpid()
curdir = os.path.dirname(os.path.realpath(__file__))
jobdir = os.path.join(curdir,'JOB')
readydir = os.path.join(jobdir,'READY')
doingdir = os.path.join(jobdir,'DOING')
okdir = os.path.join(jobdir,'OK')
faildir = os.path.join(jobdir,'FAIL')
pidfile = os.path.join(os.path.join(jobdir,'PID'),str(pid))

proctitle = "chaijin-web worker #%s" % str(pid)

# 설정 출력
print "===> %s" % proctitle
print "     curdir : %s" % curdir
print "     JOB dir : %s" % jobdir
print "     READY dir : %s" % readydir
print "     DOING dir : %s" % doingdir
print "     OK dir : %s" % okdir
print "     FAIL dir : %s" % faildir
print "     PID file : %s" % pidfile
print

import time

# file lock 을 만든다.
# if program stops working, then remove 'JOB/job.lock'
from lockfile import LockFile
lock = LockFile(os.path.join(jobdir,'job'))

# 종료될때 PID파일 제거 & 락 해제
import signal
def handler(signum, frame):
    os.remove(pidfile)
    #lock.release()
    print "OK BYE"
    exit()

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

while(True):
    # PID 파일을 루프돌때마다 비운다.
    # with 를 벗어나면 close()가 자동으로 호출된다.
    with open(pidfile, 'w') as pidf:
        print "===> Loop #%s" % pid

        # worker끼리 작동이 겹치지 않게 file lock을 건다.
        # with lock 을 벗어나면 lock이 플리고 다른 worker 하나가 작동한다.
        with lock:
            # READY 하나 가져오기
            ready = [f for f in os.listdir(readydir) if not f.startswith('.')]
            if len(ready) == 0:
                print "---> NO JOBS. Retry after 5 secs."
                time.sleep(5)
                continue
            
            # JOB이 있으면 첫번째 것을 가져온다.
            ready0 = ready[0]

            # PID파일에 처리중인 JOB이름을 저장
            pidf.write(ready0)
            pidf.flush()
            
            readyfile = os.path.join(readydir, ready0)
            doingfile = os.path.join(doingdir, ready0)
            okfile = os.path.join(okdir, ready0)
            failfile = os.path.join(faildir, ready0)
            print "===> START %s" % readyfile

            # DOING으로 옮긴다.
            shutil.move(readyfile, doingfile)
            print "     Move %s to %s" % (readyfile, doingfile)

        result = True

        # 옮긴 파일을 읽는다.
        with open(doingfile, 'r') as doingfh:
            try:
                job = json.load(doingfh)
            except ValueError as e:
                print "!!!! Invalid JSON"
                errmsg = "\n".join(["     "+ee for ee in str(e).splitlines()])
                print errmsg
                result = False

            if result:
                print "---> JOB"
                print "     ",
                print job
                # cmd 를 이용해서 실행한다.
                cmd = job['cmd']
                if cmd:
                    result = True if subprocess.call(cmd)==0 else False
                else:
                    print "!!!! no cmd"
                    result = False

        # 결과에 따라서 다시 옮긴다.
        if result:
            print "---> OK : %s" % okfile
            shutil.move(doingfile, okfile)
        else:
            print "!!!! FAIL : %s" % failfile
            shutil.move(doingfile, failfile)

