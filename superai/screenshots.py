import sys
import os
import time

import win32con
import win32ui

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.defer import defer

import logging

logger = logging.getLogger(__name__)

import cv2
import numpy as np
import win32gui
import datetime


@defer
def WindowCaptureToFile(windowClassName, windowName, captureDir, dx=0, dy=0, dw=0, dh=0, defer=None):
    hwnd = win32gui.FindWindow(windowClassName, windowName)
    if hwnd == 0:
        return None
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bot - top

    if dx != 0:
        left = left + dx

    if dy != 0:
        top = top + dy

    if dw != 0:
        w = dw

    if dh != 0:
        h = dh

    hdesktop, desktopDC, imgDC, memDC, bitmap = None, None, None, None, None
    try:
        hdesktop = win32gui.GetDesktopWindow()
        desktopDC = win32gui.GetWindowDC(hdesktop)
        imgDC = win32ui.CreateDCFromHandle(desktopDC)
        memDC = imgDC.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(imgDC, w, h)
        oldmap = memDC.SelectObject(bitmap)
        memDC.BitBlt((0, 0), (w, h), imgDC, (left, top), win32con.SRCCOPY)
        filename = '{}/screenshot{}.png'.format(captureDir, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        bitmap.SaveBitmapFile(memDC, filename)
        memDC.SelectObject(oldmap)
        return filename
    except:
        logger.warning("截图函数发生异常")
        return ""

    finally:
        try:
            if bitmap:
                win32gui.DeleteObject(bitmap.GetHandle())
        except:
            logger.warning("win32gui.DeleteObject 发生异常")

        try:
            if memDC:
                memDC.DeleteDC()
        except:
            logger.warning("memDC.DeleteDC() 发生异常")

        try:
            if imgDC:
                imgDC.DeleteDC()
        except:
            logger.warning("imgDC.DeleteDC() 发生异常")

        try:
            if desktopDC:
                win32gui.ReleaseDC(hdesktop, desktopDC)
        except:
            logger.warning("win32gui.ReleaseDC() 发生异常")


@defer
def WindowCaptureToMem(windowClassName, windowName, dx=0, dy=0, dw=0, dh=0, defer=None):
    hwnd = win32gui.FindWindow(windowClassName, windowName)
    if hwnd == 0:
        return None
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bot - top

    if dx != 0:
        left = left + dx

    if dy != 0:
        top = top + dy

    if dw != 0:
        w = dw

    if dh != 0:
        h = dh

    hdesktop, desktopDC, imgDC, memDC, bitmap = None, None, None, None, None
    try:
        hdesktop = win32gui.GetDesktopWindow()
        desktopDC = win32gui.GetWindowDC(hdesktop)
        imgDC = win32ui.CreateDCFromHandle(desktopDC)
        memDC = imgDC.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(imgDC, w, h)
        oldmap = memDC.SelectObject(bitmap)
        memDC.BitBlt((0, 0), (w, h), imgDC, (left, top), win32con.SRCCOPY)
        npbytes = np.frombuffer(bitmap.GetBitmapBits(True), dtype='uint8')
        npbytes.shape = (h, w, 4)
        memDC.SelectObject(oldmap)
        return cv2.cvtColor(npbytes, cv2.COLOR_BGRA2BGR)
    except:
        logger.warning("截图函数发生异常")
        return np.zeros((h, w, 3), dtype=np.uint8)

    finally:
        try:
            if bitmap:
                win32gui.DeleteObject(bitmap.GetHandle())
        except:
            logger.warning("win32gui.DeleteObject 发生异常")

        try:
            if memDC:
                memDC.DeleteDC()
        except:
            logger.warning("memDC.DeleteDC() 发生异常")

        try:
            if imgDC:
                imgDC.DeleteDC()
        except:
            logger.warning("imgDC.DeleteDC() 发生异常")

        try:
            if desktopDC:
                win32gui.ReleaseDC(hdesktop, desktopDC)
        except:
            logger.warning("win32gui.ReleaseDC() 发生异常")


def main():
    # img = WindowCaptureToMem("TWINCONTROL", "WeGame")
    # cv2.imshow('my img', img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    img = WindowCaptureToMem("地下城与勇士", "地下城与勇士")

    cv2.imshow('my img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
