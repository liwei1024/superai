import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

from superai.flannfind import Picture, GetImgDir

locationGelanzhisen = Picture(GetImgDir() + "ditu_gelanzhisen.png")
locationTiankongzhichen = Picture(GetImgDir() + "ditu_tiankongzhicheng.png")
locationTianzhuijushou = Picture(GetImgDir() + "ditu_tianzhuijushou.png")
locationAfaliya = Picture(GetImgDir() + "ditu_afaliya2.png")
locationNuoyipeila = Picture(GetImgDir() + "ditu_nuoyipeila.png")

wenziaierwenfangxian = Picture(GetImgDir() + "wenzi_aierwenfangxian.png", 610, 22, 182, 25)
wenzihedunmaer = Picture(GetImgDir() + "wenzi_hedunmaer.png", 610, 22, 182, 25)
wenziaerfayingdi = Picture(GetImgDir() + "wenzi_aerfayingdi.png", 610, 22, 182, 25)
wenzianheicheng = Picture(GetImgDir() + "wenzi_anheicheng.png", 610, 22, 182, 25)
wenzixihaian = Picture(GetImgDir() + "wenzi_xihaian.png", 610, 22, 182, 25)
wenzisidunxueyu = Picture(GetImgDir() + "wenzi_sidunxueyu.png", 610, 22, 182, 25)


# 是否在艾尔文防线
def IsinAierwenfnagxian():
    if wenziaierwenfangxian.Match() or wenzisidunxueyu.Match():
        logger.info("在艾尔文防线")
        return True
    else:
        logger.warning("不在艾尔文防线")
        return False


# 是否在赫顿玛尔
def IsinHedunmaer():
    if wenzihedunmaer.Match() or wenzixihaian.Match():
        logger.info("在赫顿玛尔")
        return True
    else:
        logger.warning("不在赫顿玛尔")
        return False


# 是否在阿尔法营地
def IsinAerfayingdi():
    if wenziaerfayingdi.Match() or wenzianheicheng.Match():
        logger.info("在阿尔法营地")
        return True
    else:
        logger.warning("不在阿尔法营地")
        return False


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
