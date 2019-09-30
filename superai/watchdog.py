import json
import logging
import os
import sys
import threading

import subprocess

from flask import Flask
from flask_cors import CORS
from flask_jsonrpc import JSONRPC

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

app = Flask(__name__)
CORS(app)

jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)

mymaindir = "d:/win/studio/script"
mymainip = "192.168.0.200"


# 同步superai目录
@jsonrpc.method("rsyncsuperai")
def rsyncSuperai():
    command = """set-ExecutionPolicy RemoteSigned -Force;$IP="%s";net use \\$IP\win yqsy021 /user:yq /y;mkdir -Force 
    "c:\win\script";XCOPY \\$IP\win\studio\script c:\win\script /s /e /r /k /y /d; cd 
    c:\win\script;./bootstrap.ps1""" % mymainip


# 启动superai程序
@jsonrpc.method("startsuperai")
def startSuperai():
    pass


# 停止superai程序
@jsonrpc.method("stopsuperai")
def stopSuperai():
    pass


# 布置账号
@jsonrpc.method("arrange")
def arrangeSuperai():
    pass


def main():
    pass
    # subprocess.call('powershell.exe ipconfig')


if __name__ == '__main__':
    main()
