import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

import cv2
import numpy as np
import win32api
import win32con
import win32gui
import win32ui

import datetime

from superai.defer import defer


# http://timgolden.me.uk/pywin32-docs/contents.html (官方文档)


# https://www.quora.com/How-can-we-take-screenshots-using-Python-in-Windows
@defer
def DesktopCaptureToFile(captureDir, defer):
    hdesktop = win32gui.GetDesktopWindow()
    w = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    h = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    # 截图什么矩阵 (w,h 宽度和高度) (left,top, 距离左边和上面多少)
    # print("左: {} 上: {} 分辨率: {}x{}".format(left, top, w, h))

    desktopDC = win32gui.GetWindowDC(hdesktop)
    defer(lambda: (win32gui.ReleaseDC(hdesktop, desktopDC)))

    imgDC = win32ui.CreateDCFromHandle(desktopDC)
    defer(lambda: (imgDC.DeleteDC()))

    memDC = imgDC.CreateCompatibleDC()
    defer(lambda: (memDC.DeleteDC()))

    bitmap = win32ui.CreateBitmap()
    defer(lambda: (win32gui.DeleteObject(bitmap.GetHandle())))

    bitmap.CreateCompatibleBitmap(imgDC, w, h)
    memDC.SelectObject(bitmap)
    memDC.BitBlt((0, 0), (w, h), imgDC, (left, top), win32con.SRCCOPY)

    bitmap.SaveBitmapFile(memDC, '{}/screenshot{}.bmp'.format(captureDir,
                                                              datetime.datetime.now().strftime("%Y%m%d%H%M%S")))


# https://stackoverflow.com/questions/3586046/fastest-way-to-take-a-screenshot-with-python-on-windows
@defer
def WindowCaptureToFile(windowClassName, windowName, captureDir, defer):
    hwnd = win32gui.FindWindow(windowClassName, windowName)
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bot - top
    # print("窗口 左上角 x:{} y:{} 右下角 x:{} y:{}, 分辨率: {}x{}".format(left, top, right, bot, w, h))

    windowDC = win32gui.GetWindowDC(hwnd)
    defer(lambda: (win32gui.ReleaseDC(hwnd, windowDC)))

    imgDC = win32ui.CreateDCFromHandle(windowDC)
    defer(lambda: (imgDC.DeleteDC()))

    memDC = imgDC.CreateCompatibleDC()
    defer(lambda: (memDC.DeleteDC()))

    bitmap = win32ui.CreateBitmap()
    defer(lambda: (win32gui.DeleteObject(bitmap.GetHandle())))

    bitmap.CreateCompatibleBitmap(imgDC, w, h)
    memDC.SelectObject(bitmap)
    memDC.BitBlt((0, 0), (w, h), imgDC, (0, 0), win32con.SRCCOPY)

    bitmap.SaveBitmapFile(memDC,
                          '{}/screenshot{}.bmp'.format(captureDir, datetime.datetime.now().strftime("%Y%m%d%H%M%S")))


# https://stackoverflow.com/questions/49511753/python-byte-image-to-numpy-array-using-opencv
@defer
def WindowCaptureToMem(windowClassName, windowName, dx=0, dy=0, dw=0, dh=0, defer=None):
    hwnd = win32gui.FindWindow(windowClassName, windowName)
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bot - top

    windowDC = win32gui.GetWindowDC(hwnd)
    defer(lambda: (win32gui.ReleaseDC(hwnd, windowDC)))

    imgDC = win32ui.CreateDCFromHandle(windowDC)
    defer(lambda: (imgDC.DeleteDC()))

    memDC = imgDC.CreateCompatibleDC()
    defer(lambda: (memDC.DeleteDC()))

    bitmap = win32ui.CreateBitmap()
    defer(lambda: (win32gui.DeleteObject(bitmap.GetHandle())))

    if dw != 0 or dh != 0:
        w = dw
        h = dh

    bitmap.CreateCompatibleBitmap(imgDC, w, h)
    memDC.SelectObject(bitmap)

    # 从dx, dy 处拷贝 w,h 的位图,到申请的w,h大小的空间的0,0处开始拷贝
    memDC.BitBlt((0, 0), (w, h), imgDC, (dx, dy), win32con.SRCCOPY)

    npbytes = np.frombuffer(bitmap.GetBitmapBits(True), dtype='uint8')
    npbytes.shape = (h, w, 4)

    img = cv2.cvtColor(npbytes, cv2.COLOR_BGRA2BGR)

    return img


def main():
    # DesktopCaptureToFile("E:/win/tmp/capture")

    WindowCaptureToFile("地下城与勇士", "地下城与勇士", "E:/win/tmp/capture")

    # img = WindowCaptureToMem("地下城与勇士", "地下城与勇士")
    # cv2.imshow('my img', img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
