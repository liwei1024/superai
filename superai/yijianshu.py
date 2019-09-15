import os
import sys
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

import time
import win32gui
import random

from ctypes import *
from superai.common import InitLog, GameWindowToTop

from superai.vkcode import *

if os.path.exists("c:/win/superai/dll/"):
    lib = CDLL("c:/win/superai/dll/msdk.dll", RTLD_GLOBAL)
elif os.path.exists("D:/win/superai/dll/"):
    lib = CDLL("D:/win/superai/dll/msdk.dll", RTLD_GLOBAL)
else:
    lib = CDLL("D:/win/reference/project/superai/dll/msdk.dll", RTLD_GLOBAL)

# 键盘

# 打开
lib.M_Open.argtypes = [c_int]
lib.M_Open.restype = c_void_p

# 以特殊vid pid 打开
lib.M_Open_VidPid.argtypes = [c_int, c_int]
lib.M_Open_VidPid.restype = c_void_p

# 关闭
lib.M_Close.argtypes = [c_void_p]
lib.M_Close.restype = c_int

# 按下, 50~80ms 弹起
lib.M_KeyPress2.argtypes = [c_void_p, c_int, c_int]
lib.M_KeyPress2.restype = c_int

# 按下
lib.M_KeyDown2.argtypes = [c_void_p, c_int]
lib.M_KeyDown2.restype = c_int

# 弹起
lib.M_KeyUp2.argtypes = [c_void_p, c_int]
lib.M_KeyUp2.restype = c_int

# 弹起所有按键
lib.M_ReleaseAllKey.argtypes = [c_void_p]
lib.M_KeyUp2.restype = c_int

# 读取按键状态
lib.M_KeyState2.argtypes = [c_void_p, c_int]
lib.M_KeyState2.restype = c_int

# 输入支持GBK
lib.M_KeyInputStringGBK.argtypes = [c_void_p, c_void_p, c_int]
lib.M_KeyInputStringGBK.restype = c_int

# 输入支持Unicode
lib.M_KeyInputStringUnicode.argtypes = [c_void_p, c_void_p, c_int]
lib.M_KeyInputStringUnicode.restype = c_int

# 鼠标

# 左键单击
lib.M_LeftClick.argtypes = [c_void_p, c_int]
lib.M_LeftClick.restype = c_int

# 左键双击
lib.M_LeftDoubleClick.argtypes = [c_void_p, c_int]
lib.M_LeftDoubleClick.restype = c_int

# 按下左键不弹起
lib.M_LeftDown.argtypes = [c_void_p]
lib.M_LeftDown.restype = c_int

# 弹起左键
lib.M_LeftUp.argtypes = [c_void_p]
lib.M_LeftUp.restype = c_int

# 右键单击
lib.M_RightClick.argtypes = [c_void_p, c_int]
lib.M_RightClick.restype = c_int

# 按下右键不弹起
lib.M_RightDown.argtypes = [c_void_p]
lib.M_RightDown.restype = c_int

# 弹起右键
lib.M_RightUp.argtypes = [c_void_p]
lib.M_RightUp.restype = c_int
#
# # 鼠标移动到原点
lib.M_ResetMousePos.argtypes = [c_void_p]
lib.M_ResetMousePos.restype = c_int

# 当前相对位置移动鼠标
lib.M_MoveR.argtypes = [c_void_p, c_int, c_int]
lib.M_MoveR.restype = c_int

# 移动鼠标到指定位置
lib.M_MoveTo.argtypes = [c_void_p, c_int, c_int]
lib.M_MoveTo.restype = c_int

# 当前相对位置移动鼠标
lib.M_MoveR2.argtypes = [c_void_p, c_int, c_int]
lib.M_MoveR2.restype = c_int

# 移动鼠标到指定位置
lib.M_MoveTo2.argtypes = [c_void_p, c_int, c_int]
lib.M_MoveTo2.restype = c_int

# 获取鼠标位置, GetCurosPos
lib.M_GetCurrMousePos2.argtypes = [POINTER(c_int)]
lib.M_GetCurrMousePos2.restype = c_int

# 设置分辨率
lib.M_ResolutionUsed.argtypes = [c_void_p, c_int, c_int]
lib.M_ResolutionUsed.restype = c_int

# 移动鼠标到指定位置 (没有轨迹)
lib.M_MoveTo3.argtypes = [c_void_p, c_int, c_int]
lib.M_MoveTo3.restype = c_int

# 滚轮 (向上正,向下负)
lib.M_MouseWheel.argtypes = [c_void_p, c_int]
lib.M_MouseWheel.restype = c_int

# 输入 ascii
lib.M_KeyInputString.argtypes = [c_void_p, c_char_p, c_int]
lib.M_KeyInputString.restype = c_int


# 随机时间sleep
def RanSleep(t):
    t = random.uniform(t - 0.005, t + 0.005)
    if t < 0:
        t = 0

    time.sleep(t)


# 操作控件后的sleep
def KongjianSleep():
    RanSleep(0.2)


# 打开某个栏的sleep
def LanSleep():
    RanSleep(0.3)


# 全局变量
h = None
x = None


# 初始化函数
def YijianshuInit():
    global h
    global x

    h = lib.M_Open_VidPid(0x612c, 0x1030)
    x = c_void_p(h)

    if h != 0:
        logger.info("Init 易键鼠 ok")
    else:
        logger.info("Init 易键鼠 err")
        exit(0)

    ReleaseAllKey()


def ReleaseAllKey():
    lib.M_ReleaseAllKey(h, x)


def JiPaoYou():
    lib.M_KeyDown2(h, VK_CODE["right_arrow"]), RanSleep(0.15)
    lib.M_KeyUp2(h, VK_CODE["right_arrow"]), RanSleep(0.15)
    lib.M_KeyDown2(h, VK_CODE["right_arrow"]), RanSleep(0.15)


def JiPaoZuo():
    lib.M_KeyDown2(h, VK_CODE["left_arrow"]), RanSleep(0.15)
    lib.M_KeyUp2(h, VK_CODE["left_arrow"]), RanSleep(0.15)
    lib.M_KeyDown2(h, VK_CODE["left_arrow"]), RanSleep(0.15)


# 八方位移动
def DownSHANG():
    lib.M_KeyDown2(h, VK_CODE["up_arrow"])


def DownXIA():
    lib.M_KeyDown2(h, VK_CODE["down_arrow"])


def DownZUO():
    lib.M_KeyDown2(h, VK_CODE["left_arrow"])


def DownYOU():
    lib.M_KeyDown2(h, VK_CODE["right_arrow"])


def DownZUOSHANG():
    DownZUO()
    DownSHANG()


def DownZUOXIA():
    DownZUO()
    DownXIA()


def DownYOUSHANG():
    DownYOU()
    DownSHANG()


def DownYOUXIA():
    DownYOU()
    DownXIA()


def UpSHANG():
    lib.M_KeyUp2(h, VK_CODE["up_arrow"])


def UpXIA():
    lib.M_KeyUp2(h, VK_CODE["down_arrow"])


def UpZUO():
    lib.M_KeyUp2(h, VK_CODE["left_arrow"])


def UpYOU():
    lib.M_KeyUp2(h, VK_CODE["right_arrow"])


def UpZUOSHANG():
    UpZUO()
    UpSHANG()


def UpZUOXIA():
    UpZUO()
    UpXIA()


def UpYOUSHANG():
    UpYOU()
    UpSHANG()


def UpYOUXIA():
    UpYOU()
    UpXIA()


def PressKey(key):
    lib.M_KeyDown2(h, key), KongjianSleep()
    lib.M_KeyUp2(h, key)


def PressRight():
    lib.M_KeyDown2(h, VK_CODE["right_arrow"]), KongjianSleep()
    lib.M_KeyUp2(h, VK_CODE["right_arrow"])


def PressLeft():
    lib.M_KeyDown2(h, VK_CODE["left_arrow"]), KongjianSleep()
    lib.M_KeyUp2(h, VK_CODE["left_arrow"])


def PressUp():
    lib.M_KeyDown2(h, VK_CODE["up_arrow"]), KongjianSleep()
    lib.M_KeyUp2(h, VK_CODE["up_arrow"])


def PressDown():
    lib.M_KeyDown2(h, VK_CODE["down_arrow"]), KongjianSleep()
    lib.M_KeyUp2(h, VK_CODE["down_arrow"])


def PressX():
    lib.M_KeyDown2(h, VK_CODE["x"]), KongjianSleep()
    lib.M_KeyUp2(h, VK_CODE["x"])


def PressSkill(key, delay, afterdelay, thenpress=None, doublepress=False, issimpleattack=False):

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


def PressHouTiao():
    lib.M_KeyDown2(h, VK_CODE["down_arrow"]), KongjianSleep()
    lib.M_KeyDown2(h, VK_CODE["c"])

    lib.M_KeyUp2(h, VK_CODE["c"]), KongjianSleep()
    lib.M_KeyUp2(h, VK_CODE["down_arrow"])


# 相对移动鼠标
def MouseMoveTo(x, y):
    hwnd = win32gui.FindWindow("地下城与勇士", "地下城与勇士")
    _, _, (curx, cury) = win32gui.GetCursorInfo()
    centrex, centrey = win32gui.ClientToScreen(hwnd, (int(x), int(y)))
    relativex = centrex - curx
    relativey = centrey - cury

    # if x < 2:
    #     relativex = random.uniform(relativex, relativex + 2)
    # else:
    #     relativex = random.uniform(relativex - 2, relativex + 2)
    #
    # if y < 2:
    #     relativey = random.uniform(relativey, relativey + 2)
    # else:
    #     relativey = random.uniform(relativey - 2, relativey + 2)

    lib.M_MoveR(h, int(relativex), int(relativey))


# 相对移动
def MouseMoveR(x, y):
    lib.M_MoveR(h, int(x), int(y))


# 右键单击
def MouseRightClick():
    lib.M_RightDown(h), KongjianSleep()
    lib.M_RightUp(h)


# 左键单击
def MouseLeftClick():
    lib.M_LeftDown(h), KongjianSleep()
    lib.M_LeftUp(h)


# 左键持续按键
def MouseLeftDownFor(t):
    lib.M_LeftDown(h), RanSleep(t)
    lib.M_LeftUp(h)


# 右键持续按键
def MouseRightDownFor(t):
    lib.M_RightDown(h), RanSleep(t)
    lib.M_RightUp(h)


# 左键双击
def MouseLeftDoubleClick():
    MouseLeftClick(), KongjianSleep()
    MouseLeftClick()


# 左键按下
def MouseLeftDown():
    lib.M_LeftDown(h)


# 左键弹出
def MouseLeftUp():
    lib.M_LeftUp(h)


# 滚轮
def MouseWheel(v):
    lib.M_MouseWheel(h, v)


# 输入ascii
def KeyInputStgring(s):
    ins = bytes(s, "utf8")
    lib.M_KeyInputString(h, ins, len(s))


def main():
    InitLog()
    YijianshuInit()

    # RanSleep(3.0)
    # KeyInputStgring("GGC88zyj")
    # GameWindowToTop()
    # MouseMoveTo(329, 335)


if __name__ == "__main__":
    main()
