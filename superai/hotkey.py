import os
import sys

import win32api

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import threading

import ctypes, win32con, ctypes.wintypes, win32gui
import time

from superai.common import HideConsole
from superai.vkcode import VK_CODE

EXIT = False


# class Hotkey(threading.Thread):
#     def run(self):
#         global EXIT
#         user32 = ctypes.windll.user32
#         if not user32.RegisterHotKey(None, 99, win32con.MOD_ALT, VK_CODE['k']):
#             raise RuntimeError
#         try:
#             msg = ctypes.wintypes.MSG()
#             print(msg)
#             while user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
#                 if msg.message == win32con.WM_HOTKEY:
#                     if msg.wParam == 99:
#                         EXIT = True
#                         return
#                 user32.TranslateMessage(ctypes.byref(msg))
#                 user32.DispatchMessageA(ctypes.byref(msg))
#         finally:
#             user32.UnregisterHotKey(None, 1)


def Hotkey():
    while True:
        statealt = win32api.GetAsyncKeyState(VK_CODE['alt'])
        statek = win32api.GetAsyncKeyState(VK_CODE['q'])
        global EXIT
        if statealt != 0 and statek != 0:
            EXIT = True
            break
        time.sleep(0.005)


def main():
    # HideConsole()
    t = threading.Thread(target=Hotkey)
    t.start()

    while not EXIT:
        time.sleep(1.0)
        print('running')


if __name__ == '__main__':
    main()
