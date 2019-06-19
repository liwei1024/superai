import sys
import os

import pywintypes
import win32con
import win32file

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from ctypes import *


class ZuoBiaoMsg(Structure):
    _fields_ = [("x", c_uint32),
                ("y", c_uint32)]


class Header(Structure):
    _fields_ = [("len", c_uint32),
                ("type", c_uint32)]


def main():
    zuobiaomsg = ZuoBiaoMsg()
    zuobiaomsg.x = 100
    zuobiaomsg.y = 279

    header = Header()
    header.len = len(bytes(zuobiaomsg))
    header.type = 1

    with open("C:\\xxiii\\ipc", "wb+") as f:
        hfile = win32file._get_osfhandle(f.fileno())

        win32file.LockFileEx(
            hfile,
            win32con.LOCKFILE_EXCLUSIVE_LOCK, 0, 0xffffffff, pywintypes.OVERLAPPED())
        f.write(bytes(header))
        f.write(bytes(zuobiaomsg))
        win32file.UnlockFileEx(hfile, 0, 0xffffffff, pywintypes.OVERLAPPED())


if __name__ == "__main__":
    main()
