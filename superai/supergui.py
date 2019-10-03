import configparser
import os
import sys
import threading
import time
import logging
import win32api

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
logger = logging.getLogger(__name__)

from PyQt5.QtCore import QTimer, QThread
from superai.vkcode import VK_CODE
from superai.superai import SuperAiThread
from superai.subnodedb import InitDb, DbStateSelect
from superai.common import InitLog
from superai.superai import InitSetting
from superai.pathsetting import GetCfgPath

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QTableWidget, QPushButton, QVBoxLayout, QLineEdit, \
    QLabel, QMessageBox, QTableWidgetItem


def main():
    InitDb()
    InitLog()
    InitSetting()

    app = QApplication(sys.argv)
    w = QWidget()

    w.resize(1200, 300)
    w.setWindowTitle("superai")

    # 列表
    table = QTableWidget()
    columns = ["account", "region", "role", "level", "occupation", "curpilao", "money", "zhicaipoint",
               "updatepoint"]
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels(columns)

    header = table.horizontalHeader()
    header.setSectionResizeMode(8, QtWidgets.QHeaderView.ResizeToContents)

    def tick():
        states = DbStateSelect()

        if len(states) > 0 and (len(states) != table.rowCount()):
            table.clearContents()
            table.setRowCount(len(states))

        state: object
        for idx, state in enumerate(states):
            if table.itemAt(idx, 8) != str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(state["timepoint"]))):
                table.setItem(idx, 0, QTableWidgetItem(str(state["account"])))
                table.setItem(idx, 1, QTableWidgetItem(str(state["region"])))
                table.setItem(idx, 2, QTableWidgetItem(str(state["role"])))
                table.setItem(idx, 3, QTableWidgetItem(str(state["curlevel"])))
                table.setItem(idx, 4, QTableWidgetItem(str(state["zhiye"])))
                table.setItem(idx, 5, QTableWidgetItem(str(state["curpilao"])))
                table.setItem(idx, 6, QTableWidgetItem(str(state["money"])))
                # table.setItem(idx, 7, QTableWidgetItem(str(state["wuse"])))
                table.setItem(idx, 7, QTableWidgetItem(str(state["kicktime"])))
                table.setItem(idx, 8, QTableWidgetItem(
                    str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(state["timepoint"])))))

    timer = QTimer()
    timer.timeout.connect(tick)
    timer.start(1000)
    tick()

    # 设置账号按钮
    settingAccountbtn = QPushButton("setting account(notepad)")

    def settingaccont():
        os.system("start notepad %s" % (os.path.join(GetCfgPath(), "accounts")))

    settingAccountbtn.clicked.connect(settingaccont)

    # 刷角色数量策略
    jueseSettingLayout = QHBoxLayout()
    juesenumedit = QLineEdit()

    jueseSettingLayout.addWidget(QLabel("role num: "))
    jueseSettingLayout.addWidget(juesenumedit)

    cfgfile = os.path.join(GetCfgPath(), "superai.cfg")
    config = configparser.RawConfigParser()
    config.read(cfgfile)
    num = config.get("superai", "单账号刷角色数量")
    juesenumedit.setText(num)

    # 启动按钮
    buttonlayout = QHBoxLayout()
    confirmbtn = QPushButton("save config")

    def confirm():
        cfgfile = os.path.join(GetCfgPath(), "superai.cfg")
        config = configparser.RawConfigParser()
        config.read(cfgfile)
        config.set("superai", "单账号刷角色数量", juesenumedit.text())
        f = open(cfgfile, "w")
        config.write(f)
        f.close()

        msgBox = QMessageBox()
        msgBox.setText("成功修改配置")
        msgBox.exec_()

    startbtn = QPushButton("start(f11)")

    t = SuperAiThread(stophotkey=True)

    def start():
        nonlocal t
        if startbtn.text() == "start(f11)":
            t.start()
            startbtn.setText("stop(f11)")
        else:
            t.stop()
            t = SuperAiThread(stophotkey=True)
            startbtn.setText("start(f11)")

    class Hotkey(QThread):
        def run(self) -> None:
            while True:
                f11 = win32api.GetAsyncKeyState(VK_CODE['F11'])
                if f11 != 0:
                    startbtn.clicked.emit()
                    time.sleep(1)
                time.sleep(0.005)

    hotkey = Hotkey()
    hotkey.start()

    confirmbtn.clicked.connect(confirm)

    startbtn.clicked.connect(start)

    buttonlayout.addWidget(confirmbtn)
    buttonlayout.addWidget(startbtn)

    listlayout = QVBoxLayout()
    listlayout.addWidget(table)

    settinglayout = QVBoxLayout()
    settinglayout.addWidget(settingAccountbtn)
    settinglayout.addLayout(jueseSettingLayout)
    settinglayout.addSpacing(195)
    settinglayout.addLayout(buttonlayout)
    settinglayout.setAlignment(QtCore.Qt.AlignTop)

    widgetlayout = QHBoxLayout()
    widgetlayout.addLayout(listlayout)
    widgetlayout.addLayout(settinglayout)

    widgetlayout.setStretch(0, 10)
    widgetlayout.setStretch(1, 1)

    w.setLayout(widgetlayout)
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
