import os
import sys
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

import time
import win32gui
import random
from superai.pathsetting import GetYiLib
from ctypes import *
from superai.common import InitLog, GameWindowToTop

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

# 输入GBK
lib.M_KeyInputStringGBK.argtypes = [c_void_p, c_char_p, c_int]
lib.M_KeyInputStringGBK.restype = c_int

# 输入unicode
lib.M_KeyInputStringUnicode.argtypes = [c_void_p, c_char_p, c_int]
lib.M_KeyInputStringUnicode.restype = c_int


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


# 是否意usb键盘鼠标开启了
def IsInit():
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
def YijianshuInit(pid=None, vid=None):
    global h, x

    h = lib.M_Open_VidPid(0x612c, 0x1030)
    x = c_void_p(h)

    r = False
    if IsInit():
        logger.info("Init 易键鼠 ok")
        r = True
        ReleaseAllKey()
    else:
        h = lib.M_Open_VidPid(0000, 0000)
        x = c_void_p(h)

        if IsInit():
            logger.info("Init 易键鼠 ok")
            r = True
            ReleaseAllKey()
        else:
            logger.info("Init 易键鼠 err, 易键鼠没有加载成功")
            r = False

    return r


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


# 是否移动到目的位置
def IsMovedTo(x, y):
    _, _, (curx, cury) = win32gui.GetCursorInfo()
    return (curx, cury) == (x, y)


# 相对移动鼠标
def MouseMoveTo(x, y):
    hwnd = win32gui.FindWindow("地下城与勇士", "地下城与勇士")

    try:
        centrex, centrey = win32gui.ClientToScreen(hwnd, (int(x), int(y)))
    except:
        return

    flag = False
    # 修正
    while not IsMovedTo(centrex, centrey):
        _, _, (curx, cury) = win32gui.GetCursorInfo()
        relativex, relativey = centrex - curx, centrey - cury
        if flag:
            logger.warning("当前鼠标坐标: (%d, %d) != (%d, %d)" % (curx, cury, centrex, centrey))
        else:
            flag = True
        lib.M_MoveR(h, int(relativex), int(relativey)), RanSleep(0.3)


# 相对移动鼠标,游戏登录界面
def MouseMoveToLogin(x, y):
    hwnd = win32gui.FindWindow("TWINCONTROL", "地下城与勇士登录程序")

    try:
        centrex, centrey = win32gui.ClientToScreen(hwnd, (int(x), int(y)))
    except:
        return

    flag = False
    # 修正
    while not IsMovedTo(centrex, centrey):
        _, _, (curx, cury) = win32gui.GetCursorInfo()
        relativex, relativey = centrex - curx, centrey - cury
        if flag:
            logger.warning("当前鼠标坐标: (%d, %d) != (%d, %d)" % (curx, cury, centrex, centrey))
        else:
            flag = True
        lib.M_MoveR(h, int(relativex), int(relativey)), RanSleep(0.3)


# 相对移动
def MouseMoveR(x, y):
    _, _, (curx, cury) = win32gui.GetCursorInfo()
    centrex, centrey = curx + x, cury + y

    flag = False
    # 修正
    while not IsMovedTo(centrex, centrey):
        _, _, (curx, cury) = win32gui.GetCursorInfo()
        relativex, relativey = centrex - curx, centrey - cury
        if flag:
            logger.warning("当前鼠标坐标: (%d, %d) != (%d, %d)" % (curx, cury, centrex, centrey))
        else:
            flag = True
        lib.M_MoveR(h, int(relativex), int(relativey)), RanSleep(0.3)


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


# shift + 左按键
def ShiftLeft():
    lib.M_KeyDown2(h, VK_CODE["left_shift"]), KongjianSleep()
    lib.M_LeftDown(h), KongjianSleep()
    lib.M_LeftUp(h),  KongjianSleep()
    lib.M_KeyUp2(h, VK_CODE["left_shift"])

# shift + 右按键
def ShiftRight():
    lib.M_KeyDown2(h, VK_CODE["left_shift"]), KongjianSleep()
    lib.M_RightDown(h), KongjianSleep()
    lib.M_RightUp(h), KongjianSleep()
    lib.M_KeyUp2(h, VK_CODE["left_shift"])

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
def KeyInputString(s):
    ins = bytes(s, "utf8")
    lib.M_KeyInputString(h, ins, len(s))


# 输入gbk
def KeyInputGBK(s):
    ins = bytes(s, "gb2312")
    lib.M_KeyInputStringGBK(h, ins, len(s))


# 删除所有文字
def DeleteAll():
    lib.M_KeyDown2(h, VK_CODE['backspace']), RanSleep(2)
    lib.M_KeyUp2(h, VK_CODE['backspace']), RanSleep(0.05)


def main():
    InitLog()
    if not YijianshuInit():
        sys.exit()

    # GameWindowToTop()
    # RanSleep(2)

    MouseMoveR(100, 100)

    # DeleteAll()
    # MouseMoveTo(537, 468)
    # RanSleep(3.0)
    # KeyInputString("GGC88zyj")
    # GameWindowToTop()
    # MouseMoveTo(329, 335)


if __name__ == "__main__":
    main()
