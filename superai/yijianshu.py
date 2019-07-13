import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import time
import win32con
import win32gui
import random

from ctypes import *

from superai.common import Log
from superai.vkcode import *

if os.path.exists("c:/win/superai/dll/"):
    lib = CDLL("c:/win/superai/dll/msdk.dll", RTLD_GLOBAL)
else:
    lib = CDLL("E:/win/reference/project/superai/dll/msdk.dll", RTLD_GLOBAL)

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
lib.M_MoveR2.argtypes = [c_void_p, c_int, c_int]
lib.M_MoveR2.restype = c_int

# 移动鼠标到指定位置
lib.M_MoveTo2.argtypes = [c_void_p, c_int, c_int]
lib.M_MoveTo2.restype = c_int

# 获取鼠标位置, GetCurosPos
lib.M_GetCurrMousePos2.argtypes = [POINTER(c_int)]
lib.M_GetCurrMousePos2.restype = c_int


# 随机时间sleep
def RanSleep(t):
    ran = random.uniform(0, 0.005)
    if random.uniform(0, 1) < 0.5:
        if t - ran > 0.0:
            t = t - ran
        time.sleep(t)
    else:
        t = t + ran
        time.sleep(t)


# 全局变量
h = None
x = None


# 初始化函数
def YijianshuInit() -> bool:
    global h
    global x

    h = lib.M_Open_VidPid(0x612c, 0x1030)
    x = c_void_p(h)
    return h != 0


def ReleaseAllKey():
    lib.M_ReleaseAllKey(h, x)


def JiPaoYou():
    RanSleep(0.15)
    lib.M_KeyDown2(h, VK_CODE["right_arrow"])
    RanSleep(0.15)
    lib.M_KeyUp2(h, VK_CODE["right_arrow"])
    RanSleep(0.15)
    lib.M_KeyDown2(h, VK_CODE["right_arrow"])
    RanSleep(0.15)


def JiPaoZuo():
    RanSleep(0.15)
    lib.M_KeyDown2(h, VK_CODE["left_arrow"])
    RanSleep(0.15)
    lib.M_KeyUp2(h, VK_CODE["left_arrow"])
    RanSleep(0.15)
    lib.M_KeyDown2(h, VK_CODE["left_arrow"])
    RanSleep(0.15)


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


def PressF12():
    lib.M_KeyDown2(h, VK_CODE["F12"])
    RanSleep(0.1)
    lib.M_KeyUp2(h, VK_CODE["F12"])


def PressRight():
    lib.M_KeyDown2(h, VK_CODE["right_arrow"])
    RanSleep(0.1)
    lib.M_KeyUp2(h, VK_CODE["right_arrow"])


def PressLeft():
    lib.M_KeyDown2(h, VK_CODE["left_arrow"])
    RanSleep(0.1)
    lib.M_KeyUp2(h, VK_CODE["left_arrow"])


def PressX():
    lib.M_KeyDown2(h, VK_CODE["x"])
    RanSleep(0.1)
    lib.M_KeyUp2(h, VK_CODE["x"])


def PressSkill(key, delay, afterdelay):
    lib.M_KeyDown2(h, key)
    RanSleep(delay)
    lib.M_KeyUp2(h, key)
    RanSleep(afterdelay)


def PressHouTiao():
    lib.M_KeyDown2(h, VK_CODE["down_arrow"])
    RanSleep(0.1)
    lib.M_KeyDown2(h, VK_CODE["c"])
    RanSleep(0.1)
    lib.M_KeyUp2(h, VK_CODE["c"])
    lib.M_KeyUp2(h, VK_CODE["down_arrow"])


def main():
    if YijianshuInit():
        Log("Init 易键鼠 ok")
    else:
        Log("Init 易键鼠 err")
        exit(0)

    global h
    global x

    # hwnd = win32gui.FindWindow("地下城与勇士", "地下城与勇士")
    # win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 800, 600,
    #                       win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    # win32gui.SetForegroundWindow(hwnd)


if __name__ == "__main__":
    main()
