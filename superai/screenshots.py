import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)


def WindowCaptureToFile(windowClassName, windowName, captureDir, dx=0, dy=0, dw=0, dh=0, defer=None):
    pass


def WindowCaptureToMem(windowClassName, windowName, dx=0, dy=0, dw=0, dh=0, defer=None):
    pass


def main():

    import win32gui
    hwnd_title = dict()

    def get_all_hwnd(hwnd, mouse):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

    win32gui.EnumWindows(get_all_hwnd, 0)

    for h, t in hwnd_title.items():
        if t is not "":
            print(h, t)

    from PyQt5.QtWidgets import QApplication

    import win32gui
    import sys

    hwnd = win32gui.FindWindow("TWINCONTROL", "WeGame")
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen()
    img = screen.grabWindow(2690140).toImage()
    img.save("screenshot1.jpg")


if __name__ == "__main__":
    main()
