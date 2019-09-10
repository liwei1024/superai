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
socketio = SocketIO(app)


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


@socketio.on('machinestatepush')
def machinestatepush():
    socketio.emit(event="machinestatepush")


def main():
    t = threading.Thread(target=sysFlushThread)
    t.start()
    app.run(host='0.0.0.0', port=22222)
    cpuFlushStop()


if __name__ == '__main__':
    main()
