import json
import logging
import os
import sys

logger = logging.getLogger(__name__)

from flask import Flask
from flask_jsonrpc import JSONRPC
from flask_cors import CORS
from flask_socketio import SocketIO
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.pathsetting import GetVersionFile, GetServerRootDirectory
from superai.common import InitLog

app = Flask(__name__)
CORS(app)

jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='gevent')

# 版本增量迭代升级
versionmap = {
    "1_0_0", "1_0_1",
}


@app.route('/')
def test():
    return 'updateserver'


# 最新版本是多少
@jsonrpc.method('getVersion')
def getVersion():
    with open(os.path.join(GetServerRootDirectory(), "version"), 'r') as f:
        v = f.readline()
        j = {"version": v}
        jsonstr = json.dumps(j, ensure_ascii=False)
        return jsonstr


# 下载文件
@jsonrpc.method('download')
def downloadFiles(curversion):
    curversion = curversion.replace(".", "_")
    filemap = {}
    if curversion in versionmap:
        j = {"results": None}
        updatedir = curversion + '-' + versionmap[curversion]

        for root, dirs, files in os.walk(os.path.join(GetServerRootDirectory(), updatedir)):
            for file in files:
                logger.info(file)

                with open(file) as f:
                    bs64str = base64.b64encode(f.read())

                    filemap[file] = bs64str

        j["results"] = filemap

        jsonstr = json.dumps(j, ensure_ascii=False)
        return jsonstr

    else:
        j = {"error": "找不到当前版本号%s的更新补丁包" % curversion}
        jsonstr = json.dumps(j, ensure_ascii=False)
        return jsonstr


def main():
    InitLog()
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 22222), app, handler_class=WebSocketHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
