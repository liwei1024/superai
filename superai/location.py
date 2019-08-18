import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging
logger = logging.getLogger(__name__)

from superai.flannfind import Picture, GetImgDir

locationAierwenfangxian = Picture(GetImgDir() + "/location_aierwenfangxian.png")


# 分解,出售,修理 单独使用吧
class Location:
    def __init__(self):
        pass

    def get(self):
        if locationAierwenfangxian.Match():
            return "艾尔文防线"

        return ""


def main():
    pass


if __name__ == '__main__':
    main()
