import json
import os
import sys
import threading

from flask import Flask
from flask_jsonrpc import JSONRPC
from flask_cors import CORS
from flask_socketio import SocketIO, emit

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.sysmonitor import sysVersion, cpuInfo, memInfo, diskInfo, networkInfo, sysFlushThread, cpuFlushStop, \
    getCpuResult, getSysversionResult, getMemResult, getDiskResult, getNetworkResult
from superai.subnodedb import DbEventSelect, DbStateSelect, DbItemSelect

app = Flask(__name__)
CORS(app)

jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)
socketio = SocketIO(app, cors_allowed_origins='*')

thread = None
threadLock = threading.Lock()


@app.route('/')
def test():
    return 'subnodeapi'


@jsonrpc.method('getEvent')
def getEvent():
    rows = DbEventSelect()
    jsonstr = json.dumps(rows, ensure_ascii=False)
    return jsonstr


@jsonrpc.method('getState')
def getState():
    rows = DbStateSelect()
    jsonstr = json.dumps(rows, ensure_ascii=False)
    return jsonstr


@jsonrpc.method('getItem')
def getItem():
    rows = DbItemSelect()
    jsonstr = json.dumps(rows, ensure_ascii=False)
    return jsonstr


@jsonrpc.method('getMachineState')
def getMachineState():
    result = {
        "sys": getSysversionResult(),
        "cpuInfo": getCpuResult(),
        "memInfo": getMemResult(),
        "diskInfo": getDiskResult(),
        "networkInfo": getNetworkResult()
    }
    jsonstr = json.dumps(result, ensure_ascii=False)
    return jsonstr


# websocket推送单个机器信息
@socketio.on('machinestatepush')
def machinestatepush():
    def background_thread():
        while True:
            socketio.emit('machinestatepush', getMachineState())
            socketio.sleep(2)

    global thread
    with threadLock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)


def main():
    t = threading.Thread(target=sysFlushThread)
    t.start()
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 22222), app, handler_class=WebSocketHandler)
    server.serve_forever()
    cpuFlushStop()


if __name__ == '__main__':
    main()
