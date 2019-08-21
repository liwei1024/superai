import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging
logger = logging.getLogger(__name__)

from superai.flannfind import Picture, GetImgDir

locationGelanzhisen = Picture(GetImgDir() + "ditu_gelanzhisen.png")
locationTiankongzhichen = Picture(GetImgDir() + "ditu_tiankongzhicheng.png")
locationTianzhuijushou  = Picture(GetImgDir() + "ditu_tianzhuijushou.png")

# 分解,出售,修理 单独使用吧
class Location:
    def __init__(self):
        pass

    def get(self):
        if locationGelanzhisen.Match():
            return "格兰之森"

        if locationTiankongzhichen.Match():
            return "天空之城"

        if locationTianzhuijushou.Match():
            return "天锥巨兽"

        return ""


def main():
    pass


if __name__ == '__main__':
    main()
