import json
import os
import sys
import threading

import logging

from engineio.async_drivers import gevent

logger = logging.getLogger(__name__)

from flask import Flask
from flask_jsonrpc import JSONRPC
from flask_cors import CORS
from flask_socketio import SocketIO, emit

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.common import InitLog

from superai.sysmonitor import sysFlushThread, cpuFlushStop, \
    getCpuResult, getSysversionResult, getMemResult, getDiskResult, getNetworkResult
from superai.subnodedb import DbEventSelect, DbStateSelect, DbItemSelect, DbStateGetNearestTimepoint

app = Flask(__name__)
CORS(app)

jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)
socketio = SocketIO(app, cors_allowed_origins='*',async_mode='gevent')


@app.route('/')
def test():
    return 'subnodeapi'


# jsonprc 事件
@jsonrpc.method('getEvent')
def getEvent():
    rows = DbEventSelect()
    jsonstr = json.dumps(rows, ensure_ascii=False)
    return jsonstr


# jsonrpc 状态
@jsonrpc.method('getState')
def getState():
    rows = DbStateSelect()
    jsonstr = json.dumps(rows, ensure_ascii=False)
    return jsonstr


# jsonrpc 流水
@jsonrpc.method('getItem')
def getItem():
    rows = DbItemSelect()
    jsonstr = json.dumps(rows, ensure_ascii=False)
    return jsonstr


# jsonrpc
@jsonrpc.method('getMachineState')
def getMachineState():
    result = {
        "sys": getSysversionResult(),
        "cpuInfo": getCpuResult(),
        "memInfo": getMemResult(),
        "diskInfo": getDiskResult(),
        "networkInfo": getNetworkResult(),
        "latestStateInfo":  DbStateGetNearestTimepoint()
    }
    jsonstr = json.dumps(result, ensure_ascii=False)
    return jsonstr


# websocket 推送事件
@socketio.on('geteventpush')
def geteventpush():
    socketio.emit('geteventpush', getEvent())


# websocket 推送状态
@socketio.on('getstatepush')
def getstatepush():
    socketio.emit('getstatepush', getState())


# websocket 推送流水
@socketio.on('getitempush')
def getitempush():
    socketio.emit('getitempush', getItem())


# websocket 推送状态信息
@socketio.on('machinestatepush')
def machinestatepush():
    socketio.emit('machinestatepush', getMachineState())


def background_thread():
    while True:
        socketio.emit('machinestatepush', getMachineState())
        socketio.emit('geteventpush', getEvent())
        socketio.emit('getstatepush', getState())
        socketio.emit('getitempush', getItem())

        logger.info("推送机器/业务数据 machinestatepush")

        socketio.sleep(2)


def subnodeapi():
    t = threading.Thread(target=sysFlushThread)
    t.start()
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 22222), app, handler_class=WebSocketHandler)
    socketio.start_background_task(target=background_thread)
    server.serve_forever()
    cpuFlushStop()


def main():
    InitLog()

    subnodeapi()


if __name__ == '__main__':
    main()
