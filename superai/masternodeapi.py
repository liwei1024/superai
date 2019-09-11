import json
import os
import sys
import threading

from flask import Flask
from flask_cors import CORS
from flask_jsonrpc import JSONRPC
from flask_socketio import SocketIO, emit

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

app = Flask(__name__)
# app.config["SECRET_KEY"] = "secret!"

CORS(app)

jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)
socketio = SocketIO(app, cors_allowed_origins='*')

thread = None
threadLock = threading.Lock()


@app.route('/')
def test():
    return 'masternodeapi'


subs = [
    (1, "localhost"),
    (2, "localhost"),
    (3, "localhost"),
]


@jsonrpc.method('getsubs')
def getSubs():
    newsubs = []
    for idx, sub in enumerate(subs):
        newsubs.append({"id": sub[0], "ip": sub[1]})
    jsonstr = json.dumps(newsubs, ensure_ascii=False)
    return jsonstr


# websocket推送所有机器列表
@socketio.on('getsubspush')
def getsubspush():
    def background_thread():
        while True:
            socketio.emit('getsubspush', getSubs())
            socketio.sleep(2)

    global thread
    with threadLock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)


def main():
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 33333), app, handler_class=WebSocketHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
