import logging
import os
import socket
import sys
import threading
import time

import win32gui

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
logger = logging.getLogger(__name__)

from superai.vkcode import VK_reverse
from superai.common import RanSleep, KongjianSleep, GetCursorInfo

server_address = ('localhost', 8888)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)


# 发送指令,同步接收
def socketrpc(command):
    sock.sendto(bytes(command, "gb2312"), server_address)
    buf = sock.recvfrom(10)
    return True if str(buf) == "yes" else False


class Youling:
    def __init__(self):
        pass

    # 初始化函数
    def Init(self):
        # 幽灵好像不能修改vid pid, 所以默认返回true了
        return True

    # 释放所有按键
    def ReleaseAllKey(self):
        socketrpc("releaseall")

    # 疾跑右
    def JiPaoYou(self):
        socketrpc("keydown Right"), RanSleep(0.15)
        socketrpc("keyup Right"), RanSleep(0.15)
        socketrpc("keydown Right"), RanSleep(0.15)

    # 疾跑左
    def JiPaoZuo(self):
        socketrpc("keydown Left"), RanSleep(0.15)
        socketrpc("keyup Left"), RanSleep(0.15)
        socketrpc("keydown Left"), RanSleep(0.15)

    # 按下 上
    def DownSHANG(self):
        socketrpc("keydown Up")

    # 按下 下
    def DownXIA(self):
        socketrpc("keydown Down")

    # 按下 左
    def DownZUO(self):
        socketrpc("keydown Left")

    # 按下 右
    def DownYOU(self):
        socketrpc("keydown Right")

    # 按下 左上
    def DownZUOSHANG(self):
        self.DownZUO()
        self.DownSHANG()

    # 按下 左下
    def DownZUOXIA(self):
        self.DownZUO()
        self.DownXIA()

    # 按下 右上
    def DownYOUSHANG(self):
        self.DownYOU()
        self.DownSHANG()

    # 按下 右下
    def DownYOUXIA(self):
        self.DownYOU()
        self.DownXIA()

    # 弹起 上
    def UpSHANG(self):
        socketrpc("keyup Up")

    # 弹起 下
    def UpXIA(self):
        socketrpc("keyup Down")

    # 弹起 左
    def UpZUO(self):
        socketrpc("keyup Left")

    # 弹起 右
    def UpYOU(self):
        socketrpc("keyup Right")

    # 弹起 左上
    def UpZUOSHANG(self):
        self.UpZUO()
        self.UpSHANG()

    # 弹起 左下
    def UpZUOXIA(self):
        self.UpZUO()
        self.UpXIA()

    # 弹起 右上
    def UpYOUSHANG(self):
        self.UpYOU()
        self.UpSHANG()

    # 弹起 右下
    def UpYOUXIA(self):
        self.UpYOU()
        self.UpXIA()

    # 按键
    def PressKey(self, key):
        youlingstr = VK_reverse[key]
        socketrpc("keydown %s" % youlingstr), KongjianSleep()
        socketrpc("keyup %s" % youlingstr)

    # 按键 右
    def PressRight(self):
        socketrpc("keydown Right"), KongjianSleep()
        socketrpc("keyup Right")

    # 按键 左
    def PressLeft(self):
        socketrpc("keydown Left"), KongjianSleep()
        socketrpc("keyup Left")

    # 按键 上
    def PressUp(self):
        socketrpc("keydown Up"), KongjianSleep()
        socketrpc("keyup Up")

    # 按键 下
    def PressDown(self):
        socketrpc("keydown Down"), KongjianSleep()
        socketrpc("keyup Down")

    # 按键 x
    def PressX(self):
        socketrpc("keydown x"), KongjianSleep()
        socketrpc("keyup x")

    # 按键攻击
    def PressSkill(self, key, delay, afterdelay, thenpress=None, doublepress=False, issimpleattack=False):
        youlingstr = VK_reverse[key]

        if issimpleattack:
            for i in range(10):
                socketrpc("keydown %s" % youlingstr), RanSleep(0.05)
                socketrpc("keyup %s" % youlingstr), RanSleep(0.05)
                RanSleep(0.05)

        else:
            socketrpc("keydown %s" % youlingstr), RanSleep(delay)
            socketrpc("keyup %s" % youlingstr), RanSleep(afterdelay)

            if thenpress is not None:
                youlingstrThen = VK_reverse[thenpress]
                socketrpc("keydown %s" % youlingstrThen), KongjianSleep()
                socketrpc("keyup %s" % youlingstrThen)

            if doublepress:
                def worker():
                    for i in range(10):
                        socketrpc("keydown %s" % youlingstr), KongjianSleep()
                        socketrpc("keyup %s" % youlingstr), KongjianSleep()

                threading.Thread(target=worker).start()

    # 按键 后跳
    def PressHouTiao(self):
        socketrpc("keydown Down"), KongjianSleep()
        socketrpc("keydown c")

        socketrpc("keyup c"), KongjianSleep()
        socketrpc("keyup Down")

    # 是否移动到目的位置
    def IsMovedTo(self, x, y):
        (curx, cury) = GetCursorInfo()
        return (curx, cury) == (x, y)

    # 鼠标移动到 (游戏内)
    def MouseMoveTo(self, x, y):
        hwnd = win32gui.FindWindow("地下城与勇士", "地下城与勇士")

        try:
            centrex, centrey = win32gui.ClientToScreen(hwnd, (int(x), int(y)))
        except:
            return

        flag = False
        # 修正
        while not self.IsMovedTo(centrex, centrey):
            (curx, cury) = GetCursorInfo()
            if flag:
                logger.warning("当前鼠标坐标: (%d, %d) != (%d, %d)" % (curx, cury, centrex, centrey))
            else:
                flag = True

            socketrpc("moveto %d %d" % (centrex, centrey)), RanSleep(0.3)

    # 鼠标移动到 (游戏登录界面)
    def MouseMoveToLogin(self, x, y):
        hwnd = win32gui.FindWindow("TWINCONTROL", "地下城与勇士登录程序")

        try:
            centrex, centrey = win32gui.ClientToScreen(hwnd, (int(x), int(y)))
        except:
            return

        flag = False
        # 修正
        while not self.IsMovedTo(centrex, centrey):
            (curx, cury) = GetCursorInfo()

            if flag:
                logger.warning("当前鼠标坐标: (%d, %d) != (%d, %d)" % (curx, cury, centrex, centrey))
            else:
                flag = True
            socketrpc("moveto %d %d" % (centrex, centrey)), RanSleep(0.3)

    # 相对移动
    def MouseMoveR(self, x, y):
        (curx, cury) = GetCursorInfo()
        centrex, centrey = curx + x, cury + y

        flag = False
        # 修正
        while not self.IsMovedTo(centrex, centrey):
            (curx, cury) = GetCursorInfo()

            if flag:
                logger.warning("当前鼠标坐标: (%d, %d) != (%d, %d)" % (curx, cury, centrex, centrey))
            else:
                flag = True
            socketrpc("moveto %d %d" % (centrex, centrey)), RanSleep(0.3)

    # 右键单击
    def MouseRightClick(self):
        socketrpc("rightdown"), KongjianSleep()
        socketrpc("rightup")

    # 左键单击
    def MouseLeftClick(self):
        socketrpc("leftdown"), KongjianSleep()
        socketrpc("leftup")

    # shift + 左按键
    def ShiftLeft(self):
        socketrpc("keydown Shift"), KongjianSleep()
        socketrpc("leftdown"), KongjianSleep()
        socketrpc("leftup"), KongjianSleep()
        socketrpc("keyup Shift")

    # shift + 右按键
    def ShiftRight(self):
        socketrpc("keydown Shift"), KongjianSleep()
        socketrpc("rightdown"), KongjianSleep()
        socketrpc("rightup"), KongjianSleep()
        socketrpc("keyup Shift")

    # 左键按下
    def MouseLeftDown(self):
        socketrpc("leftdown")

    # 左键弹出
    def MouseLeftUp(self):
        socketrpc("leftup")

    # 滚轮
    def MouseWheel(self, v):
        if v > 0:
            for i in range(v):
                socketrpc("whellup 1")
                time.sleep(0.005)

        else:
            v = -v
            for i in range(v):
                socketrpc("whelldown 1")
                time.sleep(0.005)

    # 输入gbk
    def KeyInputGBK(self, s):
        sock.sendto(bytes("input %s" % s, "gb2312"), server_address)

    # 删除所有文字
    def DeleteAll(self):
        socketrpc("keydown Backspace"), RanSleep(2)
        socketrpc("keyup Backspace"), RanSleep(0.05)


def main():
    time.sleep(1.0)

    anjian = Youling()
    anjian.MouseWheel(-3)

    anjian.KeyInputGBK("GGC88zyj")

if __name__ == '__main__':
    main()
