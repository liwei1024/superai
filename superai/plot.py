import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

from superai.flannfind import Picture, GetImgDir
from superai.gameapi import GetMenInfo, IsClosedTo, IsManInSelectMap, Quardant, QuadKeyDownMap, QuadKeyUpMap, \
    CurSelectId
from superai.yijianshu import PressKey, VK_CODE, RanSleep, MouseMoveTo, MouseLeftClick, DownZUO, DownYOU

shijiedituScene = Picture(GetImgDir() + "shijieditu.png")


class MoveInfo:
    def __init__(self, destpic, destcoord, shijiepic, mousecoord, desc):
        # 目的地位置的 场景图片 (判断是否移动到)
        self.destpic = destpic

        # 目的地城镇坐标 (判断是否移动到)
        self.destcoord = destcoord

        # 标识世界地图是否能够到达目的地
        self.shijiepic = shijiepic

        # 移动到世界地图哪个位置可以到达目的地
        self.mousecoord = mousecoord

        # 描述
        self.desc = desc


MoveSetting = {
    "格兰之森": MoveInfo(destpic=Picture(GetImgDir() + "ditu_gelanzhisen.png"), destcoord=(163, 288),
                     shijiepic=Picture(GetImgDir() + "shijie_gelanzhisen.png"), mousecoord=(211, 423),
                     desc="格兰之森")

}


# 打开世界地图
def OpenShijieDitu():
    while not shijiedituScene.Match():
        logger.info("打开世界地图")
        PressKey(VK_CODE["n"]), RanSleep(0.5)


# 关闭世界地图
def CloseShijieDitu():
    while shijiedituScene.Match():
        logger.info("关闭世界地图")
        PressKey(VK_CODE["n"]), RanSleep(0.5)


# 是否移动城镇的位置
def IsMoveToChengzhenPos(destpic, destcoord):
    if destpic.Match():
        meninfo = GetMenInfo()
        if IsClosedTo(meninfo.x, meninfo.y, destcoord.x, destcoord.y):
            return True
    return False


# 移动到目的位置
def CoordMoveTo(shijitpic, mousecoord):
    OpenShijieDitu()
    if not shijitpic.Match():
        raise NotImplementedError()
    MouseMoveTo(mousecoord[0], mousecoord[1]), RanSleep(0.3)
    MouseLeftClick(), RanSleep(0.3)
    CloseShijieDitu()


# 移动到目的位置 (幂等,最终)
def MoveTo(moveinfo):
    logger.info("目标位置 %s" % moveinfo.desc)
    t = None
    while not IsMoveToChengzhenPos(moveinfo.destpic, moveinfo.destcoord):
        if t is None or time.time() - t > 10.0:
            logger.info("目标: %s 城镇位置: (%d,%d)  没有到达, 开始移动. 鼠标指向到 (%d, %d)" % (moveinfo.desc, moveinfo.destcoord[0],
                                                                              moveinfo.destcoord[1],
                                                                              moveinfo.mousecoord[0],
                                                                              moveinfo.mousecoord[1]))
            t = time.time()
            CoordMoveTo(moveinfo.shijiepic, moveinfo.mousecoord)

        RanSleep(1.0)


# 到达选择角色页面
def GoToSelect(quad: Quardant):
    while not IsManInSelectMap():
        logger.info("微调选择地图")
        QuadKeyDownMap[quad](), RanSleep(1)
        QuadKeyUpMap[quad](), RanSleep(0.5)


IdxMapMap = {
    "幽暗密林": 0
}


# 选择地图
def SelectMap(mapname):
    while CurSelectId() != IdxMapMap[mapname]:
        logger.info("↑ 切换地图")
        PressKey(VK_CODE["up_arrow"]), RanSleep(0.2)


def linnasideqingqiu():
    moveinfo = MoveSetting["格兰之森"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.ZUO)
    SelectMap("幽暗密林")


plotMap = {
    "林纳斯的请求": linnasideqingqiu
}


def main():
    pass


if __name__ == '__main__':
    main()
