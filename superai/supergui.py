import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))


from superai.superai import InitSetting
from superai.pathsetting import GetCfgPath


from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QTableWidget, QPushButton, QVBoxLayout, QLineEdit, \
    QLabel



def main():
    app = QApplication(sys.argv)
    w = QWidget()

    InitSetting()

    w.resize(1200, 300)
    w.setWindowTitle("superai")

    # 列表
    table = QTableWidget()
    columns = ["account", "region", "role", "level", "occupation", "curpilao", "money", "wuse", "zhicaipoint", "updatepoint"]
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels(columns)

    # 设置账号按钮
    settingAccountbtn = QPushButton("setting account(notepad)")

    def settingaccont():
        os.system("start notepad %s" % (os.path.join(GetCfgPath(), "accounts")))

    settingAccountbtn.clicked.connect(settingaccont)

    # 刷角色数量策略
    jueseSettingLayout = QHBoxLayout()
    jusesenumedit = QLineEdit()

    jueseSettingLayout.addWidget(QLabel("role num: "))
    jueseSettingLayout.addWidget(jusesenumedit)

    # 启动按钮
    buttonlayout = QHBoxLayout()
    confirmbtn = QPushButton("save config")
    startbtn = QPushButton("start")
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
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
