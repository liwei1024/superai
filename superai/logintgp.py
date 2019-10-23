import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.superai import tgpselectdaqu
from superai.anjian import aj
from superai.common import KongjianSleep, RanSleep
from superai.pathsetting import GetvercodeDir
from superai.screenshots import WindowCaptureToFile


# tgp 固定大区坐标
firstposes = [
    ()
]


def main():
    time.sleep(5)
    imgfile = WindowCaptureToFile("TWINCONTROL", "WeGame", GetvercodeDir())



if __name__ == '__main__':
    main()
