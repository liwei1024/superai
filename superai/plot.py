import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

from superai.flannfind import Picture, GetImgDir
from superai.gameapi import GetMenInfo, IsClosedTo, IsManInSelectMap, Quardant, QuadKeyDownMap, QuadKeyUpMap, \
    CurSelectId, GetTaskObj, IsManInMap, IsEscTop
from superai.yijianshu import PressKey, VK_CODE, RanSleep, MouseMoveTo, MouseLeftClick, DownZUO, DownYOU

shijiedituScene = Picture(GetImgDir() + "shijieditu.png")

selectmen = Picture(GetImgDir() + "selectmen.png")

gamebegin = Picture(GetImgDir() + "gamebegin.png")


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
    # 1. 目标场景截图 + 城镇坐标,判断是否到达
    # 2. 世界地图特征 + 鼠标移动地图的的绝对坐标
    "格兰之森": MoveInfo(destpic=Picture(GetImgDir() + "ditu_gelanzhisen.png"), destcoord=(161, 256),
                     shijiepic=Picture(GetImgDir() + "shijie_gelanzhisen.png"), mousecoord=(211, 423),
                     desc="格兰之森"),

    "林纳斯": MoveInfo(destpic=Picture(GetImgDir() + "ditu_linnasi.png"), destcoord=(1234, 196),
                    shijiepic=Picture(GetImgDir() + "shijie_gelanzhisen.png"), mousecoord=(362, 415),
                    desc="林纳斯")

}


# 到赛利亚
def MoveToSailiya():
    while not IsEscTop():
        PressKey(VK_CODE["esc"]), RanSleep(0.2)

    while not gamebegin.Match():
        pos = selectmen.Match()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(1.5)


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
        if IsClosedTo(meninfo.chengzhenx, meninfo.chengzheny, destcoord[0], destcoord[1], 50):
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


# 选择地图
def SelectMap(mapname):
    while CurSelectId() != IdxMapMap[mapname]:
        logger.info("↑ 切换地图")
        PressKey(VK_CODE["up_arrow"]), RanSleep(0.2)


# 进图
def EnterMap(mapname, player):
    SelectMap(mapname)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.2)

    while not IsManInMap():
        logger.info("等待进图...")
        RanSleep(2)

    from superai.superai import FirstInMap
    player.ChangeState(FirstInMap())


def 林纳斯的请求(player):
    moveinfo = MoveSetting["格兰之森"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.ZUO)
    EnterMap("幽暗密林", player)


def 再访林纳斯(player):
    moveinfo = MoveSetting["林纳斯"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 传说中的白化变异哥布林(player):
    moveinfo = MoveSetting["格兰之森"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.ZUO)
    EnterMap("幽暗密林", player)


def 毒泉的主人(player):
    moveinfo = MoveSetting["格兰之森"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.ZUO)
    EnterMap("猛毒雷鸣废墟", player)


def 疯掉的魔法师克拉赫(player):
    moveinfo = MoveSetting["格兰之森"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.ZUO)
    EnterMap("冰霜幽暗密林", player)


def 备战格拉卡(player):
    moveinfo = MoveSetting["林纳斯"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 营救赛丽亚(player):
    moveinfo = MoveSetting["格兰之森"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.ZUO)
    EnterMap("格拉卡", player)


def 通向森林深处的道路(player):
    moveinfo = MoveSetting["格兰之森"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.ZUO)
    EnterMap("烈焰格拉卡", player)


def 森林的黑暗(player):
    moveinfo = MoveSetting["格兰之森"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.ZUO)
    EnterMap("暗黑雷鸣废墟", player)


def 大魔法阵是什么(player):
    MoveToSailiya()
    QuadKeyDownMap[Quardant.SHANG](), RanSleep(0.5)
    QuadKeyUpMap[Quardant.SHANG](), RanSleep(0.3)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 前辈冒险家的建议(player):
    moveinfo = MoveSetting["林纳斯"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 守护森林的战斗(player):
    pass


IdxMapMap = {
    # 1-16 格兰之森
    "幽暗密林": 0,
    "雷鸣废墟": 1,
    "猛毒雷鸣废墟": 2,
    "冰霜幽暗密林": 5,
    "格拉卡": 3,
    "烈焰格拉卡": 4,
    "暗黑雷鸣废墟": 6,
}

plotMap = {
    # 1-16 格兰之森
    "林纳斯的请求": 林纳斯的请求,
    "再访林纳斯": 再访林纳斯,
    "传说中的白化变异哥布林": 传说中的白化变异哥布林,
    "毒泉的主人": 毒泉的主人,
    "疯掉的魔法师克拉赫": 疯掉的魔法师克拉赫,
    "备战格拉卡": 备战格拉卡,
    "营救赛丽亚": 营救赛丽亚,
    "森林的黑暗": 森林的黑暗,
    "大魔法阵是什么": 大魔法阵是什么,
    "前辈冒险家的建议": 前辈冒险家的建议,
    "守护森林的战斗": 守护森林的战斗
}


# 是否有剧情任务
def HasPlot():
    tasks = GetTaskObj()
    for v in tasks:
        if v.name in plotMap.keys():
            return True
    return False


# 做剧情任务
def DoPlot(player):
    logger.info("开始做剧情任务")
    tasks = GetTaskObj()
    for v in tasks:
        if v.name in plotMap.keys():
            logger.info("剧情任务: %s" % v.name)
            plotMap[v.name](player)

    from superai.superai import Setup
    player.ChangeState(Setup())


def main():
    pass


if __name__ == '__main__':
    main()
