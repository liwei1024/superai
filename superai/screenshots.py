import os
import sys

import numpy as np
import win32gui
from cv2 import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)


def WindowCaptureToFile(windowClassName, windowName, captureDir, dx=0, dy=0, dw=0, dh=0, defer=None):
    pass


def WindowCaptureToMem(windowClassName, windowName, dx=0, dy=0, dw=0, dh=0, defer=None):
    hwnd = win32gui.FindWindow(windowClassName, windowName)

    if hwnd == 0:
        return None

    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bot - top
    if dw != 0:
        w = dw
    if dh != 0:
        h = dh



def main():

    # img = WindowCaptureToMem("TWINCONTROL", "WeGame")
    #
    # cv2.imshow('1', img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    from PIL import ImageGrab
    import win32gui

    hwnd = win32gui.FindWindow("TWINCONTROL", "WeGame")

    win32gui.SetForegroundWindow(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)
    img = ImageGrab.grab(bbox)
    img.show()


if __name__ == "__main__":
    main()
