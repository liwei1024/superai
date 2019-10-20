import logging
import os
import sys

from superai.youling import Youling

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
logger = logging.getLogger(__name__)

from superai.config import GetConfig
from superai.yijianshu import Yijianshu

anjianobj = None


def aj():
    global anjianobj

    if anjianobj is None:
        config = GetConfig()
        anjianuse = config.get("superai", "按键")
        if anjianuse == "易键鼠":
            anjianobj = Yijianshu()
        elif anjianuse == "幽灵按键":
            anjianobj = Youling()
    return anjianobj


def main():
    pass


if __name__ == '__main__':
    main()
