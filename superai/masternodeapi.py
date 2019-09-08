import json
import os
import sys

from flask import Flask
from flask_cors import CORS
from flask_jsonrpc import JSONRPC

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

app = Flask(__name__)
CORS(app)

jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)


@app.route('/')
def test():
    return 'masternodeapi'


subs = [
    (1, "192.168.1.155"),
    (2, "192.168.1.155"),  # TODO 暂时用本机
    (3, "192.168.1.155"),  # TODO 暂时用本机
]


@jsonrpc.method('getsubs')
def getSubs():
    newsubs = []
    for idx, sub in enumerate(subs):
        newsubs.append({"id": sub[0], "ip": sub[1]})
    jsonstr = json.dumps(newsubs, ensure_ascii=False)
    return jsonstr


def main():
    app.run(host='0.0.0.0', port=33333)


if __name__ == '__main__':
    main()
