import logging
import os
import sys
import time

import win32api


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
logger = logging.getLogger(__name__)

from superai.anjian import aj
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from superai.vkcode import VK_CODE
from superai.subnodedb import InitDb, DbStateSelect, DbStateDel
from superai.common import InitLog
from superai.superai import InitSetting
from superai.pathsetting import GetCfgPath
from superai.config import GetConfig, SaveConfig
from superai.superai import SuperAiThread

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
    w.setWindowTitle(" ")

    # 列表
    table = QTableWidget()
    columns = ["账号", "大区", "角色", "等级", "职业", "当前疲劳", "金币", "制裁时间点",
               "更新时间点"]
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels(columns)

    header = table.horizontalHeader()
    header.setSectionResizeMode(8, QtWidgets.QHeaderView.ResizeToContents)

    def tick():
        states = DbStateSelect()

        if len(states) > 0 and (len(states) != table.rowCount()):
            table.clearContents()
            table.setRowCount(len(states))
        elif len(states) == 0:
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
    settingAccountbtn = QPushButton("设置账号")
    settingAccountDefaultbtn = QPushButton("参考账号配置")


    def settingaccont():
        os.system("start notepad %s" % (os.path.join(GetCfgPath(), "accounts")))

    def settingaccountdefault():
        os.system("start notepad %s" % (os.path.join(GetCfgPath(), "accounts.template")))

    settingAccountbtn.clicked.connect(settingaccont)
    settingAccountDefaultbtn.clicked.connect(settingaccountdefault)

    settingAccountLayout = QHBoxLayout()
    settingAccountLayout.addWidget(settingAccountbtn)
    settingAccountLayout.addWidget(settingAccountDefaultbtn)

    # 设置配置
    settingLayout = QHBoxLayout()

    settingCfgbtn = QPushButton("设置配置")
    settingCfgDefaultbtn = QPushButton("参考默认配置")


    def settingcfg():
        os.system("start notepad %s" % (os.path.join(GetCfgPath(), "superai.cfg")))

    def settingCfgDefault():
        os.system("start notepad %s" % (os.path.join(GetCfgPath(), "superai.cfg.template")))

    settingCfgbtn.clicked.connect(settingcfg)
    settingCfgDefaultbtn.clicked.connect(settingCfgDefault)

    settingLayout.addWidget(settingCfgbtn)
    settingLayout.addWidget(settingCfgDefaultbtn)

    # 启动按钮
    buttonlayout = QHBoxLayout()

    startbtn = QLabel("开启(HOME)")

    t = SuperAiThread(stophotkey=True)

    def start():
        nonlocal t
        if startbtn.text() == "开启(HOME)":
            t.start()
            startbtn.setText("关闭(END)")
        else:
            logger.warning("已经开启了")

    def stop():
        nonlocal t
        if startbtn.text() == "关闭(END)":
            t.stop()
            t = SuperAiThread(stophotkey=True)
            startbtn.setText("开启(HOME)")
        else:
            logger.warning("已经关闭了")

    class Hotkey(QThread):
        startsign = pyqtSignal()
        stopsign = pyqtSignal()

        def run(self) -> None:
            while True:
                home = win32api.GetAsyncKeyState(VK_CODE['home'])
                if home != 0:
                    self.startsign.emit()
                    time.sleep(1)
                end = win32api.GetAsyncKeyState(VK_CODE['end'])
                if end != 0:
                    self.stopsign.emit()
                    time.sleep(1)
                time.sleep(0.005)

    # 快捷键
    hotkey = Hotkey()
    hotkey.startsign.connect(start)
    hotkey.stopsign.connect(stop)
    hotkey.start()

    buttonlayout.setAlignment(QtCore.Qt.AlignCenter)
    buttonlayout.addWidget(startbtn)

    listlayout = QVBoxLayout()
    listlayout.addWidget(table)

    def reset():
        DbStateDel()

        msgBox = QMessageBox()
        msgBox.setText("成功重置数据库")
        msgBox.setWindowTitle("superai")
        msgBox.exec_()

    # 清除制裁状态按钮
    resetbtn = QPushButton("重置数据库")

    resetbtn.clicked.connect(reset)

    settinglayout = QVBoxLayout()
    # settinglayout.addWidget(settingAccountbtn)
    settinglayout.addLayout(settingAccountLayout)
    settinglayout.addLayout(settingLayout)
    settinglayout.addWidget(resetbtn)
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
