import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

from superai.flannfind import Picture, GetImgDir
from superai.gameapi import GetMenInfo, IsClosedTo, IsManInSelectMap, Quardant, QuadKeyDownMap, QuadKeyUpMap, \
    CurSelectId, GetTaskObj, IsManInMap, IsEscTop, GetAccptedTaskObj, IsWindowTop, Clear
from superai.yijianshu import PressKey, VK_CODE, RanSleep, MouseMoveTo, MouseLeftClick

shijiedituScene = Picture(GetImgDir() + "shijieditu.png")
selectmen = Picture(GetImgDir() + "selectmen.png")
gamebegin = Picture(GetImgDir() + "gamebegin.png")
taskScene = Picture(GetImgDir() + "taskscene.png")
taskShouhusenlin = Picture(GetImgDir() + "task_shouhusenlin.png")
taskChaozhexindemaoxian = Picture(GetImgDir() + "task_chaozhexindemaoxian.png")
taskHuodetongxinzhen = Picture(GetImgDir() + "task_huodetongxingzhen.png")
taskkzhuxian = Picture(GetImgDir() + "task_zhuxian.png")
taskok = Picture(GetImgDir() + "taskok.png")
zhuanzhiAnqiangshi = Picture(GetImgDir() + "zhuanzhi_anqiangshi.png")
zhuanzhiConfirm = Picture(GetImgDir() + "zhuanzhi_confirm.png")
dituHedunmaer = Picture(GetImgDir() + "ditu_hedunmaer.png")
dituAfaliya = Picture(GetImgDir() + "ditu_afaliya.png")
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
                     shijiepic=Picture(GetImgDir() + "shijie_gelanzhisen.png"), mousecoord=(209, 424),
                     desc="格兰之森"),

    "林纳斯": MoveInfo(destpic=Picture(GetImgDir() + "ditu_linnasi.png"), destcoord=(1234, 196),
                    shijiepic=Picture(GetImgDir() + "shijie_gelanzhisen.png"), mousecoord=(362, 415),
                    desc="林纳斯"),
    "艾尔文南": MoveInfo(destpic=Picture(GetImgDir() + "ditu_aierwennan.png"), destcoord=(770, 251),
                     shijiepic=Picture(GetImgDir() + "shijie_gelanzhisen.png"), mousecoord=(400, 504),
                     desc="艾尔文南"),
    "月光酒馆": MoveInfo(destpic=Picture(GetImgDir() + "ditu_yueguangjiuguan.png"), destcoord=(758, 216),
                     shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(189, 219),
                     desc="月光酒馆"),
    "挡路的帝国军队": MoveInfo(destpic=Picture(GetImgDir() + "ditu_dangludiguo.png"), destcoord=(2308, 319),
                        shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(612, 285),
                        desc="挡路的帝国军队"),
    "罗杰": MoveInfo(destpic=Picture(GetImgDir() + "ditu_luojie.png"), destcoord=(1190, 183),
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
    "天帷巨兽": MoveInfo(destpic=Picture(GetImgDir() + "ditu_tianzhuijushou.png"), destcoord=(712, 306),
                     shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(647, 399),
                     desc="天帷巨兽"),
    "赫顿玛尔": MoveInfo(destpic=Picture(GetImgDir() + "ditu_hedunmaer2.png"), destcoord=(1430, 188),
                     shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(346, 335),
                     desc="赫顿玛尔"),
    "阿甘左": MoveInfo(destpic=Picture(GetImgDir() + "ditu_aganzuo.png"), destcoord=(1096, 188),
                    shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(210, 213),
                    desc="阿甘左"),
    "后街": MoveInfo(destpic=Picture(GetImgDir() + "ditu_houjie.png"), destcoord=(578, 244),
                   shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(221, 300),
                   desc="后街"),
    "布告": MoveInfo(destpic=Picture(GetImgDir() + "ditu_bugaolan.png"), destcoord=(926, 213),
                   shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(320, 339),
                   desc="布告"),
    "赫顿玛尔2": MoveInfo(destpic=Picture(GetImgDir() + "hedunmaer2.png"), destcoord=(1257, 417),
                      shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(336, 372),
                      desc="赫顿玛尔2"),
}


class TaskCtx:
    def __init__(self):
        # 上一次小地图按键的时间点(对话NPC)
        self.latestmovpoint = None

        # 上一次完成任务单击时间
        self.latestsubmitpoint = None

    def Clear(self):
        self.latestmovpoint = None
        # self.latestsubmitpoint = None


# 到赛利亚
def BackAndEnter():
    while not IsEscTop():
        logger.info("打开esc")
        PressKey(VK_CODE["esc"]), RanSleep(0.2)

    while not gamebegin.Match():
        logger.info("寻找游戏开始按钮")

        pos = selectmen.Pos()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(1.5)

    PressKey(VK_CODE["spacebar"]), RanSleep(0.2)


# 打开世界地图
def OpenShijieDitu():
    Clear()

    logger.info("打开世界地图")
    PressKey(VK_CODE["n"]), RanSleep(0.5)
    return shijiedituScene.Match()


# 关闭世界地图
def CloseShijieDitu():
    while shijiedituScene.Match():
        logger.info("关闭世界地图")
        PressKey(VK_CODE["n"]), RanSleep(0.5)


# 是否移动城镇的位置
def IsMoveToChengzhenPos(destpic, destcoord):
    if destpic.Match():
        meninfo = GetMenInfo()
        if IsClosedTo(meninfo.chengzhenx, meninfo.chengzheny, destcoord[0], destcoord[1], 100):
            return True
    return False


# 移动到目的位置
def CoordMoveTo(shijitpic, mousecoord):
    if OpenShijieDitu():
        if not shijiedituScene.Match():
            raise NotImplementedError()
        MouseMoveTo(mousecoord[0], mousecoord[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)
        CloseShijieDitu()


# 移动到目的位置
def MoveTo(npcname, player):
    moveinfo = MoveSetting[npcname]
    if player.taskctx.latestmovpoint is None or time.time() > player.taskctx.latestmovpoint + 10.0:
        # 没有移动过或者超时

        logger.info("目标: %s 城镇位置: (%d,%d)  没有到达, 开始移动. 鼠标指向到 (%d, %d)" % (
            moveinfo.desc, moveinfo.destcoord[0],
            moveinfo.destcoord[1], moveinfo.mousecoord[0],
            moveinfo.mousecoord[1]))

        CoordMoveTo(moveinfo.shijiepic, moveinfo.mousecoord)
        player.taskctx.latestmovpoint = time.time()
    else:
        logger.info("城镇移动中")


# 到达选择角色页面
def GoToSelect(quad: Quardant):
    while not IsManInSelectMap():
        logger.info("微调选择地图")
        QuadKeyDownMap[quad](), RanSleep(1)
        QuadKeyUpMap[quad](), RanSleep(0.5)


# 选择地图
def SelectMap(mapname):
    idx = IdxMapMap[mapname]
    while CurSelectId() != idx:
        logger.info("↑ 切换地图")
        PressKey(VK_CODE["up_arrow"]), RanSleep(0.2)


# 进图
def EnterMap(mapname, player):
    SelectMap(mapname)
    PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
    while not IsManInMap():
        logger.info("等待进图...")
        RanSleep(1)
    from superai.superai import FirstInMap
    player.ChangeState(FirstInMap())


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
        if name in v.name:
            return True
    return False


# 保证任务已经被接受. (接受任务列表里有主线剧情)
def IsTaskaccept():
    acceptedtasks = GetAccptedTaskObj()
    for v in acceptedtasks:
        if "守护森林的战斗" in v.name:
            return True

        if v.name in plotMap:
            return True

    return False


# 任务是否完成
def TaskOk():
    acceptedtasks = GetAccptedTaskObj()
    for v in acceptedtasks:
        if not v.needdo:
            return True
    return False


# 领取主线任务
def AcceptMain():
    MouseMoveTo(0, 0), RanSleep(0.3)
    Clear()

    if not taskScene.Match():
        logger.info("F1打开任务")
        PressKey(VK_CODE["F1"]), RanSleep(0.3)

        if not taskScene.Match():
            logger.warning("按F1了没出现任务框")
            return

    if not taskkzhuxian.Match():
        logger.warning("没有主线任务")
        return

    if IsWindowTop():
        logger.warning("有窗口弹出,退出领取主线任务")
        return

    pos = taskkzhuxian.Pos()
    MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
    MouseLeftClick(), RanSleep(1)


# 完成任务  (直接完成不能一直点,因为会有对话框弹出来,多次按任务对话框数据变0)
def SubmitTask(player):
    if player.taskctx.latestsubmitpoint is None or time.time() - player.taskctx.latestsubmitpoint > 5.0:
        MouseMoveTo(0, 0), RanSleep(0.3)
        Clear()

        if not taskScene.Match():
            logger.info("F1打开任务")
            PressKey(VK_CODE["F1"]), RanSleep(0.3)

            if not taskScene.Match():
                logger.warning("按F1了没出现任务框")
                return

        if not taskok.Match():
            logger.warning("没有完成的主线任务")
            return

        if IsWindowTop():
            logger.warning("有窗口弹出,退出完成任务")
            return

        pos = taskok.Pos()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(1)

        player.taskctx.latestsubmitpoint = time.time()
    else:
        logger.warning("完成任务不能多次点击,本次啥都不做")


# 返回一个打指定地图的函数
def AttacktaskFoo(fubenname):
    # 获取地图名称
    dituname = ""
    for k, v in fubenMap.items():
        if fubenname in v:
            dituname = k

    def foo(player, dituname=dituname, fubenname=fubenname):
        if not IsTaskaccept():
            logger.info("没有主线任务被接受")
            AcceptMain(), RanSleep(0.3)
            return

        if TaskOk():
            logger.info("任务直接可完成")
            SubmitTask(player), RanSleep(0.3)
            return

        moveinfo = MoveSetting[dituname]
        if IsMoveToChengzhenPos(moveinfo.destpic, moveinfo.destcoord):
            # 左右调整进入地图选择界面
            GoToSelect(quadMap[dituname])
            # 进入地图
            EnterMap(fubenname, player)
        else:
            # 移动到指定位置
            MoveTo(dituname, player)

    return foo


# 是否移动到
def HasMoveTo(npcname):
    moveinfo = MoveSetting[npcname]
    return IsMoveToChengzhenPos(moveinfo.destpic, moveinfo.destcoord)


# 返回一个访问指定对象的函数
def MeetNpcFoo(npcname):
    def foo(player, npcname=npcname):
        if not IsTaskaccept():
            logger.info("没有主线任务被接受")
            AcceptMain(), RanSleep(0.3)
            return

        if TaskOk():
            logger.info("任务直接可完成")
            SubmitTask(player), RanSleep(0.3)
            return

        if npcname == "":
            logger.info("空任务")
            return

        if npcname == "赛利亚":
            # 返回角色再进入
            BackAndEnter()
            QuadKeyDownMap[Quardant.SHANG](), RanSleep(1)
            QuadKeyUpMap[Quardant.SHANG](), RanSleep(0.3)
            PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
        else:
            if HasMoveTo(npcname):
                logger.info("到达了指定位置,按space键")
                PressKey(VK_CODE["spacebar"]), RanSleep(0.2)
            else:
                MoveTo(npcname, player)

    return foo


# 转职任务!!!!!
def 守护森林的战斗(player):
    if not DidPlotAccept("守护森林的战斗"):
        logger.info("任务没有接受, 接受任务")
        # 接受任务
        while not taskScene.Match():
            logger.info("F1打开任务")
            PressKey(VK_CODE["F1"]), RanSleep(0.5)

        while not taskShouhusenlin.Match():
            logger.info("寻找守护森林任务")
            RanSleep(0.5)

        pos = taskShouhusenlin.Pos()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.5)

        # 转职按钮
        while not zhuanzhiAnqiangshi.Match():
            logger.info("寻找转职按钮")
            PressKey(VK_CODE["spacebar"]), RanSleep(1)

        # TODO  目前写死暗枪. 要搞个全局变量
        pos = zhuanzhiAnqiangshi.Pos()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.5)

        while not zhuanzhiConfirm.Match():
            logger.info("寻找转职确认按钮")
            PressKey(VK_CODE["spacebar"]), RanSleep(0.2)

        # 确认
        pos = zhuanzhiConfirm.Pos()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.5)
    else:
        AttacktaskFoo("暗黑雷鸣废墟")(player)


# 需要到指定位置
def 赫顿玛尔的骚乱(player):
    if HasMoveTo("艾尔文南"):
        logger.info("移动到了艾尔文南")
        while not dituHedunmaer.Match():
            logger.info("按键前往赫顿玛尔")
            QuadKeyDownMap[Quardant.XIA](), RanSleep(1)
            QuadKeyUpMap[Quardant.XIA](), RanSleep(0.5)

        while not taskScene.Match():
            logger.info("F1打开任务列表")
            PressKey(VK_CODE["F1"]), RanSleep(0.5)
        pos = taskdone.Pos()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(1.5)
    else:
        MoveTo("艾尔文南", player)


# 同名任务
def 长脚罗特斯():
    def foo(player):
        meninfo = GetMenInfo()
        if meninfo.level < 30:
            MeetNpcFoo("巴恩")(player)
        else:
            AttacktaskFoo("第二脊椎")(player)

    return foo


# 走到新的位置
def 前往阿法利亚营地(player):
    if HasMoveTo("赫顿玛尔2"):
        logger.info("移动到了赫顿玛尔2")

        while not dituAfaliya.Match():
            QuadKeyDownMap[Quardant.XIA](), RanSleep(1)
            QuadKeyUpMap[Quardant.XIA](), RanSleep(0.5)

        logger.info("到达了阿法利亚营地")


    else:
        MoveTo("赫顿玛尔2", player)


fubenMap = {
    "格兰之森": ["幽暗密林", "猛毒雷鸣废墟", "冰霜幽暗密林", "格拉卡", "烈焰格拉卡", "烈焰格拉卡", "暗黑雷鸣废墟"],
    "天空之城": ["龙人之塔", "人偶玄关", "石巨人塔", "黑暗悬廊", "城主宫殿", "悬空城"],
    "天帷巨兽": ["GBL教的神殿", "树精丛林", "炼狱", "极昼", "第一脊椎", "天帷禁地", "第二脊椎"]
}

quadMap = {
    "格兰之森": Quardant.ZUO,
    "天空之城": Quardant.YOU,
    "天帷巨兽": Quardant.YOU,
}

IdxMapMap = {
    # 1-16 格兰之森
    "幽暗密林": 0,
    "雷鸣废墟": 1,
    "猛毒雷鸣废墟": 2,
    "冰霜幽暗密林": 3,
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
    "第一脊椎": 4,
    "天帷禁地": 5,  # TODO 剧情变化了,下标也变啦
    "第二脊椎": 5
}

plotMap = {
    # 1-16 格兰之森
    "林纳斯的请求": AttacktaskFoo("幽暗密林"),
    "再访林纳斯": MeetNpcFoo("林纳斯"),
    "传说中的白化变异哥布林": AttacktaskFoo("幽暗密林"),
    "毒泉的主人": AttacktaskFoo("猛毒雷鸣废墟"),
    "疯掉的魔法师克拉赫": AttacktaskFoo("冰霜幽暗密林"),
    "备战格拉卡": MeetNpcFoo("林纳斯"),
    "营救赛丽亚": AttacktaskFoo("格拉卡"),
    "通向森林深处的道路": AttacktaskFoo("烈焰格拉卡"),
    "森林的黑暗": AttacktaskFoo("暗黑雷鸣废墟"),
    "大魔法阵是什么": MeetNpcFoo("赛利亚"),
    "前辈冒险家的建议": MeetNpcFoo("林纳斯"),
    "守护森林的战斗": 守护森林的战斗,
    "转职祝贺": MeetNpcFoo("林纳斯"),
    "赛丽亚的决心": MeetNpcFoo("林纳斯"),
    "朝着新的冒险": MeetNpcFoo("艾尔文南"),

    # 17-24
    "赫顿玛尔的骚乱": 赫顿玛尔的骚乱,
    "月光酒馆": MeetNpcFoo("月光酒馆"),
    "挡路的帝国军队": MeetNpcFoo("挡路的帝国军队"),
    "如何进入天空之城": MeetNpcFoo("罗杰"),
    "接受考验": MeetNpcFoo("诺顿"),
    "进入天空之城": AttacktaskFoo("龙人之塔"),
    "探索天空之城": AttacktaskFoo("龙人之塔"),
    "汇报结果": MeetNpcFoo("罗杰"),
    "调查赫顿玛尔市政厅": MeetNpcFoo("洛巴赫"),
    "获得通行证": MeetNpcFoo("罗杰"),
    "天空之城的神秘": AttacktaskFoo("人偶玄关"),
    "救助": AttacktaskFoo("人偶玄关"),
    "帝国骑士——巴恩·巴休特": AttacktaskFoo("石巨人塔"),
    "寻找帝国公主": AttacktaskFoo("石巨人塔"),
    "巴恩的问候": MeetNpcFoo("巴恩"),
    "向罗杰汇报": MeetNpcFoo("罗杰"),
    "另一桩交易": MeetNpcFoo("莎兰"),
    "占卜师艾丽丝": MeetNpcFoo("艾丽丝"),
    "艾丽丝的请求": MeetNpcFoo("罗杰"),
    "重返天空之城": AttacktaskFoo("黑暗悬廊"),
    "合作": AttacktaskFoo("黑暗悬廊"),
    "调查天空之城的人": AttacktaskFoo("黑暗悬廊"),
    "剑魂阿甘左": MeetNpcFoo("巴恩"),
    "月光酒馆的索西雅": MeetNpcFoo("索西雅"),
    "水晶净化": MeetNpcFoo(""),
    "来自天界的女人": MeetNpcFoo("凯丽"),
    "关于使徒巴卡尔": MeetNpcFoo("天空之城"),
    "去见公国女王": MeetNpcFoo("洛巴赫"),
    "贝尔玛尔公国女王——斯卡迪": MeetNpcFoo("斯卡迪"),
    "天空之城的邪恶魔力": AttacktaskFoo("城主宫殿"),
    "浮空之城": AttacktaskFoo("悬空城"),
    "光之城主": AttacktaskFoo("城主宫殿"),
    "从天而落之物": AttacktaskFoo("城主宫殿"),
    "向斯卡迪女王汇报": MeetNpcFoo("斯卡迪"),
    "莎兰的建议": MeetNpcFoo("莎兰"),

    # 24 -
    "告别和另一段冒险": MeetNpcFoo("奥菲利亚"),
    # "长脚罗特斯": MeetNpcFoo("巴恩"),
    "长脚罗特斯": 长脚罗特斯(),
    "前往天帷巨兽": MeetNpcFoo("卡坤"),
    "GBL教的神殿": AttacktaskFoo("GBL教的神殿"),
    "被捉的信徒": AttacktaskFoo("GBL教的神殿"),
    "探索丛林": AttacktaskFoo("树精丛林"),
    "美神维纳斯": AttacktaskFoo("树精丛林"),
    "可疑的幸存者": AttacktaskFoo("炼狱"),
    "女神的诅咒": AttacktaskFoo("炼狱"),
    "圣书": AttacktaskFoo("极昼"),
    "在神殿之巅": AttacktaskFoo("极昼"),
    "前往神殿中心": AttacktaskFoo("第一脊椎"),
    "返回地面": AttacktaskFoo("第一脊椎"),
    "奥菲利亚的帮助": MeetNpcFoo("奥菲利亚"),
    "骑士团参战": MeetNpcFoo("卡坤"),
    "艾丽丝的帮助": MeetNpcFoo(""),
    "前往天帷巨兽的肚子里": AttacktaskFoo("天帷禁地"),
    "无法幸免的马塞尔": AttacktaskFoo("天帷禁地"),
    "罗特斯所在之地": AttacktaskFoo("第二脊椎"),
    "寻找阿甘左": AttacktaskFoo("第二脊椎"),
    # "长脚罗特斯": AttacktaskFoo("第二脊椎"),
    "消灭长脚罗特斯": AttacktaskFoo("第二脊椎"),
    "满目疮痍的胜利": MeetNpcFoo("奥菲利亚"),
    "斯卡迪女王": MeetNpcFoo("斯卡迪"),
    "艾丽丝到访": MeetNpcFoo("赫顿玛尔"),
    "关于艾丽丝的秘密与使徒": MeetNpcFoo("艾丽丝"),
    "使徒的危险性": MeetNpcFoo("艾丽丝"),
    "前往月光酒馆": MeetNpcFoo("阿甘左"),
    "战端又起": MeetNpcFoo("月光酒馆"),
    "商人的情报": MeetNpcFoo("后街"),
    "宣战": MeetNpcFoo("布告"),
    "忐忑不安的人们": MeetNpcFoo("洛巴赫"),
    "前往阿法利亚营地": 前往阿法利亚营地,

}


def main():
    pass


if __name__ == '__main__':
    main()
