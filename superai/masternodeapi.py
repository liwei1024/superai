import json
import os
import sys
import threading

import logging

from engineio.async_drivers import gevent

logger = logging.getLogger(__name__)

from flask import Flask
from flask_cors import CORS
from flask_jsonrpc import JSONRPC
from flask_socketio import SocketIO, emit

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.common import InitLog

app = Flask(__name__)
# app.config["SECRET_KEY"] = "secret!"

CORS(app)

jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='gevent')


@app.route('/')
def test():
    return 'masternodeapi'


subs = [
    (1, "192.168.0.85"),
    (2, "192.168.0.83")
]


@jsonrpc.method('getsubs')
def getSubs():
    newsubs = []
    for idx, sub in enumerate(subs):
        newsubs.append({"id": sub[0], "ip": sub[1]})
    jsonstr = json.dumps(newsubs, ensure_ascii=False)
    return jsonstr


@socketio.on('getsubspush')
def getsubspush():
    socketio.emit('getsubspush', getSubs())


def background_thread():
    while True:
        socketio.emit('getsubspush', getSubs())
        logger.info("推送机器列表 getsubspush")
        socketio.sleep(2)


def main():
    InitLog()

    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 33333), app, handler_class=WebSocketHandler)
    socketio.start_background_task(target=background_thread)
    server.serve_forever()


if __name__ == '__main__':
    main()
