import os
import sys
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.pathsetting import GetYoulingLib

from superai.common import InitLog

from ctypes import *
import logging

logger = logging.getLogger(__name__)

lib = GetYoulingLib()

lib.OpenDevice.argtypes = []
lib.OpenDevice.restype = c_bool


def main():
    InitLog()
    print(1)
    res = lib.OpenDevice()
    print(2)
    print(res)


if __name__ == '__main__':
    main()
