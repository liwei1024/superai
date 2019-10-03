import ctypes
import logging

import coloredlogs
import win32con
import win32com.client
import win32gui


def InitLog():
    coloredlogs.DEFAULT_FIELD_STYLES['filename'] = {'color': 'blue'}
    coloredlogs.DEFAULT_FIELD_STYLES['lineno'] = {'color': 'blue'}
    coloredlogs.DEFAULT_FIELD_STYLES['levelname'] = {'color': 'magenta'}
    fmt = '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    datefmt = '%Y-%m-%d:%H:%M:%S'
    coloredlogs.install(fmt=fmt, datefmt=datefmt, level=logging.DEBUG)


# 置顶游戏窗口
def GameWindowToTop():
    hwnd = win32gui.FindWindow("地下城与勇士", "地下城与勇士")
    # win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 800, 600,
    #                       win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    if hwnd != 0:
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')

        try:
            win32gui.SetForegroundWindow(hwnd)
        except:
            pass


# 置顶登录界面
def ClientWindowToTop():
    hwnd = win32gui.FindWindow("TWINCONTROL", "地下城与勇士登录程序")
    # win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 800, 600,
    #                       win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    if hwnd != 0:
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')

        try:
            win32gui.SetForegroundWindow(hwnd)
        except:
            pass


# 隐藏控制台
def HideConsole():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        ctypes.windll.kernel32.CloseHandle(whnd)


import psutil


def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def main():
    hwnd = win32gui.FindWindow("地下城与勇士", "地下城与勇士")
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 1000, 600, 800, 600,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)


if __name__ == '__main__':
    main()
