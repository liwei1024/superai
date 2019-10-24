import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

import cv2
import numpy as np
import win32gui
import datetime
from PIL import ImageGrab


def WindowCaptureToFile(windowClassName, windowName, captureDir, dx=0, dy=0, dw=0, dh=0):
    hwnd = win32gui.FindWindow(windowClassName, windowName)
    if hwnd == 0:
        return None
    left, top, right, bot = win32gui.GetWindowRect(hwnd)

    if dx != 0:
        left = left + dx

    if dy != 0:
        top = top + dy

    if dw != 0:
        right = left + dw

    if dh != 0:
        bot = top + dh

    img = ImageGrab.grab((left, top, right, bot),  all_screens=True)

    filename = '{}/screenshot{}.png'.format(captureDir, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    img.save(filename)
    return filename


def WindowCaptureToMem(windowClassName, windowName, dx=0, dy=0, dw=0, dh=0):
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
        right = left + dw

    if dh != 0:
        bot = top + dh

    img = ImageGrab.grab((left, top, right, bot), all_screens=True)
    img = np.array(img)

    try:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    except TypeError:
        img = np.zeros((h, w, 3), dtype=np.uint8)

    return img


def main():
    # img = WindowCaptureToMem("TWINCONTROL", "WeGame")
    # cv2.imshow('my img', img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    img = WindowCaptureToMem("TWINCONTROL", "WeGame")

    cv2.imshow('my img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
