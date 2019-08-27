import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

from superai.flannfind import Picture, GetImgDir
from superai.plot import IsinAierwenfnagxian, IsinHedunmaer, IsinAerfayingdi


locationGelanzhisen = Picture(GetImgDir() + "ditu_gelanzhisen.png")
locationTiankongzhichen = Picture(GetImgDir() + "ditu_tiankongzhicheng.png")
locationTianzhuijushou = Picture(GetImgDir() + "ditu_tianzhuijushou.png")
locationAfaliya = Picture(GetImgDir() + "ditu_afaliya2.png")
locationNuoyipeila = Picture(GetImgDir() + "ditu_nuoyipeila.png")


# 分解,出售,修理 单独使用吧
class Location:
    def __init__(self):
        pass

    def get(self):
        if IsinAierwenfnagxian() and locationGelanzhisen.Match():
            return "格兰之森"
        elif IsinHedunmaer() and locationTiankongzhichen.Match():
            return "天空之城"
        elif IsinHedunmaer() and locationTianzhuijushou.Match():
            return "天锥巨兽"
        elif IsinAerfayingdi() and locationAfaliya.Match():
            return "阿法利亚"
        elif IsinAerfayingdi() and locationNuoyipeila.Match():
            return "诺伊佩拉"

        return ""


def main():
    pass


if __name__ == '__main__':
    main()
