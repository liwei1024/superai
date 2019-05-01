import win32api
import win32con
import win32gui
import win32ui

import datetime
from ctypes import windll


# http://timgolden.me.uk/pywin32-docs/contents.html (官方文档)

# https://www.quora.com/How-can-we-take-screenshots-using-Python-in-Windows
def DesctopCapture():
    hdesktop = win32gui.GetDesktopWindow()
    # 截图什么矩阵 (width,height 宽度和高度) (left,top, 距离左边和上面多少)
    w = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    h = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    print("左: {} 上: {}".format(left, top))
    print("截图 分辨率: {}x{}".format(w, h))

    desktopDC = win32gui.GetWindowDC(hdesktop)
    imgDC = win32ui.CreateDCFromHandle(desktopDC)
    memDC = imgDC.CreateCompatibleDC()

    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(imgDC, w, h)
    memDC.SelectObject(screenshot)
    memDC.BitBlt((0, 0), (w, h), imgDC, (left, top), win32con.SRCCOPY)

    screenshot.SaveBitmapFile(memDC, 'c:\\WINDOWS\\Temp\\screenshot{}.bmp'.format(
        datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
    memDC.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())


# https://stackoverflow.com/questions/3586046/fastest-way-to-take-a-screenshot-with-python-on-windows
def WindowCapture():
    hwnd = win32gui.FindWindow("地下城与勇士", "地下城与勇士")
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bot - top
    print("DNF窗口 左上角 x:{} y:{} 右下角 x:{} y:{}".format(left, top, right, bot))
    print("DNF窗口 分辨率: {}x{} ".format(w, h))

    windowDC = win32gui.GetWindowDC(hwnd)
    imgDC = win32ui.CreateDCFromHandle(windowDC)
    memDC = imgDC.CreateCompatibleDC()

    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(imgDC, w, h)
    memDC.SelectObject(screenshot)
    memDC.BitBlt((0, 0), (w, h), imgDC, (0, 0), win32con.SRCCOPY)
    screenshot.SaveBitmapFile(memDC, 'c:\\WINDOWS\\Temp\\screenshot{}.bmp'.format(
        datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
    memDC.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())


def main():
    # GlobalCapture()

    WindowCapture()


if __name__ == "__main__":
    main()
