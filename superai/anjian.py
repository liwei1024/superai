import logging
import os
import sys
import time

import win32gui

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
logger = logging.getLogger(__name__)

from superai.pathsetting import GetYoulingExe
from superai.common import checkIfProcessRunning
from superai.youling import Youling
from superai.config import GetConfig
from superai.yijianshu import Yijianshu

anjianobj = None


def aj():
    global anjianobj

    if anjianobj is None:
        config = GetConfig()
        anjianuse = config.get("superai", "按键")
        if anjianuse == "易键鼠":
            anjianobj = Yijianshu()
        elif anjianuse == "幽灵按键":
            if checkIfProcessRunning("youlingserver.exe"):
                os.system("taskkill /F /im youlingserver.exe")

            os.system("\"%s\"" % GetYoulingExe())

            for i in range(5):
                logger.info("等待启动幽灵键鼠 %d" % i), time.sleep(0.2)

            hwnd = win32gui.FindWindow(None, "youlingserver")
            if hwnd != 0:
                import win32con
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

            anjianobj = Youling()
    return anjianobj


def main():
    if checkIfProcessRunning("youlingserver.exe"):
        os.system("taskkill /F /im youlingserver.exe")


if __name__ == '__main__':
    main()
