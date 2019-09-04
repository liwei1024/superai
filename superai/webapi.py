import json
import os
import sys

from flask import Flask
from flask_jsonrpc import JSONRPC
from flask_sqlalchemy import SQLAlchemy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.sqlite import DbEventSelect, DbStateSelect, DbItemSelect

app = Flask(__name__)

jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)


@app.route('/')
def test():
    return 'superai'


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


def main():
    # webapi 和 superai 是两个程序,所以不用担心冲突
    app.run()


if __name__ == '__main__':
    main()
