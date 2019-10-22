# coding=utf-8
import logging
import os
import sys
import threading
import time
from ctypes import *

import win32gui

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

logger = logging.getLogger(__name__)

from superai.pathsetting import GetYiLib
from superai.common import InitLog, GetCursorInfo, RanSleep, KongjianSleep, GameWindowToTop
from superai.vkcode import *

lib = GetYiLib()
# 键盘

# 打开
lib.M_Open.argtypes = [c_int]
lib.M_Open.restype = c_void_p

# 以特殊vid pid 打开
lib.M_Open_VidPid.argtypes = [c_int, c_int]
lib.M_Open_VidPid.restype = c_void_p

# 获取设备序列号
lib.M_GetDevSn.argtypes = [c_void_p, POINTER(c_uint), c_char_p]
lib.M_GetDevSn.restype = c_int

# 按下
lib.M_KeyDown2.argtypes = [c_void_p, c_int]
lib.M_KeyDown2.restype = c_int

# 弹起
lib.M_KeyUp2.argtypes = [c_void_p, c_int]
lib.M_KeyUp2.restype = c_int

# 弹起所有按键
lib.M_ReleaseAllKey.argtypes = [c_void_p]
lib.M_KeyUp2.restype = c_int

# 输入支持GBK
lib.M_KeyInputStringGBK.argtypes = [c_void_p, c_void_p, c_int]
lib.M_KeyInputStringGBK.restype = c_int

# 按下左键不弹起
lib.M_LeftDown.argtypes = [c_void_p]
lib.M_LeftDown.restype = c_int

# 弹起左键
lib.M_LeftUp.argtypes = [c_void_p]
lib.M_LeftUp.restype = c_int

# 按下右键不弹起
lib.M_RightDown.argtypes = [c_void_p]
lib.M_RightDown.restype = c_int

# 弹起右键
lib.M_RightUp.argtypes = [c_void_p]
lib.M_RightUp.restype = c_int

# 当前相对位置移动鼠标
lib.M_MoveR.argtypes = [c_void_p, c_int, c_int]
lib.M_MoveR.restype = c_int

# 滚轮 (向上正,向下负)
lib.M_MouseWheel.argtypes = [c_void_p, c_int]
lib.M_MouseWheel.restype = c_int

# 输入GBK
lib.M_KeyInputStringGBK.argtypes = [c_void_p, c_char_p, c_int]
lib.M_KeyInputStringGBK.restype = c_int

# 全局变量
h = None
x = None


class Yijianshu:
    def __init__(self):
        pass

    # 是否意usb键盘鼠标开启了
    def IsInit(self):
        result = False
        try:
            lenresponse = c_uint(256)
            response = create_string_buffer(256)
            r = lib.M_GetDevSn(h, pointer(lenresponse), response)
            result = (r == 0)
        except OSError:
            pass
        return result

    # 初始化函数
    def YijianshuInit(self, pid=None, vid=None):
        global h, x

        if h is not None and x is not None:
            logger.info("Init 易键鼠 ok")
            return True

        h = lib.M_Open_VidPid(0x612c, 0x1030)
        x = c_void_p(h)

        r = False
        if self.IsInit():
            logger.info("Init 易键鼠 ok")
            r = True
            self.ReleaseAllKey()
        else:
            h = lib.M_Open_VidPid(0xC216, 0x0301)
            x = c_void_p(h)

            if self.IsInit():
                logger.info("Init 易键鼠 ok")
                r = True
                self.ReleaseAllKey()
            else:
                logger.info("Init 易键鼠 err, 易键鼠没有加载成功")
                r = False

        return r

    # 初始化函数
    def Init(self):
        return self.YijianshuInit()

    # 释放所有按键
    def ReleaseAllKey(self):
        lib.M_ReleaseAllKey(h, x)

    # 疾跑右
    def JiPaoYou(self):
        lib.M_KeyDown2(h, VK_CODE["right_arrow"]), RanSleep(0.15)
        lib.M_KeyUp2(h, VK_CODE["right_arrow"]), RanSleep(0.15)
        lib.M_KeyDown2(h, VK_CODE["right_arrow"]), RanSleep(0.15)

    # 疾跑左
    def JiPaoZuo(self):
        lib.M_KeyDown2(h, VK_CODE["left_arrow"]), RanSleep(0.15)
        lib.M_KeyUp2(h, VK_CODE["left_arrow"]), RanSleep(0.15)
        lib.M_KeyDown2(h, VK_CODE["left_arrow"]), RanSleep(0.15)

    # 按下 上
    def DownSHANG(self):
        lib.M_KeyDown2(h, VK_CODE["up_arrow"])

    # 按下 下
    def DownXIA(self):
        lib.M_KeyDown2(h, VK_CODE["down_arrow"])

    # 按下 左
    def DownZUO(self):
        lib.M_KeyDown2(h, VK_CODE["left_arrow"])

    # 按下 右
    def DownYOU(self):
        lib.M_KeyDown2(h, VK_CODE["right_arrow"])

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
        lib.M_KeyUp2(h, VK_CODE["up_arrow"])

    # 弹起 下
    def UpXIA(self):
        lib.M_KeyUp2(h, VK_CODE["down_arrow"])

    # 弹起 左
    def UpZUO(self):
        lib.M_KeyUp2(h, VK_CODE["left_arrow"])

    # 弹起 右
    def UpYOU(self):
        lib.M_KeyUp2(h, VK_CODE["right_arrow"])

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
        lib.M_KeyDown2(h, key), KongjianSleep()
        lib.M_KeyUp2(h, key)

    # 按键 右
    def PressRight(self):
        lib.M_KeyDown2(h, VK_CODE["right_arrow"]), KongjianSleep()
        lib.M_KeyUp2(h, VK_CODE["right_arrow"])

    # 按键 左
    def PressLeft(self):
        lib.M_KeyDown2(h, VK_CODE["left_arrow"]), KongjianSleep()
        lib.M_KeyUp2(h, VK_CODE["left_arrow"])

    # 按键 上
    def PressUp(self):
        lib.M_KeyDown2(h, VK_CODE["up_arrow"]), KongjianSleep()
        lib.M_KeyUp2(h, VK_CODE["up_arrow"])

    # 按键 下
    def PressDown(self):
        lib.M_KeyDown2(h, VK_CODE["down_arrow"]), KongjianSleep()
        lib.M_KeyUp2(h, VK_CODE["down_arrow"])

    # 按键 x
    def PressX(self):
        lib.M_KeyDown2(h, VK_CODE["x"]), KongjianSleep()
        lib.M_KeyUp2(h, VK_CODE["x"])

    # 按键攻击
    def PressSkill(self, key, delay, afterdelay, thenpress=None, doublepress=False, issimpleattack=False):
        if issimpleattack:
            for i in range(10):
                lib.M_KeyDown2(h, key), RanSleep(0.05)
                lib.M_KeyUp2(h, key), RanSleep(0.05)
                RanSleep(0.05)

        else:
            lib.M_KeyDown2(h, key), RanSleep(delay)
            lib.M_KeyUp2(h, key), RanSleep(afterdelay)

            if thenpress is not None:
                lib.M_KeyDown2(h, thenpress), KongjianSleep()
                lib.M_KeyUp2(h, thenpress)

            if doublepress:
                def worker():
                    for i in range(10):
                        lib.M_KeyDown2(h, key), KongjianSleep()
                        lib.M_KeyUp2(h, key), KongjianSleep()

                threading.Thread(target=worker).start()

    # 按键 后跳
    def PressHouTiao(self):
        lib.M_KeyDown2(h, VK_CODE["down_arrow"]), KongjianSleep()
        lib.M_KeyDown2(h, VK_CODE["c"])

        lib.M_KeyUp2(h, VK_CODE["c"]), KongjianSleep()
        lib.M_KeyUp2(h, VK_CODE["down_arrow"])

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
            relativex, relativey = centrex - curx, centrey - cury
            if flag:
                logger.warning("当前鼠标坐标: (%d, %d) != (%d, %d)" % (curx, cury, centrex, centrey))
            else:
                flag = True
            lib.M_MoveR(h, int(relativex), int(relativey)), RanSleep(0.3)

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
            relativex, relativey = centrex - curx, centrey - cury
            if flag:
                logger.warning("当前鼠标坐标: (%d, %d) != (%d, %d)" % (curx, cury, centrex, centrey))
            else:
                flag = True
            lib.M_MoveR(h, int(relativex), int(relativey)), RanSleep(0.3)

    # 相对移动
    def MouseMoveR(self, x, y):
        (curx, cury) = GetCursorInfo()
        centrex, centrey = curx + x, cury + y

        flag = False
        # 修正
        while not self.IsMovedTo(centrex, centrey):
            (curx, cury) = GetCursorInfo()
            relativex, relativey = centrex - curx, centrey - cury
            if flag:
                logger.warning("当前鼠标坐标: (%d, %d) != (%d, %d)" % (curx, cury, centrex, centrey))
            else:
                flag = True
            lib.M_MoveR(h, int(relativex), int(relativey)), RanSleep(0.3)

    # 右键单击
    def MouseRightClick(self):
        lib.M_RightDown(h), KongjianSleep()
        lib.M_RightUp(h)

    # 左键单击
    def MouseLeftClick(self):
        lib.M_LeftDown(h), KongjianSleep()
        lib.M_LeftUp(h)

    # shift + 左按键
    def ShiftLeft(self):
        lib.M_KeyDown2(h, VK_CODE["left_shift"]), KongjianSleep()
        lib.M_LeftDown(h), KongjianSleep()
        lib.M_LeftUp(h), KongjianSleep()
        lib.M_KeyUp2(h, VK_CODE["left_shift"])

    # shift + 右按键
    def ShiftRight(self):
        lib.M_KeyDown2(h, VK_CODE["left_shift"]), KongjianSleep()
        lib.M_RightDown(h), KongjianSleep()
        lib.M_RightUp(h), KongjianSleep()
        lib.M_KeyUp2(h, VK_CODE["left_shift"])

    # 左键按下
    def MouseLeftDown(self):
        lib.M_LeftDown(h)

    # 左键弹出
    def MouseLeftUp(self):
        lib.M_LeftUp(h)

    # 滚轮
    def MouseWheel(self, v):
        lib.M_MouseWheel(h, v)

    # 输入gbk
    def KeyInputGBK(self, s):
        ins = bytes(s, "gb2312")
        lib.M_KeyInputStringGBK(h, ins, len(ins))

    # 删除所有文字
    def DeleteAll(self):
        lib.M_KeyDown2(h, VK_CODE['backspace']), RanSleep(2)
        lib.M_KeyUp2(h, VK_CODE['backspace']), RanSleep(0.05)


def main():
    InitLog()

    anjian = Yijianshu()

    if not anjian.Init():
        logger.warning("易键鼠初始化失败")
        sys.exit()

    GameWindowToTop()

    anjian.MouseMoveTo(205, 434)


if __name__ == '__main__':
    main()
