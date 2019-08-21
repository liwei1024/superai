import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

from superai.flannfind import Picture, GetImgDir
from superai.gameapi import GetMenInfo, IsClosedTo, IsManInSelectMap, Quardant, QuadKeyDownMap, QuadKeyUpMap, \
    CurSelectId, GetTaskObj, IsManInMap, IsEscTop, GetAccptedTaskObj, IsWindowTop
from superai.yijianshu import PressKey, VK_CODE, RanSleep, MouseMoveTo, MouseLeftClick, DownZUO, DownYOU

shijiedituScene = Picture(GetImgDir() + "shijieditu.png")
selectmen = Picture(GetImgDir() + "selectmen.png")
gamebegin = Picture(GetImgDir() + "gamebegin.png")
taskScene = Picture(GetImgDir() + "taskscene.png")
taskShouhusenlin = Picture(GetImgDir() + "task_shouhusenlin.png")
zhuanzhiAnqiangshi = Picture(GetImgDir() + "zhuanzhi_anqiangshi.png")
zhuanzhiConfirm = Picture(GetImgDir() + "zhuanzhi_confirm.png")
dituHedunmaer = Picture(GetImgDir() + "ditu_hedunmaer.png")
taskdone = Picture(GetImgDir() + "task_done.png")


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
                     shijiepic=Picture(GetImgDir() + "shijie_gelanzhisen.png"), mousecoord=(651, 241),
                     desc="格兰之森"),

    "林纳斯": MoveInfo(destpic=Picture(GetImgDir() + "ditu_linnasi.png"), destcoord=(1234, 196),
                    shijiepic=Picture(GetImgDir() + "shijie_gelanzhisen.png"), mousecoord=(362, 415),
                    desc="林纳斯"),
    "艾尔文南": MoveInfo(destpic=Picture(GetImgDir() + "ditu_aierwennan.png"), destcoord=(770, 251),
                     shijiepic=Picture(GetImgDir() + "shijie_gelanzhisen.png"), mousecoord=(400, 504),
                     desc="艾尔文南"),
    "月光酒馆": MoveInfo(destpic=Picture(GetImgDir() + "ditu_yueguangjiuguan.png"), destcoord=(758, 216),
                     shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(189, 214),
                     desc="月光酒馆"),
    "挡路帝国军队": MoveInfo(destpic=Picture(GetImgDir() + "ditu_dangludiguo.png"), destcoord=(2308, 319),
                       shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(612, 285),
                       desc="挡路帝国军队"),
    "罗杰": MoveInfo(destpic=Picture(GetImgDir() + "ditu_luojie.png"), destcoord=(1203, 183),
                   shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(560, 263),
                   desc="罗杰"),
    "诺顿": MoveInfo(destpic=Picture(GetImgDir() + "ditu_tiankongzhicheng.png"), destcoord=(331, 161),
                   shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(668, 265),
                   desc="诺顿"),
    "天空之城": MoveInfo(destpic=Picture(GetImgDir() + "ditu_tiankongzhicheng.png"), destcoord=(727, 204),
                     shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(705, 280),
                     desc="天空之城"),
    "洛巴赫": MoveInfo(destpic=Picture(GetImgDir() + "ditu_luobahe.png"), destcoord=(1433, 182),
                    shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(345, 334),
                    desc="洛巴赫"),
    "巴恩": MoveInfo(destpic=Picture(GetImgDir() + "ditu_baen.png"), destcoord=(2216, 193),
                   shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(608, 262),
                   desc="巴恩"),
    "莎兰": MoveInfo(destpic=Picture(GetImgDir() + "ditu_shalan.png"), destcoord=(587, 222),
                   shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(562, 188),
                   desc="莎兰"),
    "艾丽丝": MoveInfo(destpic=Picture(GetImgDir() + "ditu_ailisi.png"), destcoord=(283, 222),
                    shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(544, 188),
                    desc="艾丽丝"),
    "索西雅": MoveInfo(destpic=Picture(GetImgDir() + "ditu_suoxiya.png"), destcoord=(125, 266),
                    shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(151, 212),
                    desc="索西雅"),
    "凯丽": MoveInfo(destpic=Picture(GetImgDir() + "ditu_kaili.png"), destcoord=(2741, 188),
                   shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(412, 335),
                   desc="凯丽"),
    "斯卡迪": MoveInfo(destpic=Picture(GetImgDir() + "ditu_sikadi.png"), destcoord=(440, 205),
                    shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(334, 234),
                    desc="斯卡迪"),
    "奥菲利亚": MoveInfo(destpic=Picture(GetImgDir() + "ditu_aofeiliya.png"), destcoord=(861, 183),
                     shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(533, 369),
                     desc="奥菲利亚"),
    "卡坤": MoveInfo(destpic=Picture(GetImgDir() + "ditu_kakun.png"), destcoord=(1077, 175),
                   shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(543, 367),
                   desc="卡坤"),
    "天锥巨兽": MoveInfo(destpic=Picture(GetImgDir() + "ditu_tianzhuijushou.png"), destcoord=(712, 306),
                     shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(647, 399),
                     desc="天锥巨兽"),
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
        if IsClosedTo(meninfo.chengzhenx, meninfo.chengzheny, destcoord[0], destcoord[1], 40):
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

        while IsWindowTop():
            PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
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
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
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
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


# 转职任务!!!!!
def 守护森林的战斗(player):
    if not DidPlotAccept("守护森林的战斗"):
        while not taskScene.Match():
            PressKey(VK_CODE["F1"]), RanSleep(0.5)

        while not taskShouhusenlin.Match():
            RanSleep(0.5)
        pos = taskShouhusenlin.Pos()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.5)

        while not zhuanzhiAnqiangshi.Match():
            PressKey(VK_CODE["spacebar"]), RanSleep(0.2)

        pos = zhuanzhiAnqiangshi.Pos()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.5)

        while not zhuanzhiConfirm.Match():
            PressKey(VK_CODE["spacebar"]), RanSleep(0.2)

        pos = zhuanzhiConfirm.Pos()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.5)

        while IsWindowTop():
            PressKey(VK_CODE["spacebar"]), RanSleep(0.2)

    moveinfo = MoveSetting["格兰之森"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.ZUO)
    EnterMap("暗黑雷鸣废墟", player)


def 转职祝贺(player):
    moveinfo = MoveSetting["林纳斯"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 赛丽亚的决心(player):
    moveinfo = MoveSetting["林纳斯"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 朝着新的冒险(player):
    moveinfo = MoveSetting["艾尔文南"]
    MoveTo(moveinfo)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 赫顿玛尔的骚乱(player):
    moveinfo = MoveSetting["艾尔文南"]
    MoveTo(moveinfo)

    while not dituHedunmaer.Match():
        QuadKeyDownMap[Quardant.XIA](), RanSleep(1)
        QuadKeyUpMap[Quardant.XIA](), RanSleep(0.5)

    while not taskScene.Match():
        PressKey(VK_CODE["F1"]), RanSleep(0.5)

    pos = taskdone.Pos()
    MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
    MouseLeftClick(), RanSleep(1.5)

    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)

    from superai.superai import Setup
    player.ChangeState(Setup())


def 月光酒馆(player):
    moveinfo = MoveSetting["月光酒馆"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 挡路的帝国军队(player):
    moveinfo = MoveSetting["挡路帝国军队"]
    MoveTo(moveinfo)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 如何进入天空之城(player):
    moveinfo = MoveSetting["罗杰"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 接受考验(player):
    moveinfo = MoveSetting["诺顿"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 进入天空之城(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("龙人之塔", player)


def 探索天空之城(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("龙人之塔", player)


def 汇报结果(player):
    moveinfo = MoveSetting["罗杰"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 调查赫顿玛尔市政厅(player):
    moveinfo = MoveSetting["洛巴赫"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 获得通行证(player):
    moveinfo = MoveSetting["罗杰"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 天空之城的神秘(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("人偶玄关", player)


def 救助(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("人偶玄关", player)


def 帝国骑士(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("石巨人塔", player)


def 寻找帝国公主(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("石巨人塔", player)


def 巴恩的问候(player):
    moveinfo = MoveSetting["巴恩"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 向罗杰汇报(player):
    moveinfo = MoveSetting["罗杰"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 另一桩交易(player):
    moveinfo = MoveSetting["莎兰"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 占卜师爱丽丝(player):
    moveinfo = MoveSetting["爱丽丝"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 艾丽丝的请求(player):
    moveinfo = MoveSetting["罗杰"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 重返天空之城(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("黑暗悬廊", player)


def 合作(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("黑暗悬廊", player)


def 调查天空之城的人(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("黑暗悬廊", player)


def 剑魂阿甘左(player):
    moveinfo = MoveSetting["巴恩"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 月光酒馆的索西雅(player):
    moveinfo = MoveSetting["索西雅"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 水晶净化(player):
    while not taskScene.Match():
        PressKey(VK_CODE["F1"]), RanSleep(0.5)

    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 来自天界的女人(player):
    moveinfo = MoveSetting["凯丽"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 关于使徒巴卡尔(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 去见公国女王(player):
    moveinfo = MoveSetting["洛巴赫"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 贝尔玛尔公国女王斯卡迪(player):
    moveinfo = MoveSetting["斯卡迪"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 天空之城的邪恶魔力(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("城主宫殿", player)


def 浮空之城(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("悬空城", player)


def 光之城主(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("城主宫殿", player)


def 从天而落之物(player):
    moveinfo = MoveSetting["天空之城"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("城主宫殿", player)


def 向斯卡迪女王汇报(player):
    moveinfo = MoveSetting["斯卡迪"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 莎兰的建议(player):
    moveinfo = MoveSetting["莎兰"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 告别和另一段冒险(player):
    moveinfo = MoveSetting["奥菲利亚"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 长脚罗特斯(player):
    moveinfo = MoveSetting["巴恩"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 忘记了(player):
    moveinfo = MoveSetting["卡坤"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def GBL教的神殿(player):
    moveinfo = MoveSetting["天锥巨兽"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("GBL教的神殿", player)


def 被捉的信徒(player):
    moveinfo = MoveSetting["天锥巨兽"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("GBL教的神殿", player)


def 探索丛林(player):
    moveinfo = MoveSetting["天锥巨兽"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("树精丛林", player)


def 美神维纳斯(player):
    moveinfo = MoveSetting["天锥巨兽"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("树精丛林", player)


def 可疑的幸存者(player):
    moveinfo = MoveSetting["天锥巨兽"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("炼狱", player)


def 女神的诅咒(player):
    moveinfo = MoveSetting["天锥巨兽"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("炼狱", player)


def 圣书(player):
    moveinfo = MoveSetting["天锥巨兽"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("极昼", player)


def 在神殿之巅(player):
    moveinfo = MoveSetting["天锥巨兽"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("极昼", player)


def 前往神殿中心(player):
    moveinfo = MoveSetting["天锥巨兽"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("第一脊椎", player)


def 返回地面(player):
    moveinfo = MoveSetting["天锥巨兽"]
    MoveTo(moveinfo)
    GoToSelect(Quardant.YOU)
    EnterMap("第一脊椎", player)


def 奥菲利亚的帮助(player):
    moveinfo = MoveSetting["奥菲利亚"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 骑士团参战(player):
    moveinfo = MoveSetting["卡坤"]
    MoveTo(moveinfo)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    while IsWindowTop():
        PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    from superai.superai import Setup
    player.ChangeState(Setup())


def 艾丽丝的帮助(player):
    while not taskScene.Match():
        PressKey(VK_CODE["F1"]), RanSleep(0.5)

    PressKey(VK_CODE["spacebar"]), RanSleep(0.3)
    from superai.superai import Setup
    player.ChangeState(Setup())


IdxMapMap = {
    # 1-16 格兰之森
    "幽暗密林": 0,
    "雷鸣废墟": 1,
    "猛毒雷鸣废墟": 2,
    "冰霜幽暗密林": 5,
    "格拉卡": 3,
    "烈焰格拉卡": 4,
    "暗黑雷鸣废墟": 6,

    # 17-24:
    "龙人之塔": 0,
    "人偶玄关": 1,
    "石巨人塔": 2,
    "黑暗悬廊": 3,
    "城主宫殿": 4,
    "悬空城": 5,

    # 24:
    "GBL教的神殿": 0,
    "树精丛林": 1,
    "炼狱": 2,
    "极昼": 3,
    "第一脊椎": 4
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
    "守护森林的战斗": 守护森林的战斗,
    "转职祝贺": 转职祝贺,
    "赛丽亚的决心": 赛丽亚的决心,
    "朝着新的冒险": 朝着新的冒险,

    # 17-24
    "赫顿玛尔的骚乱": 赫顿玛尔的骚乱,
    "月光酒馆": 月光酒馆,
    "挡路帝国军队": 挡路的帝国军队,
    "如何进入天空之城": 如何进入天空之城,
    "接受考验": 接受考验,
    "进入天空之城": 进入天空之城,
    "探索天空之城": 探索天空之城,
    "汇报结果": 汇报结果,
    "调查赫顿玛尔市政厅": 调查赫顿玛尔市政厅,
    "获得通行证": 获得通行证,
    "天空之城的神秘": 天空之城的神秘,
    "救助": 救助,
    "帝国骑士——巴恩·巴休特": 帝国骑士,
    "寻找帝国公主": 寻找帝国公主,
    "巴恩的问候": 巴恩的问候,
    "向罗杰汇报": 向罗杰汇报,
    "另一桩交易": 另一桩交易,
    "占卜师爱丽丝": 占卜师爱丽丝,
    "艾丽丝的请求": 艾丽丝的请求,
    "重返天空之城": 重返天空之城,
    "合作": 合作,
    "调查天空之城的人": 调查天空之城的人,
    "剑魂阿甘左": 剑魂阿甘左,
    "月光酒馆的索西雅": 月光酒馆的索西雅,
    "水晶净化": 水晶净化,
    "来自天界的女人": 来自天界的女人,
    "关于使徒巴卡尔": 关于使徒巴卡尔,
    "去见公国女王": 去见公国女王,
    "贝尔玛尔公国女王——斯卡迪": 贝尔玛尔公国女王斯卡迪,
    "天空之城的邪恶魔力": 天空之城的邪恶魔力,
    "浮空之城": 浮空之城,
    "光之城主": 光之城主,
    "从天而落之物": 从天而落之物,
    "向斯卡迪女王汇报": 向斯卡迪女王汇报,
    "莎兰的建议": 莎兰的建议,

    # 24 -
    "告别和另一段冒险": 告别和另一段冒险,
    "长脚罗特斯": 长脚罗特斯,
    "忘记了": 忘记了,
    "GBL教的神殿": GBL教的神殿,
    "被捉的信徒": 被捉的信徒,
    "探索丛林": 探索丛林,
    "美神维纳斯": 美神维纳斯,
    "可疑的幸存者": 可疑的幸存者,
    "女神的诅咒": 女神的诅咒,
    "圣书": 圣书,
    "在神殿之巅": 在神殿之巅,
    "前往神殿中心": 前往神殿中心,
    "返回地面": 返回地面,
    "奥菲利亚的帮助": 奥菲利亚的帮助,
    "骑士团参战": 骑士团参战,
    "艾丽丝的帮助": 艾丽丝的帮助,
}


# 是否有剧情任务
def HasPlot():
    tasks = GetTaskObj()
    for v in tasks:
        if v.name in plotMap.keys():
            return True
    return False


# 任务是否未接受
def DidPlotAccept(name):
    acceptedtasks = GetAccptedTaskObj()
    for v in acceptedtasks:
        if name == v.name:
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
