import json
import os
import sys

from flask import Flask
from flask_jsonrpc import JSONRPC

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

app = Flask(__name__)

jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)


@app.route('/')
def test():
    return 'masternodeapi'


subs = [
    (1, "192.168.0.1"),
    (2, "192.168.0.2"),
]


@jsonrpc.method('getsubs')
def getSubs():
    jsonstr = json.dumps(subs, ensure_ascii=False)
    return jsonstr

