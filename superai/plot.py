import os
import sys
import time

from superai.equip import OpenBagScene, ZhunangbeiPos, XiaohaoPos, bagScene, CloseBagScene

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

from superai.flannfind import Picture, GetImgDir
from superai.gameapi import GetMenInfo, IsClosedTo, IsManInSelectMap, Quardant, QuadKeyDownMap, QuadKeyUpMap, \
    CurSelectId, GetTaskObj, IsManInMap, IsEscTop, GetAccptedTaskObj, IsWindowTop, Clear, Openesc, SafeClear
from superai.yijianshu import PressKey, VK_CODE, RanSleep, MouseMoveTo, MouseLeftClick, MouseLeftDown, MouseMoveR, \
    MouseLeftUp, KongjianSleep

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
zhuanzhiYoumozhe = Picture(GetImgDir() + "zhuanzhi_youmozhe.png")
zhuanzhiPalading = Picture(GetImgDir() + "zhuanzhi_palading.png")
zhuanzhiConfirm = Picture(GetImgDir() + "zhuanzhi_confirm.png")
dituHedunmaer = Picture(GetImgDir() + "ditu_hedunmaer.png")
dituHedunmaer3 = Picture(GetImgDir() + "ditu_hedunmaer3.png")
dituAfaliya = Picture(GetImgDir() + "ditu_afaliya.png")
taskdone = Picture(GetImgDir() + "task_done.png")
aganzuowupin = Picture(GetImgDir() + "aganzuo_wupin.png", 243, 560, 28, 28)
aganzuowupin2 = Picture(GetImgDir() + "aganzuo_wupin2.png")

wenziaierwenfangxian = Picture(GetImgDir() + "wenzi_aierwenfangxian.png", 610, 22, 182, 25)
wenzihedunmaer = Picture(GetImgDir() + "wenzi_hedunmaer.png", 610, 22, 182, 25)
wenziaerfayingdi = Picture(GetImgDir() + "wenzi_aerfayingdi.png", 610, 22, 182, 25)
wenzianheicheng = Picture(GetImgDir() + "wenzi_anheicheng.png", 610, 22, 182, 25)
wenzixihaian = Picture(GetImgDir() + "wenzi_xihaian.png", 610, 22, 182, 25)

Wupin6Pos = (255, 577)


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
    "洛巴赫": MoveInfo(destpic=Picture(GetImgDir() + "ditu_luobahe.png"), destcoord=(1433, 176),
                    shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(345, 333),
                    desc="洛巴赫"),

    "洛巴赫2": MoveInfo(destpic=Picture(GetImgDir() + "ditu_luobahe2.png"), destcoord=(658, 215),
                     shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(355, 237),
                     desc="洛巴赫2"),
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
    "赫顿玛尔2": MoveInfo(destpic=Picture(GetImgDir() + "hedunmaer2.png"), destcoord=(1254, 417),
                      shijiepic=Picture(GetImgDir() + "shijie_hedunmaer.png"), mousecoord=(336, 372),
                      desc="赫顿玛尔2"),

    "洛巴赫3": MoveInfo(destpic=Picture(GetImgDir() + "ditu_luobahe3.png"), destcoord=(346, 160),
                     shijiepic=Picture(GetImgDir() + "shijie_aerfa.png"), mousecoord=(281, 258),
                     desc="洛巴赫3"),
    "克伦特": MoveInfo(destpic=Picture(GetImgDir() + "dittu_kelunte.png"), destcoord=(474, 135),
                    shijiepic=Picture(GetImgDir() + "shijie_aerfa.png"), mousecoord=(381, 259),
                    desc="克伦特"),
    "阿法利亚": MoveInfo(destpic=Picture(GetImgDir() + "ditu_afaliya2.png"), destcoord=(752, 227),
                     shijiepic=Picture(GetImgDir() + "shijie_aerfa.png"), mousecoord=(522, 281),
                     desc="阿法利亚"),
    "鲁埃尔": MoveInfo(destpic=Picture(GetImgDir() + "ditu_luaier.png"), destcoord=(760, 123),
                    shijiepic=Picture(GetImgDir() + "shijie_aerfa.png"), mousecoord=(405, 257),
                    desc="鲁埃尔"),
    "帕丽丝": MoveInfo(destpic=Picture(GetImgDir() + "ditu_palisi.png"), destcoord=(521, 160),
                    shijiepic=Picture(GetImgDir() + "shijie_aerfa.png"), mousecoord=(302, 261),
                    desc="帕丽丝"),
    "梅娅女王": MoveInfo(destpic=Picture(GetImgDir() + "ditu_meiyanvwang.png"), destcoord=(482, 219),
                     shijiepic=Picture(GetImgDir() + "shijie_aerfa.png"), mousecoord=(386, 489),
                     desc="梅娅女王"),
    "阿尔法-赫顿玛尔": MoveInfo(destpic=Picture(GetImgDir() + "ditu_aerfahedunmaer.png"), destcoord=(290, 81),
                         shijiepic=Picture(GetImgDir() + "shijie_aerfa.png"), mousecoord=(220, 180),
                         desc="阿尔法-赫顿玛尔"),
    "王宫外": MoveInfo(destpic=Picture(GetImgDir() + "ditu_wanggongwai.png"), destcoord=(1103, 302),
                    shijiepic=Picture(GetImgDir() + "shijie_aerfa.png"), mousecoord=(501, 508),
                    desc="王宫外"),
    "诺伊佩拉": MoveInfo(destpic=Picture(GetImgDir() + "ditu_nuoyipeila.png"), destcoord=(982, 182),
                     shijiepic=Picture(GetImgDir() + "shijie_aerfa.png"), mousecoord=(580, 425),
                     desc="诺伊佩拉"),
}


class TaskCtx:
    def __init__(self):
        # 上一次小地图按键的时间点(对话NPC)
        self.latestmovepoint = None

        # 上一次完成任务单击时间
        self.latestsubmitpoint = None

    def Clear(self):
        pass
        # self.latestmovepoint = None
        # self.latestsubmitpoint = None


# 到赛利亚
def BackAndEnter():
    if not Openesc():
        logger.warning("打开esc失败")
        return

    if not gamebegin.Match():
        logger.info("寻找游戏开始按钮")
        pos = selectmen.Pos()
        MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        MouseLeftClick(), RanSleep(1.5)  # TODO 写死了

    PressKey(VK_CODE["spacebar"]), KongjianSleep()


# 打开任务栏
def OpenTaskScene():
    Clear()

    if not taskScene.Match():
        logger.info("F1打开任务列表")
        PressKey(VK_CODE["F1"]), KongjianSleep()
    return taskScene.Match()


# 打开世界地图
def OpenShijieDitu():
    Clear()

    if not shijiedituScene.Match():
        logger.info("打开世界地图")
        PressKey(VK_CODE["n"]), KongjianSleep()

    return shijiedituScene.Match()


# 关闭世界地图
def CloseShijieDitu():
    if shijiedituScene.Match():
        logger.info("关闭世界地图")
        PressKey(VK_CODE["n"]), KongjianSleep()


# 是否移动城镇的位置
def IsMoveToChengzhenPos(destpic, destcoord, desc):
    if destpic.Match():
        meninfo = GetMenInfo()
        if IsClosedTo(meninfo.chengzhenx, meninfo.chengzheny, destcoord[0], destcoord[1], 100):
            return True
        else:
            logger.warning("目的地: %s [坐标]没有对比上" % desc)
    else:
        logger.warning("目的地: %s [图片]没有对比上" % desc)

    return False


# 移动到目的位置
def CoordMoveTo(shijitpic, mousecoord):
    if OpenShijieDitu():

        if not shijitpic.Match():
            logger.warning("当前世界地图对不上")
            return

        MouseMoveTo(mousecoord[0], mousecoord[1]), KongjianSleep()
        MouseLeftClick(), KongjianSleep()
        CloseShijieDitu()
        return True
    else:
        logger.warning("世界地图没打开")
        return False


# 移动到目的位置
def MoveTo(npcname, player):
    moveinfo = MoveSetting[npcname]
    if player.taskctx.latestmovepoint is None or time.time() > player.taskctx.latestmovepoint + 5.0:

        # 没有移动过或者超时
        logger.info("目标: %s 城镇位置: (%d,%d)  没有到达, 开始移动. 鼠标指向到 (%d, %d)" % (
            moveinfo.desc, moveinfo.destcoord[0],
            moveinfo.destcoord[1], moveinfo.mousecoord[0],
            moveinfo.mousecoord[1]))

        if CoordMoveTo(moveinfo.shijiepic, moveinfo.mousecoord):
            player.taskctx.latestmovepoint = time.time()
    else:
        logger.info("城镇移动中"), RanSleep(0.3)


# 到达选择角色页面
def GoToSelect(quad: Quardant):
    for i in range(3):
        if not IsManInSelectMap():
            logger.info("微调选择地图")
            QuadKeyDownMap[quad](), RanSleep(1)
            QuadKeyUpMap[quad](), KongjianSleep()
        else:
            break

    return IsManInSelectMap()


# 选择地图
def SelectMap(mapname):
    idx = IdxMapMap[mapname]
    while CurSelectId() != idx and IsManInSelectMap():
        logger.info("↑ 切换地图")
        PressKey(VK_CODE["up_arrow"]), KongjianSleep()

    return CurSelectId() == idx and IsManInSelectMap()


# 进图
def EnterMap(mapname, player):
    if SelectMap(mapname):
        PressKey(VK_CODE["spacebar"]), KongjianSleep()

        for i in range(10):
            if IsManInMap():
                from superai.superai import FirstInMap
                player.ChangeState(FirstInMap())
                return

            logger.info("等待进图... %d" % i), RanSleep(5)
    else:
        logger.warning("没有选择对地图")


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
    if not OpenTaskScene():
        logger.warning("没有出现任务框")
        return

    if not taskkzhuxian.Match():
        logger.warning("没有主线任务")
        return

    if IsWindowTop():
        logger.warning("有窗口弹出,退出领取主线任务")
        return

    pos = taskkzhuxian.Pos()
    MouseMoveTo(pos[0], pos[1]), KongjianSleep()
    MouseLeftClick(), KongjianSleep()


# 完成任务  (直接完成不能一直点,因为会有对话框弹出来,多次按任务对话框数据变0)
def SubmitTask(player):
    if player.taskctx.latestsubmitpoint is None or time.time() - player.taskctx.latestsubmitpoint > 8.0:

        if not OpenTaskScene():
            logger.warning("没有出现任务框")
            return

        if not taskok.Match():
            logger.warning("没有完成的主线任务")
            return

        if IsWindowTop():
            logger.warning("有窗口弹出,退出完成任务")
            return

        pos = taskok.Pos()
        MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        MouseLeftClick(), KongjianSleep()

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
            AcceptMain()
            return

        if TaskOk():
            logger.info("任务直接可完成")
            SubmitTask(player)
            return

        moveinfo = MoveSetting[dituname]
        if IsMoveToChengzhenPos(moveinfo.destpic, moveinfo.destcoord, moveinfo.desc):
            Clear()
            # 左右调整进入地图选择界面
            if GoToSelect(quadMap[dituname]):
                # 进入地图
                EnterMap(fubenname, player)
            else:
                logger.warning("没有进入选择地图")
        else:
            # 移动到指定位置
            MoveTo(dituname, player)

    return foo


# 是否移动到
def HasMoveTo(npcname):
    moveinfo = MoveSetting[npcname]
    return IsMoveToChengzhenPos(moveinfo.destpic, moveinfo.destcoord, moveinfo.desc)


# 返回一个访问指定对象的函数
def MeetNpcFoo(npcname):
    def foo(player, npcname=npcname):
        if not IsTaskaccept():
            logger.info("没有主线任务被接受")
            AcceptMain()
            return

        if TaskOk():
            logger.info("任务直接可完成")
            SubmitTask(player)
            return

        if npcname == "":
            logger.info("空任务")
            return

        if npcname == "赛利亚":
            # 返回角色再进入
            BackAndEnter()
            QuadKeyDownMap[Quardant.SHANG](), RanSleep(1)  # TODO 写死了
            QuadKeyUpMap[Quardant.SHANG](), KongjianSleep()
            PressKey(VK_CODE["spacebar"]), KongjianSleep()
        else:
            if HasMoveTo(npcname):
                Clear()
                logger.info("到达了指定位置,按space键")
                PressKey(VK_CODE["spacebar"]), KongjianSleep()
            else:
                MoveTo(npcname, player)

    return foo


# 是否在艾尔文防线
def IsinAierwenfnagxian():
    return wenziaierwenfangxian.Match()


# 是否在赫顿玛尔
def IsinHedunmaer():
    return wenzihedunmaer.Match() or wenzixihaian.Match()


# 是否在阿尔法营地
def IsinAerfayingdi():
    return wenziaerfayingdi.Match() or wenzianheicheng.Match()


# 转职任务
def 守护森林的战斗(player):
    SafeClear(player)

    if not DidPlotAccept("守护森林的战斗"):
        logger.info("任务没有接受, 接受任务")

        if not OpenTaskScene():
            logger.warning("没有出现任务框")
            return

        if not taskShouhusenlin.Match():
            logger.info("没有寻找守护森林任务")
            return

        pos = taskShouhusenlin.Pos()
        MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        MouseLeftClick(), KongjianSleep()

        while IsWindowTop():
            PressKey(VK_CODE["spacebar"]), KongjianSleep()

        # TODO  目前写死职业 . 要添加配置
        pic = None
        meninfo = GetMenInfo()
        if meninfo.zhuanzhiqian in ["圣职者"]:
            pic = zhuanzhiYoumozhe
        elif meninfo.zhuanzhiqian in ["魔枪士"]:
            pic = zhuanzhiAnqiangshi
        elif meninfo.zhuanzhiqian in ["守护者"]:
            pic = zhuanzhiPalading

        if pic is None:
            raise NotImplementedError("职业不支持")

        # 转职职业
        if not pic.Match():
            logger.warning("没有寻找到要转职的职业")
            return

        pos = pic.Pos()
        MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        MouseLeftClick(), RanSleep(1)

        while IsWindowTop():
            PressKey(VK_CODE["spacebar"]), KongjianSleep()

        if not zhuanzhiConfirm.Match():
            logger.warning("没有到寻找转职确认按钮")
            return

        # 确认
        pos = zhuanzhiConfirm.Pos()
        MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        MouseLeftClick(), KongjianSleep()
    else:
        AttacktaskFoo("暗黑雷鸣废墟")(player)


# 艾尔文防线 -> 赫顿玛尔   (艾尔文防线移动到边界点,下一个场景直接完成)
def 赫顿玛尔的骚乱(player):
    SafeClear(player)

    if IsinAierwenfnagxian():
        if not HasMoveTo("艾尔文南"):
            MoveTo("艾尔文南", player)
            return
        for i in range(30):
            if IsinHedunmaer():
                logger.info("到达了")
                break
            logger.info("按键前往赫顿玛尔")
            QuadKeyDownMap[Quardant.XIA](), RanSleep(1)
            QuadKeyUpMap[Quardant.XIA](), RanSleep(0.3)
    elif IsinHedunmaer():
        if not OpenTaskScene():
            logger.warning("没有出现任务框")
            return
        pos = taskdone.Pos()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)
    else:
        logger.warning("我在哪,我要到哪里去?")


# 赫顿玛尔 -> 阿尔法营地  (赫顿玛尔移动到边界点,下一个场景移动到NPC)
def 前往阿法利亚营地(player):
    SafeClear(player)

    if IsinHedunmaer():
        if not HasMoveTo("赫顿玛尔2"):
            MoveTo("赫顿玛尔2", player)
            return

        for i in range(30):
            if IsinAerfayingdi():
                logger.info("到达了")
                break

            logger.info("按键前往阿尔法营地")
            QuadKeyDownMap[Quardant.XIA](), RanSleep(1)
            QuadKeyUpMap[Quardant.XIA](), RanSleep(0.3)
    elif IsinAerfayingdi():
        MeetNpcFoo("洛巴赫3")(player)
    else:
        logger.warning("我在哪,我要到哪里去?")


# 阿尔法营地 -> 赫顿玛尔 (阿尔法营地移动到边界点,下一个场景移动到NPC)
def 战火虽已平息(player):
    SafeClear(player)

    if IsinAerfayingdi():
        if not HasMoveTo("阿尔法-赫顿玛尔"):
            MoveTo("阿尔法-赫顿玛尔", player)
            return
        for i in range(30):
            if IsinHedunmaer():
                logger.info("到达了")
                break
            logger.info("按键前往赫顿玛尔")
            QuadKeyDownMap[Quardant.SHANG](), RanSleep(1)
            QuadKeyUpMap[Quardant.SHANG](), RanSleep(0.3)
    elif IsinHedunmaer():
        MeetNpcFoo("斯卡迪")(player)
    else:
        logger.warning("我在哪,我要到哪里去?")


# 赫顿玛尔 -> 阿尔法营地 (赫顿玛尔移动到边界点,下一个场景移动到NPC)
def 被带走的俩人(player):
    SafeClear(player)

    if IsinHedunmaer():
        if not HasMoveTo("赫顿玛尔2"):
            MoveTo("赫顿玛尔2", player)
            return
        for i in range(30):
            if IsinAerfayingdi():
                logger.info("到达了")
                break
            logger.info("按键前往阿尔法营地")
            QuadKeyDownMap[Quardant.XIA](), RanSleep(1)
            QuadKeyUpMap[Quardant.XIA](), RanSleep(0.3)
    elif IsinAerfayingdi():
        MeetNpcFoo("帕丽丝")(player)
    else:
        logger.warning("我在哪,我要到哪里去?")


# 同名任务
def 长脚罗特斯():
    def foo(player):
        meninfo = GetMenInfo()
        if meninfo.level < 30:
            MeetNpcFoo("巴恩")(player)
        else:
            AttacktaskFoo("第二脊椎")(player)

    return foo


# 阿甘左香水
def 寻找阿甘左(player):
    SafeClear(player)

    if not aganzuowupin.Match():
        if not OpenBagScene():
            logger.warning("打开背包失败")
            return

        pos = bagScene.Pos()
        MouseMoveTo(pos[0] + XiaohaoPos[0], pos[1] + XiaohaoPos[1]), KongjianSleep()
        MouseLeftClick(), KongjianSleep()

        if not aganzuowupin2.Match():
            logger.warning("找不到爱丽丝的香料")
            return

        anganzuopos = aganzuowupin2.Pos()
        MouseMoveTo(anganzuopos[0], anganzuopos[1]), KongjianSleep()
        MouseLeftDown(), KongjianSleep()
        MouseMoveR(10, 10), KongjianSleep()
        MouseMoveTo(Wupin6Pos[0], Wupin6Pos[1]), KongjianSleep()
        MouseLeftUp(), KongjianSleep()
        MouseMoveR(30, 30), KongjianSleep()

        MouseMoveTo(pos[0] + ZhunangbeiPos[0], pos[1] + ZhunangbeiPos[1]), KongjianSleep()
        MouseLeftClick(), KongjianSleep()

        if not aganzuowupin.Match():
            logger.warning("拖动爱丽丝香料失败")
            return

        CloseBagScene()

    AttacktaskFoo("第二脊椎")(player)


fubenMap = {
    "格兰之森": ["幽暗密林", "猛毒雷鸣废墟", "冰霜幽暗密林", "格拉卡", "烈焰格拉卡", "烈焰格拉卡", "暗黑雷鸣废墟"],
    "天空之城": ["龙人之塔", "人偶玄关", "石巨人塔", "黑暗悬廊", "城主宫殿", "悬空城"],
    "天帷巨兽": ["GBL教的神殿", "树精丛林", "炼狱", "极昼", "第一脊椎", "天帷禁地", "第二脊椎"],
    "阿法利亚": ["浅栖之地", "蜘蛛洞穴", "蜘蛛王国", "英雄冢", "暗精灵墓地", "熔岩穴", "暗黑城入口", "暗黑城"],
    "诺伊佩拉": ["暴君的祭坛", "黄金矿洞"],
}

quadMap = {
    "格兰之森": Quardant.ZUO,
    "天空之城": Quardant.YOU,
    "天帷巨兽": Quardant.YOU,
    "阿法利亚": Quardant.YOU,
    "诺伊佩拉": Quardant.YOU,
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

    # 24-32:
    "GBL教的神殿": 0,
    "树精丛林": 1,
    "炼狱": 2,
    "极昼": 3,
    "第一脊椎": 4,
    "天帷禁地": 5,  # TODO 剧情变化了,下标也变啦
    "第二脊椎": 5,

    # 32
    "浅栖之地": 0,
    "蜘蛛洞穴": 1,
    "蜘蛛王国": 2,
    "英雄冢": 3,
    "暗精灵墓地": 4,
    "熔岩穴": 4,  # TODO  = =
    "暗黑城入口": 6,
    "暗黑城": 7,

    # 37
    "暴君的祭坛": 0,
    "黄金矿洞": 1,
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
    "寻找阿甘左": 寻找阿甘左,
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
    "忐忑不安的人们": MeetNpcFoo("洛巴赫2"),
    "前往阿法利亚营地": 前往阿法利亚营地,
    "暗精灵的传令使": MeetNpcFoo("克伦特"),
    "调查传染病": AttacktaskFoo("浅栖之地"),
    "寻找炼金术师": AttacktaskFoo("浅栖之地"),
    "炼金术师摩根": AttacktaskFoo("浅栖之地"),
    "好斗者鲁埃尔": MeetNpcFoo("鲁埃尔"),
    "与鲁埃尔同行": AttacktaskFoo("蜘蛛洞穴"),
    "捉蜘蛛": AttacktaskFoo("蜘蛛洞穴"),
    "寻找专家": MeetNpcFoo("洛巴赫3"),
    "莎兰与赛丽亚": MeetNpcFoo("帕丽丝"),
    "无法合作的合作者": AttacktaskFoo("蜘蛛洞穴"),
    "蜘蛛洞穴的密径": AttacktaskFoo("蜘蛛王国"),
    "蜘蛛王国": AttacktaskFoo("蜘蛛王国"),
    "安吉丽娜的突变": AttacktaskFoo("蜘蛛王国"),
    "向暗黑城前进": AttacktaskFoo("英雄冢"),
    "复活的暗精灵英雄们": AttacktaskFoo("英雄冢"),
    "埋葬在岁月中": AttacktaskFoo("英雄冢"),
    "探索墓地": AttacktaskFoo("暗精灵墓地"),
    "认识克伦特的女人": AttacktaskFoo("暗精灵墓地"),
    "封印之门的另一边": AttacktaskFoo("暗精灵墓地"),
    "穿过熔岩": AttacktaskFoo("熔岩穴"),
    "前往暗黑城入口": AttacktaskFoo("暗黑城入口"),
    "前往暗黑城": AttacktaskFoo("暗黑城"),
    "梅娅女王": MeetNpcFoo("梅娅女王"),
    "传达消息": MeetNpcFoo("克伦特"),
    "喜讯": MeetNpcFoo("洛巴赫3"),
    "战火虽已平息": 战火虽已平息,
    "邪恶的暗流": MeetNpcFoo("艾丽丝"),
    "被带走的俩人": 被带走的俩人,
    "了解情况": MeetNpcFoo("梅娅女王"),
    "夏普伦长老的要求": MeetNpcFoo("王宫外"),
    "神秘的暗精灵": AttacktaskFoo("暴君的祭坛"),
    "寻找真正的祭坛": AttacktaskFoo("暴君的祭坛"),
    "充满黄金的地方": AttacktaskFoo("黄金矿洞"),
    "维迪尔的要求": AttacktaskFoo("黄金矿洞"),
}


def main():
    pass


if __name__ == '__main__':
    main()
