import os
import queue
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

from superai.equip import OpenBagScene, ZhunangbeiPos, XiaohaoPos, bagScene, CloseBagScene
from superai.location import IsinAierwenfnagxian, IsinHedunmaer, IsinAerfayingdi, Location, IsinSailiya, \
    IsInJingxiangalade
from superai.flannfind import Picture, GetImgDir
from superai.gameapi import GetMenInfo, IsClosedTo, IsManInSelectMap, Quardant, QuadKeyDownMap, QuadKeyUpMap, \
    CurSelectId, GetTaskObj, IsManInMap, IsEscTop, GetAccptedTaskObj, IsWindowTop, Clear, Openesc, SafeClear, \
    GetQuadrant, QuardantMap
from superai.yijianshu import PressKey, VK_CODE, RanSleep, MouseMoveTo, MouseLeftClick, MouseLeftDown, MouseMoveR, \
    MouseLeftUp, KongjianSleep, LanSleep, ReleaseAllKey

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
zhuanzhiQigong = Picture(GetImgDir() + "zhuanzhi_qigong.png")
zhuanzhiJianying = Picture(GetImgDir() + "zhuanzhi_jianying.png")
zhuanzhiYuanneng = Picture(GetImgDir() + "zhuanzhi_yuannneng.png")
zhuanzhiConfirm = Picture(GetImgDir() + "zhuanzhi_confirm.png")
dituHedunmaer = Picture(GetImgDir() + "ditu_hedunmaer.png")
dituHedunmaer3 = Picture(GetImgDir() + "ditu_hedunmaer3.png")
dituAfaliya = Picture(GetImgDir() + "ditu_afaliya.png")
taskdone = Picture(GetImgDir() + "task_done.png")
aganzuowupin = Picture(GetImgDir() + "aganzuo_wupin.png", 243, 560, 28, 28)
aganzuowupin2 = Picture(GetImgDir() + "aganzuo_wupin2.png")

Wupin6Pos = (255, 577)


# 移动信息
class MoveInfo:
    def __init__(self, destcoord, mousecoord):
        # 目的地位置的 场景图片 (判断是否移动到)
        self.destpic = Picture(GetImgDir() + destcoord[0])
        # 目的地城镇坐标 (判断是否移动到)
        self.destcoord = (destcoord[1], destcoord[2])

        # 移动到世界地图哪个位置可以到达目的地
        self.mousecoord = mousecoord


# NPC信息
NpcInfos = {
    # 1. 目标场景截图 + 城镇坐标,判断是否到达
    # 2. 世界地图特征 + 鼠标移动地图的的绝对坐标

    "艾尔文防线": {
        "check": IsinAierwenfnagxian,
        "pic": Picture(GetImgDir() + "shijie_aierwenfangxian.png"),
        "npcs": {
            "林纳斯": MoveInfo(destcoord=("ditu_linnasi.png", 1234, 196), mousecoord=(362, 415)),
            "艾尔文南": MoveInfo(destcoord=("ditu_aierwennan.png", 770, 251), mousecoord=(400, 504)),
            "格兰之森": MoveInfo(destcoord=("ditu_gelanzhisen.png", 161, 256), mousecoord=(209, 424)),

            # 雪山
            "敏泰": MoveInfo(destcoord=("ditu_mintai.png", 821, 821), mousecoord=(565, 183)),
            "巴尔雷娜": MoveInfo(destcoord=("ditu_baerleina.png", 453, 400), mousecoord=(543, 138)),
            "雪山": MoveInfo(destcoord=("ditu_xueshan.png", 183, 428), mousecoord=(468, 138)),
            "奥尔卡": MoveInfo(destcoord=("ditu_aoerka.png", 1541, 715), mousecoord=(609, 172)),
            "雷诺": MoveInfo(destcoord=("ditu_leinuo.png", 755, 400), mousecoord=(561, 140)),
        }
    },

    "赫顿玛尔": {
        "check": IsinHedunmaer,
        "pic": Picture(GetImgDir() + "shijie_hedunmaer.png"),
        "npcs": {
            "月光酒馆": MoveInfo(destcoord=("ditu_yueguangjiuguan.png", 758, 216), mousecoord=(189, 219)),
            "挡路的帝国军队": MoveInfo(destcoord=("ditu_dangludiguo.png", 2308, 319), mousecoord=(612, 285)),
            "罗杰": MoveInfo(destcoord=("ditu_luojie.png", 1190, 183), mousecoord=(560, 263)),
            "诺顿": MoveInfo(destcoord=("ditu_tiankongzhicheng.png", 331, 161), mousecoord=(668, 265)),
            "天空之城": MoveInfo(destcoord=("ditu_tiankongzhicheng.png", 727, 204), mousecoord=(705, 280)),
            "洛巴赫": MoveInfo(destcoord=("ditu_luobahe.png", 1433, 176), mousecoord=(345, 333)),
            "洛巴赫2": MoveInfo(destcoord=("ditu_luobahe2.png", 658, 215), mousecoord=(355, 237)),
            "巴恩": MoveInfo(destcoord=("ditu_baen.png", 2259, 177), mousecoord=(610, 262)),
            "莎兰": MoveInfo(destcoord=("ditu_shalan.png", 587, 222), mousecoord=(562, 188)),
            "艾丽丝": MoveInfo(destcoord=("ditu_ailisi.png", 283, 222), mousecoord=(544, 188)),
            "索西雅": MoveInfo(destcoord=("ditu_suoxiya.png", 125, 266), mousecoord=(151, 212)),
            "凯丽": MoveInfo(destcoord=("ditu_kaili.png", 2703, 188), mousecoord=(410, 335)),
            "斯卡迪": MoveInfo(destcoord=("ditu_sikadi.png", 440, 205), mousecoord=(334, 234)),
            "奥菲利亚": MoveInfo(destcoord=("ditu_aofeiliya.png", 860, 183), mousecoord=(533, 370)),
            "卡坤": MoveInfo(destcoord=("ditu_kakun.png", 1077, 175), mousecoord=(543, 367)),
            "天帷巨兽": MoveInfo(destcoord=("ditu_tianzhuijushou.png", 712, 306), mousecoord=(647, 399)),
            "赫顿玛尔": MoveInfo(destcoord=("ditu_hedunmaer2.png", 1430, 188), mousecoord=(346, 335)),
            "阿甘左": MoveInfo(destcoord=("ditu_aganzuo.png", 1096, 188), mousecoord=(210, 213)),
            "后街": MoveInfo(destcoord=("ditu_houjie.png", 578, 244), mousecoord=(221, 300)),
            "布告": MoveInfo(destcoord=("ditu_bugaolan.png", 926, 213), mousecoord=(320, 339)),
            "赫顿玛尔2": MoveInfo(destcoord=("ditu_hedunmaer2.png", 1254, 417), mousecoord=(336, 372)),
            "赫顿玛尔3": MoveInfo(destcoord=("ditu_hedunmaer3.png", 356, 207), mousecoord=(290, 338)),
            "博肯": MoveInfo(destcoord=("ditu_boken2.png", 1120, 188), mousecoord=(329, 335)),
            "马琳·基希卡": MoveInfo(destcoord=("ditu_malin.png", 230, 187), mousecoord=(503, 370)),
            "后街2": MoveInfo(destcoord=("ditu_houjie2.png", 272, 243), mousecoord=(172, 367)),
            "诺斯玛尔": MoveInfo(destcoord=("ditu_nuosimaer.png", 146, 274), mousecoord=(66, 366)),
            "歌兰蒂斯·格拉西亚": MoveInfo(destcoord=("ditu_gelandisi2.png", 2415, 176), mousecoord=(396, 333)),
            "麦瑟·莫纳亨": MoveInfo(destcoord=("ditu_maise.png", 291, 223), mousecoord=(200, 291)),
            "赫顿玛尔-镜像": MoveInfo(destcoord=("ditu_hedunmaer_jingxiang.png", 169, 239), mousecoord=(191, 298)),
        }
    },
    "阿法利亚": {
        "check": IsinAerfayingdi,
        "pic": Picture(GetImgDir() + "shijie_aerfa.png"),
        "npcs": {
            "洛巴赫3": MoveInfo(destcoord=("ditu_luobahe3.png", 312, 160), mousecoord=(277, 261)),
            "克伦特": MoveInfo(destcoord=("ditu_kelunte.png", 459, 135), mousecoord=(381, 259)),
            "阿法利亚": MoveInfo(destcoord=("ditu_afaliya2.png", 741, 227), mousecoord=(522, 281)),
            "鲁埃尔": MoveInfo(destcoord=("ditu_luaier.png", 760, 123), mousecoord=(407, 257)),
            "帕丽丝": MoveInfo(destcoord=("ditu_palisi.png", 521, 160), mousecoord=(302, 261)),
            "梅娅女王": MoveInfo(destcoord=("ditu_meiyanvwang.png", 482, 219), mousecoord=(386, 489)),
            "阿尔法-赫顿玛尔": MoveInfo(destcoord=("ditu_aerfahedunmaer.png", 290, 81), mousecoord=(220, 180)),
            "王宫外": MoveInfo(destcoord=("ditu_wanggongwai.png", 1103, 302), mousecoord=(501, 508)),
            "诺伊佩拉": MoveInfo(destcoord=("ditu_nuoyipeila.png", 982, 182), mousecoord=(580, 425)),
            "米内特": MoveInfo(destcoord=("ditu_mineite.png", 1228, 223), mousecoord=(486, 405)),
            "夏普伦": MoveInfo(destcoord=("ditu_xiapulun.png", 316, 215), mousecoord=(367, 488)),
            "米内特2": MoveInfo(destcoord=("ditu_mineite2.png", 1001, 141), mousecoord=(424, 260)),
            "米内特3": MoveInfo(destcoord=("ditu_mineite3.png", 1229, 231), mousecoord=(486, 407)),
        }
    },
    "镜像阿拉德": {
        "check": IsInJingxiangalade,
        "pic": Picture(GetImgDir() + "shijie_jingxiangalade.png"),
        "npcs": {
            "镜像-赫顿玛尔": MoveInfo(destcoord=("ditu_jingxiang_hedunmaer.png", 1056, 299), mousecoord=(588, 291)),
            "阿甘左2": MoveInfo(destcoord=("ditu_aganzuo2.png", 907, 135), mousecoord=(574, 257)),
            "青之守护者塔娜": MoveInfo(destcoord=("ditu_qingzhishouhu.png", 900, 164), mousecoord=(352, 294)),
            "亚诺法森林": MoveInfo(destcoord=("ditu_yanuofasenlin.png", 328, 287), mousecoord=(232, 297)),
            "摩根": MoveInfo(destcoord=("ditu_mogen.png", 332, 247), mousecoord=(316, 291)),
            "帕丽丝2": MoveInfo(destcoord=("ditu_palisi2.png", 803, 195), mousecoord=(495, 159)),
            "厄运之城": MoveInfo(destcoord=("ditu_eyun.png", 362, 228), mousecoord=(376, 176)),
            "炼金术师摩根": MoveInfo(destcoord=("ditu_mogen2.png", 352, 244), mousecoord=(316, 296)),
        }
    }
}


# 大地图有向图
class Graph:
    def __init__(self, V):
        # 顶点数量
        self.V = V

        # 边数量
        self.E = 0

        # 邻接表
        self.adj = []

        # 走法函数. v,w tuple 作为key, foo作为map
        self.fooMap = {}

        for i in range(V):
            nears = []
            self.adj.append(nears)

    def AddEdge(self, v, w, foo):
        self.adj[v].append(w)
        self.E += 1
        self.fooMap[v, w] = foo

    def bfs(self):
        pass

    def __str__(self):
        pass


Mapid = {
    "艾尔文防线": 0,
    "赫顿玛尔": 1,
    "阿法利亚": 2,
    "镜像阿拉德": 3,
}


def InitGraph():
    graph = Graph(10)

    def 艾尔文防线_赫顿玛尔(player):
        if IsinAierwenfnagxian():
            if not HasMoveTo("艾尔文南"):
                MoveTo("艾尔文南", player)
                return
            else:
                for i in range(10):
                    if IsinHedunmaer():
                        Clear()
                        player.taskctx.latestmovepoint = None
                        break
                    QuadKeyDownMap[Quardant.XIA](), RanSleep(1)
                    QuadKeyUpMap[Quardant.XIA](), RanSleep(0.3)
        else:
            logger.warning("我在哪儿?")

    def 赫顿玛尔_艾尔文防线(player):
        if IsinHedunmaer():
            if not HasMoveTo("赫顿玛尔3"):
                MoveTo("赫顿玛尔3", player)
                return
            else:
                for i in range(10):
                    if IsinAierwenfnagxian():
                        Clear()
                        player.taskctx.latestmovepoint = None
                        break
                    QuadKeyDownMap[Quardant.SHANG](), RanSleep(1)
                    QuadKeyUpMap[Quardant.SHANG](), RanSleep(0.3)
        else:
            logger.warning("我在哪儿?")

    def 赫顿玛尔_阿法利亚(player):
        if IsinHedunmaer():
            if not HasMoveTo("赫顿玛尔2"):
                MoveTo("赫顿玛尔2", player)
                return
            else:
                for i in range(10):
                    if IsinAerfayingdi():
                        Clear()
                        player.taskctx.latestmovepoint = None
                        break
                    QuadKeyDownMap[Quardant.XIA](), RanSleep(1)
                    QuadKeyUpMap[Quardant.XIA](), RanSleep(0.3)
        else:
            logger.warning("我在哪儿?")

    def 阿法利亚_赫顿玛尔(player):
        if IsinAerfayingdi():
            if not HasMoveTo("阿尔法-赫顿玛尔"):
                MoveTo("阿尔法-赫顿玛尔", player)
                return
            else:
                for i in range(10):
                    if IsinHedunmaer():
                        Clear()
                        player.taskctx.latestmovepoint = None
                        break
                    QuadKeyDownMap[Quardant.SHANG](), RanSleep(1)
                    QuadKeyUpMap[Quardant.SHANG](), RanSleep(0.3)
        else:
            logger.warning("我在哪儿?")

    def 赫顿玛尔_镜像(player):
        if IsinHedunmaer():
            if not HasMoveTo("赫顿玛尔-镜像"):
                MoveTo("赫顿玛尔-镜像", player)
                return
            else:
                for i in range(10):
                    if IsInJingxiangalade():
                        Clear()
                        player.taskctx.latestmovepoint = None
                        break
                    QuadKeyDownMap[Quardant.SHANG](), RanSleep(1)
                    QuadKeyUpMap[Quardant.SHANG](), RanSleep(0.3)
        else:
            logger.warning("我在哪儿?")

    def 镜像_赫顿玛尔(player):
        if IsinHedunmaer():
            if not HasMoveTo("镜像-赫顿玛尔"):
                MoveTo("镜像-赫顿玛尔", player)
                return
            else:
                for i in range(10):
                    if IsinHedunmaer():
                        Clear()
                        player.taskctx.latestmovepoint = None
                        break
                    QuadKeyDownMap[Quardant.XIA](), RanSleep(1)
                    QuadKeyUpMap[Quardant.XIA](), RanSleep(0.3)
        else:
            logger.warning("我在哪儿?")

    graph.AddEdge(Mapid["艾尔文防线"], Mapid["赫顿玛尔"], 艾尔文防线_赫顿玛尔)
    graph.AddEdge(Mapid["赫顿玛尔"], Mapid["艾尔文防线"], 赫顿玛尔_艾尔文防线)

    graph.AddEdge(Mapid["赫顿玛尔"], Mapid["阿法利亚"], 赫顿玛尔_阿法利亚)
    graph.AddEdge(Mapid["阿法利亚"], Mapid["赫顿玛尔"], 阿法利亚_赫顿玛尔)

    graph.AddEdge(Mapid["赫顿玛尔"], Mapid["镜像阿拉德"], 赫顿玛尔_镜像)
    graph.AddEdge(Mapid["镜像阿拉德"], Mapid["赫顿玛尔"], 镜像_赫顿玛尔)

    return graph


graph = InitGraph()


class MapPaths:
    def __init__(self, g: Graph, s):
        self.marked = [False] * g.V
        self.edgeTo = [0] * g.V
        self.s = s
        self.g = g

        self.bfs(g, s)

    def bfs(self, g, s):
        q = queue.Queue()
        q.put(s)

        while q.qsize() != 0:
            v = q.get()

            for w in g.adj[v]:
                if not self.marked[w]:
                    self.edgeTo[w] = v
                    self.marked[w] = True
                    q.put(w)

    def HasPathTo(self, v: int):
        return self.marked[v]

    def PathTo(self, v):
        # 移动的路径点
        result = []

        # 移动的函数
        foos = []

        if not self.HasPathTo(v):
            return result, foos

        # 终点 .. 起点
        x = v
        while x != self.s:
            result.append(x)
            x = self.edgeTo[x]
        result.append(self.s)

        # 反转, 起点 .. 终点
        result = list(reversed(result))
        for i in range(len(result) - 1):
            foos.append(self.g.fooMap[result[i], result[i + 1]])

        return result, foos


# 获得大地图的路径
def GetMapPaths(s, v):
    mapPaths = MapPaths(graph, s)
    return mapPaths.PathTo(v)


# 任务上下文计时
class TaskCtx:
    def __init__(self):
        # 上一次小地图按键的时间点(对话NPC)
        self.latestmovepoint = None

        # 上一次完成任务单击时间
        self.latestsubmitpoint = None

        # 上一次接受任务单击时间
        self.latestacceptpoint = None

    def Clear(self):
        pass
        # self.latestmovepoint = None
        # self.latestsubmitpoint = None


# 打开select
def OpenSelect():
    if not gamebegin.Match():
        logger.info("寻找游戏开始按钮")
        pos = selectmen.Pos()
        MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        MouseLeftClick(), RanSleep(1.5)

    return gamebegin.Match()


# 到赛利亚
def BackAndEnter():
    if not Openesc():
        logger.warning("打开esc失败")
        return False

    if not OpenSelect():
        logger.warning("返回选择角色失败")

    PressKey(VK_CODE["spacebar"]), KongjianSleep()

    return True


# 打开任务栏
def OpenTaskScene():
    Clear()

    if not taskScene.Match():
        logger.info("F1打开任务列表")
        PressKey(VK_CODE["F1"]), LanSleep()
    return taskScene.Match()


# 打开世界地图
def OpenShijieDitu():
    Clear()

    if not shijiedituScene.Match():
        logger.info("打开世界地图")
        PressKey(VK_CODE["n"]), LanSleep()

    return shijiedituScene.Match()


# 关闭世界地图
def CloseShijieDitu():
    if shijiedituScene.Match():
        logger.info("关闭世界地图")
        PressKey(VK_CODE["n"]), KongjianSleep()


# 获取移动到位置的信息
def GetDestinfo(destname):
    destinfo = None

    for k, v in NpcInfos.items():
        if destname in v["npcs"].keys():
            destinfo = v["npcs"][destname]
            break

    if destinfo is None:
        raise NotImplementedError("地图尚未支持: %s" % destname)

    return destinfo


# 获取移动到位置的检查函数
def GetDestCheckFoo(destname):
    destgcheckFoo = None

    for k, v in NpcInfos.items():
        if destname in v["npcs"].keys():
            destgcheckFoo = v["check"]
            break
    if destgcheckFoo is None:
        raise NotImplementedError("地图尚未支持: %s" % destname)

    return destgcheckFoo


# 获取移动到位置的世界地图位置
def GetDestShijie(destname):
    shijie = None

    for k, v in NpcInfos.items():
        if destname in v["npcs"].keys():
            shijie = k
            break
    if shijie is None:
        raise NotImplementedError("地图尚未支持: %s" % destname)

    return shijie


# 获取移动到位置所用的世界地图
def GetDestShijiePic(destname):
    pic = None

    for k, v in NpcInfos.items():
        if destname in v["npcs"].keys():
            pic = v["pic"]
            break
    if pic is None:
        raise NotImplementedError("地图尚未支持: %s" % destname)

    return pic


# 是否移动城镇的位置
def IsMoveToChengzhenPos(destpic, destcoord, desc):
    if destpic.Match():
        meninfo = GetMenInfo()
        if IsClosedTo(meninfo.chengzhenx, meninfo.chengzheny, destcoord[0], destcoord[1], 10):
            return True
        elif IsClosedTo(meninfo.chengzhenx, meninfo.chengzheny, destcoord[0], destcoord[1], 100):
            # TODO 判断语句调整了位置

            # 强制移动2s 靠近
            logger.warning("目的地: %s  在100范围内, 再移动一会会" % desc)

            latestdown = None

            for i in range(50):
                meninfo = GetMenInfo()
                if IsClosedTo(meninfo.chengzhenx, meninfo.chengzheny, destcoord[0], destcoord[1], 10):
                    logger.info("目的地: %s 到达了" % desc)
                    break

                quad, _ = GetQuadrant(meninfo.chengzhenx, meninfo.chengzheny, destcoord[0], destcoord[1])

                if latestdown:
                    latestDecompose = QuardantMap[latestdown]
                    currentDecompose = QuardantMap[quad]

                    # 上次的按键在本次方向中没找到就弹起
                    for keydown in latestDecompose:
                        if keydown not in currentDecompose:
                            QuadKeyUpMap[keydown]()

                    QuadKeyDownMap[quad]()
                    latestdown = quad
                else:
                    QuadKeyDownMap[quad]()
                    latestdown = quad

                RanSleep(0.02)

            ReleaseAllKey()

            meninfo = GetMenInfo()
            return IsClosedTo(meninfo.chengzhenx, meninfo.chengzheny, destcoord[0], destcoord[1], 10)
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
def MoveTo(destname, player):
    destinfo = GetDestinfo(destname)

    if player.taskctx.latestmovepoint is None or time.time() > player.taskctx.latestmovepoint + 10.0:
        # 没有移动过或者超时
        logger.info("目标: %s 城镇位置: (%d,%d)  没有到达, 开始移动. 鼠标指向到 (%d, %d)" % (
            destname, destinfo.destcoord[0],
            destinfo.destcoord[1], destinfo.mousecoord[0],
            destinfo.mousecoord[1]))

        shijiepic = GetDestShijiePic(destname)
        if CoordMoveTo(shijiepic, destinfo.mousecoord):
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
def SelectMap(idx):
    while CurSelectId() != idx and IsManInSelectMap():
        logger.info("↑ 切换地图")
        PressKey(VK_CODE["up_arrow"]), KongjianSleep()

    return CurSelectId() == idx and IsManInSelectMap()


# 进图
def EnterMap(idx, player):
    if SelectMap(idx):
        PressKey(VK_CODE["spacebar"]), KongjianSleep()

        for i in range(10):
            if IsManInMap():
                from superai.superai import FirstInMap
                player.ChangeState(FirstInMap())
                return

            logger.info("等待进图... %d" % i), RanSleep(0.5)
    else:
        logger.warning("没有选择对地图")


# 是否有剧情任务
def HasPlot():
    tasks = GetTaskObj()
    for v in tasks:
        if v.name in plotMap.keys():
            return True
    return False


# 是否有指定id的任务
def HasSpecifyAccept(i):
    tasks = GetTaskObj()
    for v in tasks:
        if v.id == i:
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
        if not v.needdo and v.type2 != 0x1A:
            return True
    return False


# 领取主线任务
def AcceptMain(player):
    if player.taskctx.latestacceptpoint is None or time.time() - player.taskctx.latestacceptpoint > 8.0:
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

        player.taskctx.latestacceptpoint = time.time()
    else:
        PressKey(VK_CODE["esc"]), KongjianSleep()
        logger.warning("接受任务不能多次点击,本次啥都不做")


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
        PressKey(VK_CODE["esc"]), KongjianSleep()
        logger.warning("完成任务不能多次点击,本次啥都不做")


# 是否移动到
def HasMoveTo(destname):
    destinfo = GetDestinfo(destname)
    return IsMoveToChengzhenPos(destinfo.destpic, destinfo.destcoord, destname)


# 获取指定地图的信息
def GetMapInfo(fubenname):
    mapname, quad, idx = None, None, None

    for k, v in FubenInfos.items():
        if fubenname in v["fubens"].keys():
            mapname = k
            quad = v["quad"]
            idx = v["fubens"][fubenname]
            break

    if mapname is None or quad is None or idx is None:
        raise NotImplementedError("副本数据未设置好: %s" % fubenname)

    return mapname, quad, idx


# 返回一个打指定地图的函数
def AttacktaskFoo(fubenname):
    def foo(player, fubenname=fubenname):
        # 获取副本相关的信息 1. 地图名称 2. 方向
        mapname, quad, idx = GetMapInfo(fubenname)
        if not IsTaskaccept():
            logger.info("没有主线任务被接受")
            AcceptMain(player)
            return

        if TaskOk():
            logger.info("任务直接可完成")
            SubmitTask(player)
            return

        if HasMoveTo(mapname):
            Clear()
            player.taskctx.latestmovepoint = None

            logger.info("到达了指定位置,选择地图")

            if GoToSelect(quad):
                # 进入地图
                EnterMap(idx, player)
            else:
                logger.warning("没有进入选择地图")
        else:

            # 赛丽亚房间就退出来
            if IsinSailiya():
                meninfo = GetMenInfo()
                if meninfo.level <= 20 and mapname in ["林纳斯", "艾尔文南", "格兰之森"]:
                    logger.info("直接移动过去")
                else:
                    QuadKeyDownMap[Quardant.XIA](), RanSleep(1)
                    QuadKeyUpMap[Quardant.XIA](), RanSleep(0.3)
                    return

            destcheckFoo = GetDestCheckFoo(mapname)
            if not destcheckFoo():

                loc = Location()
                location = loc.GetLocation()
                if location == "":
                    Clear()
                    logger.warning("截图无法判断当前在哪里")
                    return

                shijie = GetDestShijie(mapname)
                paths, foos = GetMapPaths(Mapid[location], Mapid[shijie])

                if len(paths) < 2:
                    logger.warning("判断当前地图正确但是规划不正确")
                    return

                if paths[0] == Mapid[shijie]:
                    logger.warning("当前路径已达到,不用规划")
                    return

                foos[0](player)

            else:
                MoveTo(mapname, player)

    return foo


# 返回一个访问指定对象的函数
def MeetNpcFoo(destname):
    def foo(player, destname=destname):
        if not IsTaskaccept():
            logger.info("没有主线任务被接受")
            AcceptMain(player)
            return

        if TaskOk():
            logger.info("任务直接可完成")
            SubmitTask(player)
            return

        if destname == "":
            logger.info("空任务")
            return

        if destname == "赛丽亚":
            # 返回角色再进入
            if BackAndEnter():

                meninfo = GetMenInfo()
                if not IsClosedTo(meninfo.chengzhenx, meninfo.chengzheny, 447, 163, 20):
                    for i in range(3):
                        meninfo = GetMenInfo()

                        if not IsClosedTo(meninfo.chengzhenx, meninfo.chengzheny, 447, 163, 20):
                            QuadKeyDownMap[Quardant.SHANG](), RanSleep(1)  # TODO 写死了
                            QuadKeyUpMap[Quardant.SHANG](), KongjianSleep()

                PressKey(VK_CODE["spacebar"]), KongjianSleep()
        else:

            if HasMoveTo(destname):
                Clear()
                player.taskctx.latestmovepoint = None
                logger.info("到达了指定位置,按space键")

                if destname == "马琳·基希卡":
                    QuadKeyDownMap[Quardant.ZUO](), RanSleep(0.5)
                    QuadKeyUpMap[Quardant.ZUO](), RanSleep(0.5)

                meninfo = GetMenInfo()
                destinfo = GetDestinfo(destname)
                if not IsClosedTo(meninfo.chengzhenx, meninfo.chengzheny, destinfo.destcoord[0], destinfo.destcoord[1],
                                  2):
                    # 对话角色 微调整
                    quad, _ = GetQuadrant(meninfo.chengzhenx, meninfo.chengzheny, destinfo.destcoord[0],
                                          destinfo.destcoord[1])
                    QuadKeyDownMap[quad](), RanSleep(0.05)
                    QuadKeyUpMap[quad](), RanSleep(0.05)

                PressKey(VK_CODE["spacebar"]), KongjianSleep()

                if destname == "巴尔雷娜":
                    if HasSpecifyAccept(3286):
                        global meetbaerleina
                        meetbaerleina = True

            else:

                # 赛丽亚房间就退出来
                if IsinSailiya():
                    meninfo = GetMenInfo()
                    if meninfo.level <= 20 and destname in ["林纳斯", "艾尔文南", "格兰之森"]:
                        logger.info("直接移动过去")
                    else:
                        QuadKeyDownMap[Quardant.XIA](), RanSleep(1)
                        QuadKeyUpMap[Quardant.XIA](), RanSleep(0.3)
                        return

                destcheckFoo = GetDestCheckFoo(destname)
                if not destcheckFoo():

                    loc = Location()
                    location = loc.GetLocation()
                    if location == "":
                        Clear()
                        logger.warning("截图无法判断当前在哪里")
                        return

                    shijie = GetDestShijie(destname)
                    paths, foos = GetMapPaths(Mapid[location], Mapid[shijie])

                    if len(paths) < 2:
                        logger.warning("判断当前地图正确但是规划不正确")
                        return

                    if paths[0] == Mapid[shijie]:
                        logger.warning("当前路径已达到,不用规划")
                        return

                    foos[0](player)
                else:
                    MoveTo(destname, player)

    return foo


# 15级1转
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
        MouseLeftClick(), RanSleep(1)

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
        elif meninfo.zhuanzhiqian in ["格斗家"]:
            pic = zhuanzhiQigong
        elif meninfo.zhuanzhiqian in ["鬼剑士"]:
            pic = zhuanzhiJianying
        elif meninfo.zhuanzhiqian in ["枪剑士"]:
            pic = zhuanzhiYuanneng

        if pic is None:
            raise NotImplementedError("职业不支持: %s" % meninfo.zhuanzhiqian)

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


# 同名任务
def 长脚罗特斯():
    def foo(player):
        meninfo = GetMenInfo()
        if meninfo.level < 30:
            MeetNpcFoo("巴恩")(player)
        else:
            AttacktaskFoo("第二脊椎")(player)

    return foo


meetbaerleina = False


# 同名任务
def 雪山隐藏的秘密():
    def foo(player):
        if not meetbaerleina:
            MeetNpcFoo("巴尔雷娜")(player)
        else:
            MeetNpcFoo("奥尔卡")(player)

    return foo


# 同名任务
def 营救赛丽亚():
    def foo(player):
        meninfo = GetMenInfo()
        if meninfo.level < 48:
            AttacktaskFoo("格拉卡")(player),
        else:
            AttacktaskFoo("炽晶森林")(player),

    return foo


# 30 阿甘左香水. 要放物品
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
            logger.warning("找不到艾丽丝的香料")
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
            logger.warning("拖动艾丽丝香料失败")
            return

        CloseBagScene()

    AttacktaskFoo("第二脊椎")(player)


# 副本信息
FubenInfos = {
    "格兰之森": {
        "quad": Quardant.ZUO,
        "fubens": {
            "幽暗密林": 0,
            "雷鸣废墟": 1,
            "猛毒雷鸣废墟": 2,
            "冰霜幽暗密林": 3,
            "格拉卡": 3,
            "烈焰格拉卡": 4,
            "暗黑雷鸣废墟": 6
        }
    },
    "天空之城": {
        "quad": Quardant.YOU,
        "fubens": {
            "龙人之塔": 0,
            "人偶玄关": 1,
            "石巨人塔": 2,
            "黑暗悬廊": 3,
            "城主宫殿": 4,
            "悬空城": 5,
        }
    },
    "天帷巨兽": {
        "quad": Quardant.YOU,
        "fubens": {
            "GBL教的神殿": 0,
            "树精丛林": 1,
            "炼狱": 2,
            "极昼": 3,
            "第一脊椎": 4,
            "天帷禁地": 5,
            "第二脊椎": 5,
        }
    },
    "阿法利亚": {
        "quad": Quardant.YOU,
        "fubens": {
            "浅栖之地": 0,
            "蜘蛛洞穴": 1,
            "蜘蛛王国": 2,
            "英雄冢": 3,
            "暗精灵墓地": 4,
            "熔岩穴": 4,
            "暗黑城入口": 6,
            "暗黑城": 7,
        }
    },
    "诺伊佩拉": {
        "quad": Quardant.YOU,
        "fubens": {
            "暴君的祭坛": 0,
            "黄金矿洞": 1,
            "远古墓穴深处": 2,
            "王的遗迹": 3,
            "诺伊佩拉": 3,
        }
    },
    "雪山": {
        "quad": Quardant.ZUO,
        "fubens": {
            "山脊": 0,
            "雪山丛林": 1,
            "冰心少年": 1,
            "利库天井": 2,
            "白色废墟": 3,
            "布万加的修炼场": 4,
            "斯卡萨之巢": 5,
        }
    },
    "诺斯玛尔": {
        "quad": Quardant.ZUO,
        "fubens": {
            "绿都格罗兹尼": 0,
            "堕落的盗贼": 1,
            "迷乱之村哈穆林": 2,
            "血蝴蝶之舞": 3,
            "疑惑之村": 4,
            "痛苦之村列瑟芬": 5
        }
    },
    "亚诺法森林": {
        "quad": Quardant.ZUO,
        "fubens": {
            "炽晶森林": 0,
            "冰晶森林": 1,
            "水晶矿脉": 2,
            "幽冥监狱": 3,
            "次元空间": 4,
            "遗忘之森": 4,
        }
    },
    "厄运之城": {
        "quad": Quardant.ZUO,
        "fubens": {
            "蘑菇庄园": 0,
            "蚁后的巢穴": 1,
            "腐烂之地": 2,
            "赫顿玛尔旧街区": 3,
            "绝望的棋局": 4,
        }
    }
}

plotMap = {
    # 01-16 艾尔文防线
    "林纳斯的请求": AttacktaskFoo("幽暗密林"),
    "再访林纳斯": MeetNpcFoo("林纳斯"),
    "传说中的白化变异哥布林": AttacktaskFoo("幽暗密林"),
    "毒泉的主人": AttacktaskFoo("猛毒雷鸣废墟"),
    "疯掉的魔法师克拉赫": AttacktaskFoo("冰霜幽暗密林"),
    "备战格拉卡": MeetNpcFoo("林纳斯"),
    "营救赛丽亚": 营救赛丽亚(),
    "通向森林深处的道路": AttacktaskFoo("烈焰格拉卡"),
    "森林的黑暗": AttacktaskFoo("暗黑雷鸣废墟"),
    "大魔法阵是什么": MeetNpcFoo("赛丽亚"),
    "前辈冒险家的建议": MeetNpcFoo("林纳斯"),
    "守护森林的战斗": 守护森林的战斗,
    "转职祝贺": MeetNpcFoo("林纳斯"),
    "赛丽亚的决心": MeetNpcFoo("林纳斯"),
    "朝着新的冒险": MeetNpcFoo("艾尔文南"),
    # 17-30 赫顿玛尔
    "赫顿玛尔的骚乱": MeetNpcFoo("赫顿玛尔2"),
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
    # 30-41 阿尔法营地
    "前往阿法利亚营地": MeetNpcFoo("洛巴赫3"),
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
    "战火虽已平息": MeetNpcFoo("斯卡迪"),
    "邪恶的暗流": MeetNpcFoo("艾丽丝"),
    "被带走的俩人": MeetNpcFoo("帕丽丝"),
    "了解情况": MeetNpcFoo("梅娅女王"),
    "夏普伦长老的要求": MeetNpcFoo("王宫外"),
    "神秘的暗精灵": AttacktaskFoo("暴君的祭坛"),
    "寻找真正的祭坛": AttacktaskFoo("暴君的祭坛"),
    "充满黄金的地方": AttacktaskFoo("黄金矿洞"),
    "维迪尔的要求": AttacktaskFoo("黄金矿洞"),
    "黄金矿洞内部": AttacktaskFoo("黄金矿洞"),
    "跟随米内特": AttacktaskFoo("远古墓穴深处"),
    "远古的诅咒之地": AttacktaskFoo("远古墓穴深处"),
    "沉睡的恶魔": AttacktaskFoo("远古墓穴深处"),
    "暗精灵警备队员": AttacktaskFoo("远古墓穴深处"),
    "目击者之语": MeetNpcFoo("米内特"),
    "询问夏普伦": MeetNpcFoo("夏普伦"),
    "求药": MeetNpcFoo("米内特2"),
    "贝尔玛尔的炼金术师": MeetNpcFoo("诺顿"),
    "诺顿的手艺": MeetNpcFoo("诺顿"),
    "远古王国的遗迹": AttacktaskFoo("王的遗迹"),
    "帕丽丝呢": AttacktaskFoo("王的遗迹"),
    "抵达诺伊佩拉": AttacktaskFoo("诺伊佩拉"),
    "诺伊佩拉的人们": AttacktaskFoo("诺伊佩拉"),
    "悲剧的罪魁祸首": AttacktaskFoo("诺伊佩拉"),
    "返回暗黑城": MeetNpcFoo("米内特3"),
    "向长老汇报": MeetNpcFoo("夏普伦"),
    "梅娅女王的感谢": MeetNpcFoo("王宫外"),
    "获救的俩人": MeetNpcFoo("斯卡迪"),
    "两国和解": MeetNpcFoo("斯卡迪"),
    "歌兰蒂斯的召唤": MeetNpcFoo("敏泰"),
    # 41-46 艾尔文防线-雪山
    "住在雪山的班图族": MeetNpcFoo("巴尔雷娜"),
    "班图女人——巴尔雷娜": AttacktaskFoo("山脊"),
    "勇士的证明": AttacktaskFoo("山脊"),
    "敏泰的哥哥——拉比纳": AttacktaskFoo("山脊"),
    "雪山隐藏的秘密": 雪山隐藏的秘密(),
    "班图族的立场": MeetNpcFoo("歌兰蒂斯·格拉西亚"),
    "冰冷的预言": MeetNpcFoo("艾丽丝"),
    "可疑的委托": MeetNpcFoo("博肯"),
    "从容的班图人": MeetNpcFoo("雷诺"),
    "雷诺的请求": AttacktaskFoo("雪山丛林"),
    "林中徘徊的孩子": AttacktaskFoo("雪山丛林"),
    "冰心少年": AttacktaskFoo("冰心少年"),
    "项链完成": MeetNpcFoo("巴尔雷娜"),
    "蛮横的斯卡萨": AttacktaskFoo("利库天井"),
    "突然现身的艾丽丝": AttacktaskFoo("利库天井"),
    "不肯倒下的白色身影": AttacktaskFoo("利库天井"),
    "新的危险": MeetNpcFoo("奥尔卡"),
    "为了见到布万加": AttacktaskFoo("白色废墟"),
    "登上白色废墟": AttacktaskFoo("白色废墟"),
    "试图制造雪崩的雪魈": AttacktaskFoo("白色废墟"),
    "布万加的修炼场": AttacktaskFoo("布万加的修炼场"),
    "莱里特·拉里的挑战": AttacktaskFoo("布万加的修炼场"),
    "去见布万加的最后一关": AttacktaskFoo("布万加的修炼场"),
    "终于见到布万加": AttacktaskFoo("布万加的修炼场"),
    "布万加的决心": MeetNpcFoo("奥尔卡"),
    "班图族站起来了": AttacktaskFoo("斯卡萨之巢"),
    "向公国求助": AttacktaskFoo("斯卡萨之巢"),
    "冰龙斯卡萨": AttacktaskFoo("斯卡萨之巢"),
    "漫长战争的尽头": MeetNpcFoo("奥尔卡"),
    "博肯的问候": MeetNpcFoo("博肯"),
    # 46-49 赫顿玛尔-后街
    "重逢与新的相遇": MeetNpcFoo("阿甘左"),
    "天界使者": MeetNpcFoo("马琳·基希卡"),
    "前往诺斯玛尔": MeetNpcFoo("后街2"),
    "绿都格罗兹尼": AttacktaskFoo("绿都格罗兹尼"),
    "警惕的超能者们": AttacktaskFoo("绿都格罗兹尼"),
    "麦瑟·莫纳亨": AttacktaskFoo("绿都格罗兹尼"),
    "警惕的麦瑟": AttacktaskFoo("绿都格罗兹尼"),
    "盗贼群": AttacktaskFoo("堕落的盗贼"),
    "变成怪物的存在": AttacktaskFoo("堕落的盗贼"),
    "寻找头领": AttacktaskFoo("堕落的盗贼"),
    "疯狂盗贼的大恶棍": AttacktaskFoo("堕落的盗贼"),
    "前往哈穆林": AttacktaskFoo("迷乱之村哈穆林"),
    "发现幸存者": AttacktaskFoo("迷乱之村哈穆林"),
    "帮助诺诺拉逃脱": AttacktaskFoo("迷乱之村哈穆林"),
    "迷惑人心的歌声": AttacktaskFoo("迷乱之村哈穆林"),
    "传染病治疗剂": MeetNpcFoo("诺顿"),
    "惊讶的诺顿": MeetNpcFoo("诺顿"),
    "把治疗剂交给诺诺拉": AttacktaskFoo("绿都格罗兹尼"),
    "另一个变异生物": AttacktaskFoo("血蝴蝶之舞"),
    "寻找幸存者": AttacktaskFoo("血蝴蝶之舞"),
    "再遇暴戾搜捕团": AttacktaskFoo("血蝴蝶之舞"),
    "蝴蝶怪": AttacktaskFoo("血蝴蝶之舞"),
    "使徒与暴戾搜捕团": AttacktaskFoo("疑惑之村"),
    "探索古怪的村落": AttacktaskFoo("疑惑之村"),
    "试图献祭的人": AttacktaskFoo("疑惑之村"),
    "痛苦之村列瑟芬": AttacktaskFoo("痛苦之村列瑟芬"),
    "面对使徒狄瑞吉": AttacktaskFoo("痛苦之村列瑟芬"),
    "依然存在的不祥之感": AttacktaskFoo("痛苦之村列瑟芬"),
    # 50-61 镜像
    "回归阿拉德": MeetNpcFoo("麦瑟·莫纳亨"),
    "黑色噩梦笼罩下的阿拉德": MeetNpcFoo("麦瑟·莫纳亨"),
    "为了阻止次元": MeetNpcFoo("阿甘左2"),
    "前往银色村庄": MeetNpcFoo("青之守护者塔娜"),
    "精灵生活的森林": AttacktaskFoo("炽晶森林"),
    # "营救赛丽亚": AttacktaskFoo("炽晶森林"),
    "火焰公主婕拉": AttacktaskFoo("炽晶森林"),
    "向塔娜说明": MeetNpcFoo("青之守护者塔娜"),
    "从森林吹来的寒风": AttacktaskFoo("冰晶森林"),
    "搜索冰晶森林": AttacktaskFoo("冰晶森林"),
    "冰雪精灵王杰鲁斯": AttacktaskFoo("冰晶森林"),
    "前往水晶矿脉": AttacktaskFoo("水晶矿脉"),
    "精灵王子": AttacktaskFoo("水晶矿脉"),
    "黑暗之王": AttacktaskFoo("水晶矿脉"),
    "塔娜": MeetNpcFoo("青之守护者塔娜"),
    "前往幽冥监狱": AttacktaskFoo("幽冥监狱"),
    "怨气冲天的监狱": AttacktaskFoo("幽冥监狱"),
    "邪念魔石萨姆": AttacktaskFoo("幽冥监狱"),
    "在生死线挣扎的普莱斯": MeetNpcFoo("青之守护者塔娜"),
    "为了救活普莱斯": AttacktaskFoo("水晶矿脉"),
    "伟大的意志": AttacktaskFoo("次元空间"),
    "雅妮丝的建议": MeetNpcFoo("青之守护者塔娜"),
    "毁灭纪碎片": AttacktaskFoo("遗忘之森"),
    "拜访摩根": MeetNpcFoo("炼金术师摩根"),
    "前往赫顿玛尔废墟": MeetNpcFoo("帕丽丝2"),

    "被毁灭纪摧毁的地方": AttacktaskFoo("蘑菇庄园"),
    "收集蜂蜜": AttacktaskFoo("蘑菇庄园"),
    "操纵蘑菇的蚂蚁": AttacktaskFoo("蚁后的巢穴"),
    "破坏蚁穴": AttacktaskFoo("蚁后的巢穴"),
    "堕落蚁后梅莲娜": AttacktaskFoo("蚁后的巢穴"),
    "前往腐烂之地": AttacktaskFoo("腐烂之地"),
    "阿尔伯特的请求": AttacktaskFoo("腐烂之地"),
    "收集蝎毒": AttacktaskFoo("腐烂之地"),
    "污染土壤的黑暗巨蝎": AttacktaskFoo("腐烂之地"),
    "鲁埃尔的好意": AttacktaskFoo("赫顿玛尔旧街区"),
    "与鲁埃尔的较量": AttacktaskFoo("赫顿玛尔旧街区"),
    # "寻找幸存者": AttacktaskFoo("赫顿玛尔旧街区"),
    "变异的幸存者": MeetNpcFoo("阿尔伯特·伯恩斯坦"),
    "愤怒的帕丽丝": AttacktaskFoo("赫顿玛尔旧街区"),
    "被绑架的居民": MeetNpcFoo("阿尔伯特·伯恩斯坦"),
    # "被绑架的居民": AttacktaskFoo("赫顿玛尔旧街区深处"),
    "调查绝望的棋局": AttacktaskFoo("绝望的棋局"),
    "跳舞的人偶": AttacktaskFoo("绝望的棋局"),
    "棋局的秘密": AttacktaskFoo("绝望的棋局"),
    # "棋局的秘密": MeetNpcFoo("帕丽丝2"),
    "麦瑟的召唤": AttacktaskFoo("绝望的棋局"),
    "下一个目的地": MeetNpcFoo("赛丽亚"),
    "准备离开": MeetNpcFoo("帕丽丝2"),

    "另一个次元的天帷巨兽": MeetNpcFoo("奥菲利亚·贝伊兰斯"),
    "教主奥菲利亚": MeetNpcFoo("伊沙杜拉"),
    "伊沙杜拉的请求": AttacktaskFoo("鲨鱼栖息地"),
    "海洋的追随者": AttacktaskFoo("鲨鱼栖息地"),
    "消灭食人鲨": AttacktaskFoo("鲨鱼栖息地"),
    "来到天帷巨兽的人们": MeetNpcFoo("奥菲利亚·贝伊兰斯"),
    "剑魂们找来的理由": MeetNpcFoo("巨剑阿甘左"),
    "寻找人鱼之王": AttacktaskFoo("人鱼的国度"),
    "见到人鱼之王": AttacktaskFoo("人鱼的国度"),
    "向伊莎杜拉转达": MeetNpcFoo("伊沙杜拉"),
    "捣乱的鸭嘴海盗团": AttacktaskFoo("人鱼的国度"),
    "人鱼之王图雷": AttacktaskFoo("人鱼的国度"),
    "人鱼之王留下的话": MeetNpcFoo("奥菲利亚·贝伊兰斯"),
    "GBL教的秘密": MeetNpcFoo("巨剑阿甘左"),
    # "GBL教的秘密": AttacktaskFoo("GBL女神殿"),
    "GBL女神殿的怪人": AttacktaskFoo("GBL女神殿"),
    "GBL女神殿的秘密": AttacktaskFoo("GBL女神殿"),
    "会合": AttacktaskFoo("GBL女神殿"),
    "崩溃的罗特斯封印": AttacktaskFoo("树精繁殖地"),
    "阿甘左的问题": AttacktaskFoo("树精繁殖地"),
    "手持火焰的树精": AttacktaskFoo("树精繁殖地"),
    "罗特斯的信徒": AttacktaskFoo("树精繁殖地"),
    # "罗特斯所在之地": AttacktaskFoo("树精繁殖地"),
    "询问奥菲利亚": MeetNpcFoo("奥菲利亚·贝伊兰斯"),
    "碍事的信徒": AttacktaskFoo("罗特斯的宫殿"),
    "不安的雷尼": AttacktaskFoo("罗特斯的宫殿"),
    "面对罗特斯": MeetNpcFoo("巨剑阿甘左"),
    "再遇长脚罗特斯": AttacktaskFoo("罗特斯的宫殿"),
    "返回赫顿玛尔": MeetNpcFoo("麦瑟·莫纳亨"),
    # 63-74 天界
    "洛巴赫的委托": MeetNpcFoo("斯卡迪女王"),
    "前往天界": MeetNpcFoo("巴恩·巴休特"),
    "邪龙之角": MeetNpcFoo("梅娅女王"),
    "准备就绪": MeetNpcFoo("马琳·基希卡"),
    "终于开启的天界之门": MeetNpcFoo("马琳·基希卡"),
    "天界的守备队长": MeetNpcFoo("泽丁·施奈德"),
    "侦查根特外围": AttacktaskFoo("根特外围"),
    "冒险家被抓": AttacktaskFoo("根特外围"),
    "阻止纵火兵": AttacktaskFoo("根特外围"),
    "根特的守护神": MeetNpcFoo("梅尔文·里克特"),
    # "根特的守护神": MeetNpcFoo("泽丁·施奈德"),
    # "根特的守护神": AttacktaskFoo("根特东门"),
    "救出我军": AttacktaskFoo("根特东门"),
    "疾风之苏雷德": AttacktaskFoo("根特东门"),
    "夺取弹药": AttacktaskFoo("根特南门"),
    "奇怪的兵器": MeetNpcFoo("梅尔文·里克特"),
    # "奇怪的兵器": MeetNpcFoo("泽丁·施奈德"),
    # "奇怪的兵器": AttacktaskFoo("根特南门"),
    "机动兵器 GT-9600": AttacktaskFoo("根特南门"),
    "持续的战争": MeetNpcFoo("泽丁·施奈德"),
    "遗失的AT5T 步行者": AttacktaskFoo("根特北门"),
    "回收AT5T 步行者": AttacktaskFoo("根特北门"),
    "拥有机械臂的男人": AttacktaskFoo("根特北门"),
    "天界的摄政王": MeetNpcFoo("纳维罗·尤尔根"),
    "让人惊叹不已的料理": MeetNpcFoo("马琳·基希卡"),
    # "让人惊叹不已的料理": MeetNpcFoo("巴恩·巴休特"),
    # "让人惊叹不已的料理": MeetNpcFoo("泽丁·施奈德"),
    "卡勒特突袭": AttacktaskFoo("根特北门"),
    "遇见革命军": AttacktaskFoo("峡谷深处"),
    "向泽丁报告": MeetNpcFoo("泽丁·施奈德"),
    "躲在峡谷的敌人": AttacktaskFoo("根特防御战"),
    "突破包围": AttacktaskFoo("根特防御战"),
    "夜战司令官巴比伦": AttacktaskFoo("根特防御战"),
    "侦查敌军营地": AttacktaskFoo("夜间袭击战"),
    "午夜行动": MeetNpcFoo("沙影贝利特"),
    # "午夜行动": MeetNpcFoo("夜间袭击战"),
    "银勺团杂技团": MeetNpcFoo("泽丁·施奈德"),
    "打败小丑人": AttacktaskFoo("夜间袭击战"),
    "击退杂技团": AttacktaskFoo("夜间袭击战"),
    "探索补给基地": AttacktaskFoo("补给线阻断战"),
    "保证粮食供应": AttacktaskFoo("补给线阻断战"),
    "奇特的生物": AttacktaskFoo("补给线阻断战"),
    "怪物实验体": MeetNpcFoo("梅尔文·里克特"),
    # "怪物实验体": AttacktaskFoo("补给线阻断战"),
    "终极实验体": AttacktaskFoo("补给线阻断战"),
    "准备总攻": AttacktaskFoo("追击歼灭战"),
    "集结特种部队": AttacktaskFoo("追击歼灭战"),
    "无名女士": AttacktaskFoo("追击歼灭战"),
    "终极作战": AttacktaskFoo("追击歼灭战"),
    "大决战": AttacktaskFoo("追击歼灭战"),
    "马琳的问候": MeetNpcFoo("马琳·基希卡"),

    "悬空的海港": MeetNpcFoo("贝伦·博内哥特"),
    "免费搭乘海上列车": AttacktaskFoo("列车上的海贼"),
    "可疑的美人鱼空空伊": AttacktaskFoo("列车上的海贼"),
    "海盗船长": AttacktaskFoo("列车上的海贼"),
    "逃跑的黑鳞莫贝尼": AttacktaskFoo("列车上的海贼"),
    "前往船长所在之处": AttacktaskFoo("夺回西部线"),
    "小美人鱼": AttacktaskFoo("夺回西部线"),
    "破坏武器": AttacktaskFoo("夺回西部线"),
    "夺回海上列车": AttacktaskFoo("夺回西部线"),
    "小灯笼的礼物": MeetNpcFoo("小灯笼"),
    "挡路的列车": AttacktaskFoo("幽灵列车"),
    "雾都赫伊斯": AttacktaskFoo("雾都赫伊斯"),
    "敌人袭来": AttacktaskFoo("雾都赫伊斯"),
    "狙击手": AttacktaskFoo("雾都赫伊斯"),
    "不幸之门": AttacktaskFoo("雾都赫伊斯"),
    "叛徒 - 兜风皮埃尔": AttacktaskFoo("雾都赫伊斯"),
    "捉住范·弗拉丁": AttacktaskFoo("雾都赫伊斯"),
    "阿登高地": AttacktaskFoo("阿登高地"),
    "贝利特参战": AttacktaskFoo("阿登高地"),
    "双枪哈斯": AttacktaskFoo("阿登高地"),
    "终结的传说": AttacktaskFoo("阿登高地"),
    "卡勒特的改造士兵": AttacktaskFoo("阿登高地"),
    "夕日之眼 - 安祖·赛弗": AttacktaskFoo("阿登高地"),
    "紧急会议": AttacktaskFoo("无法地带营地"),
    "前往卡勒特指挥部": AttacktaskFoo("卡勒特指挥部"),
    "拯救皇女陛下": AttacktaskFoo("卡勒特指挥部"),
    "保护皇女": AttacktaskFoo("卡勒特指挥部"),
    "战争结束": AttacktaskFoo("卡勒特指挥部"),
    "皇女的问候": AttacktaskFoo("皇女艾丽婕"),
    "吉赛尔的行踪": MeetNpcFoo("梅尔文·里克特"),
    # 75-80 时空之门
    "斯卡迪女王2": MeetNpcFoo("斯卡迪女王"),
    "天界的冒险故事": MeetNpcFoo("巨剑阿甘左"),
    "前往素喃": MeetNpcFoo("卡坤   需要材料钢铁片*50  黑曜石*30"),
    # "前往素喃": MeetNpcFoo("外交使节 诺羽"),
    "真正的冒险": MeetNpcFoo("剑圣 西岚"),
    "把酒言欢": MeetNpcFoo("外交使节 诺羽"),
    "徒弟的担忧": MeetNpcFoo("剑圣 西岚"),
    "西岚的秘密": MeetNpcFoo("剑圣 西岚"),
    "时空转移之力": MeetNpcFoo("剑圣 西岚   无色小*500"),
    "开启时空之门": AttacktaskFoo("时空之门"),
    "向混乱的时空进发": AttacktaskFoo("精灵之森"),
    "调查精灵之森": AttacktaskFoo("精灵之森"),
    "精灵少女 (1 / 2)": MeetNpcFoo("剑圣 西岚"),
    "精灵少女 (2 / 2)": AttacktaskFoo("精灵之森"),
    "发狂的乌塔拉": AttacktaskFoo("西部森林"),
    "那个人的踪迹": AttacktaskFoo("格兰之火"),
    "精灵结义": AttacktaskFoo("格兰之火"),
    "美女与野兽": MeetNpcFoo("剑圣 西岚"),
    "寻找那个人的踪迹": AttacktaskFoo("瘟疫之源"),
    "治疗瘟疫的解药": MeetNpcFoo("诺顿"),
    "民兵队长贺加斯": AttacktaskFoo("瘟疫之源"),
    "回到更早之前": AttacktaskFoo("瘟疫之源"),
    "迷雾缭绕": AttacktaskFoo("瘟疫之源"),
    "衣服碎片": MeetNpcFoo("杂货店的卡妮娜"),
    # "衣服碎片": MeetNpcFoo("剑圣 西岚"),
    "昔日的天界": AttacktaskFoo("无法地带"),
    "昔日的无法地带": AttacktaskFoo("卡勒特之初"),
    "年轻时的吉赛尔": AttacktaskFoo("无法地带"),
    # "年轻时的吉赛尔": AttacktaskFoo("卡勒特之初"),
    # "年轻时的吉赛尔": AttacktaskFoo("无法地带"),
    "新的线索": MeetNpcFoo("剑圣 西岚"),
    "年轻时的贝利特": AttacktaskFoo("卡勒特之初"),
    "偷听": AttacktaskFoo("无法地带"),
    "超级别的魔法师": MeetNpcFoo("莎兰"),
    # "超级别的魔法师": MeetNpcFoo("吟游诗人艾丽丝"),
    # "超级别的魔法师": MeetNpcFoo("剑圣 西岚"),
    "前往绝密区域": AttacktaskFoo("绝密区域"),
    "破坏实验装置": AttacktaskFoo("绝密区域"),
    "转移试验": AttacktaskFoo("绝密区域"),
    "竟然是巴恩": AttacktaskFoo("绝密区域"),
    "绝密区域的悲剧": AttacktaskFoo("绝密区域"),
    "前往现在的绝密区域": AttacktaskFoo("比尔马克帝国试验场"),
    "比尔马克帝国试验场": AttacktaskFoo("比尔马克帝国试验场"),
    "前往林纳斯处": MeetNpcFoo("铁匠林纳斯"),
    "与托比再会": AttacktaskFoo("幽暗密林"),
    "可疑的男子": AttacktaskFoo("比尔马克帝国试验场"),
    "禁区": AttacktaskFoo("比尔马克帝国试验场"),
    "比尔马克帝国试验场的警卫员": AttacktaskFoo("比尔马克帝国试验场"),
    "昔日的悲鸣洞穴": AttacktaskFoo("昔日悲鸣"),
    "神秘的魔法师": AttacktaskFoo("昔日悲鸣"),
    "老朋友相见": AttacktaskFoo("昔日悲鸣"),
    "一无所获": MeetNpcFoo("剑圣 西岚"),
    "前往悲鸣洞穴深处": AttacktaskFoo("昔日悲鸣"),
    "紫雾团首领凯恩": AttacktaskFoo("昔日悲鸣"),
    "发丝的魔力": MeetNpcFoo("吟游诗人艾丽丝"),
    "一点都不简单": MeetNpcFoo("剑圣 西岚"),
    "调查巴卡尔之城": AttacktaskFoo("凛冬"),
    "为了寻找线索": AttacktaskFoo("凛冬"),
    "主人": AttacktaskFoo('凛冬'),
    "穿越时空的证明": AttacktaskFoo("凛冬"),
    "巴卡尔的好奇心": AttacktaskFoo("凛冬"),
    "身份暴露": MeetNpcFoo("剑圣 西岚"),
    # "身份暴露": MeetNpcFoo("吟游诗人艾丽丝"),
    "竟然是她": MeetNpcFoo("剑圣 西岚"),
    "残酷的真相": MeetNpcFoo("布告栏"),
    "寻找艾丽丝": MeetNpcFoo("魔法师公会"),
    "艾丽丝躲藏的地方": MeetNpcFoo("剑圣 西岚"),
    "艾丽丝之谜": AttacktaskFoo("谜之觉悟"),
    "艾丽丝的觉悟 (1 / 3)": AttacktaskFoo("谜之觉悟"),
    "艾丽丝的觉悟 (2 / 3)": MeetNpcFoo("魔法师公会"),
    "艾丽丝的觉悟 (3 / 3)": AttacktaskFoo("艾丽丝的觉悟"),
    "以后的事": MeetNpcFoo("艾丽丝"),
    # 81-83 能源中心
    "艾丽丝的挽留": MeetNpcFoo("艾丽丝"),
    "再次前往天界": MeetNpcFoo("马琳·基希卡"),
    "前往斯曼工业基地": MeetNpcFoo("梅尔文·里克特"),
    # "前往斯曼工业基地": MeetNpcFoo("米娅"),
    "斯曼工业基地的人们": MeetNpcFoo("中将尼贝尔"),
    # "斯曼工业基地的人们": MeetNpcFoo("佩拉·维恩"),
    "克雷发电站": AttacktaskFoo("克雷发电站"),
    "克雷发电站的敌人们": AttacktaskFoo("克雷发电站"),
    "蓄电池的原材料": AttacktaskFoo("克雷发电站"),
    "危险的研究": MeetNpcFoo("马蒂亚斯"),
    # "危险的研究": MeetNpcFoo("提交材料各色小晶快*200 + 马蒂亚斯对话"),
    "废旧电池": MeetNpcFoo("佩拉·维恩"),
    "菲茨的心腹": AttacktaskFoo("克雷发电站"),
    "破坏一号发电机": AttacktaskFoo("克雷发电站"),
    "下一个发电站": AttacktaskFoo("普鲁兹发电站"),
    "神秘的魔刹石": MeetNpcFoo("米亚·里克特     需要点击远程通话"),
    "收集魔刹石": AttacktaskFoo("普鲁兹发电站"),
    "转交魔法石": MeetNpcFoo("贝伦·博内哥特"),
    # "转交魔法石": MeetNpcFoo("中将尼贝尔"),
    "寻找掉队的队员": AttacktaskFoo("普鲁兹发电站"),
    "阻止能量传导": AttacktaskFoo("普鲁兹发电站"),
    "关闭起重装置": AttacktaskFoo("普鲁兹发电站"),
    "熔弹萨缪尔": AttacktaskFoo("普鲁兹发电站"),
    "皇女的联系": MeetNpcFoo("米亚·里克特     需要点击远程通话"),
    "来自魔界的通信": MeetNpcFoo("米亚·里克特"),
    "接下来的作战计划": MeetNpcFoo("中将尼贝尔"),
    "失踪的技术者们": AttacktaskFoo("特伦斯发电站"),
    "技术者的目的": AttacktaskFoo("特伦斯发电站"),
    "终止特伦斯发电站的运行": AttacktaskFoo("特伦斯发电站"),
    "变形的电": AttacktaskFoo("特伦斯发电站"),
    "闪电之帕特里斯": MeetNpcFoo("中将尼贝尔"),
    # "闪电之帕特里斯": AttacktaskFoo("特伦斯发电站"),
    "最后的发电站": AttacktaskFoo("格兰迪发电站"),
    "强大能量阻碍": MeetNpcFoo("佩拉·维恩"),
    "重要的任务": AttacktaskFoo("格兰迪发电站"),
    "巨人波图拉": AttacktaskFoo("格兰迪发电站"),
    "开路": AttacktaskFoo("格兰迪发电站"),
    "虚空之弗曼": AttacktaskFoo("格兰迪发电站"),
    "秘密工作": MeetNpcFoo("佩拉·维恩"),
    "能量阻断室": AttacktaskFoo("能量阻断室"),
    "七神之鞘翅的自尊心": MeetNpcFoo("佩拉·维恩"),
    # 安图恩84-85
    "逃亡的安徒恩": MeetNpcFoo("奈恩·希格"),
    "苍穹贵族号上的军人们": MeetNpcFoo("乌恩·莱奥尼尔"),
    "黑色迷雾": AttacktaskFoo("黑雾之谜"),
    "驱散黑色迷雾": AttacktaskFoo("黑雾之谜"),
    "关节破坏": AttacktaskFoo("破坏关节"),
    "突袭": AttacktaskFoo("舰炮防御站"),
    "劝诱": AttacktaskFoo("意志之路"),
    "为了天界的和平": AttacktaskFoo("擎天之柱上部"),
    "艰难的攻坚战": AttacktaskFoo("艰难的攻坚战"),
    "第七使徒安徒恩": AttacktaskFoo("黑色火山内部"),
    "破坏心脏": AttacktaskFoo("安徒恩的心脏"),
    "胜利之后": AttacktaskFoo("鹰眼杰克特"),
    # 85-86 寂静城
    "为了前往寂静城": MeetNpcFoo("皇女艾丽婕"),
    # "为了前往寂静城": MeetNpcFoo("纳维罗·尤尔根"),
    "抵达克洛诺斯岛的联合调查团": MeetNpcFoo("伊莎贝拉公主"),
    "奇怪的机器": AttacktaskFoo("倒悬的瞭望台"),
    "来自魔界的狐狸": MeetNpcFoo("猎手伯恩"),
    "来到克洛诺斯岛的冒险家联盟": AttacktaskFoo("倒悬的瞭望台"),
    "关于使徒卢克": AttacktaskFoo("倒悬的瞭望台"),
    "淘气的贝奇": AttacktaskFoo("倒悬的瞭望台"),
    "光学研究所": AttacktaskFoo("卢克的聚光镜"),
    "抵达克洛诺斯岛的暴戾搜捕团": MeetNpcFoo("艾泽拉·洛伊"),
    "调查卢克的聚光镜": AttacktaskFoo("卢克的聚光镜"),
    "卢克的聚光镜的妨碍物": AttacktaskFoo("卢克的聚光镜"),
    "收集光的人": AttacktaskFoo("卢克的聚光镜"),
    "奇怪的聚光镜": MeetNpcFoo("梅丽·法伊奥妮尔"),
    "罗伊引起的骚乱": MeetNpcFoo("移动到指定区域"),
    "钢铁之臂": AttacktaskFoo("钢铁之臂"),
    "城的防御系统": AttacktaskFoo("钢铁之臂"),
    "破坏控制系统": AttacktaskFoo("钢铁之臂"),
    "全金属机甲门卫": AttacktaskFoo("钢铁之臂"),
    "钢铁意志 - 耐梅盖特的恐怖": MeetNpcFoo("纳维罗·尤尔根"),
    "能源熔炉": AttacktaskFoo('能源熔炉'),
    # "能源熔炉": MeetNpcFoo('梅丽·法伊奥妮尔'),
    "寻找弱点": AttacktaskFoo("能源熔炉"),
    # "寻找弱点": MeetNpcFoo("梅丽·法伊奥妮尔"),
    "钢铁意志 - 耐梅盖特的结构": AttacktaskFoo("能源熔炉"),
    "破坏钢铁意志": AttacktaskFoo("能源熔炉"),
    "充满光的地方": AttacktaskFoo("光之舞会"),
    "被雾气笼罩的克洛诺斯岛": MeetNpcFoo("移动到联合调查团临时营地"),
    "光之舞会的主人": AttacktaskFoo("光之舞会"),
    "黄金小丑的助手": AttacktaskFoo("光之舞会"),
    "输送光之力量的人": AttacktaskFoo("光之舞会"),
    "坍塌的光之舞会": AttacktaskFoo("光之舞会"),
    "矛盾": MeetNpcFoo("艾泽拉·洛伊"),
    "暴戾搜捕团的劝说": MeetNpcFoo("纳维罗·尤尔根"),
    "联合调查团的劝说": MeetNpcFoo("达娜·多纳特"),
    "冒险家联盟的劝说和选择": MeetNpcFoo("达娜·多纳特"),
    "加入联合调查团": MeetNpcFoo("伊莎贝拉公主"),
    "动摇城池的震动": AttacktaskFoo("王的书库"),
    "通向巨人的路": AttacktaskFoo("王的书库"),
    "调查机器人": AttacktaskFoo("王的书库"),
    "卢克的数据": AttacktaskFoo("王的书库"),
    # "卢克的数据": MeetNpcFoo("梅丽·法伊奥妮尔"),
    "库尔图洛·玛努斯": AttacktaskFoo("王的书库"),
    "消灭巨人的报告": MeetNpcFoo("梅丽·法伊奥妮尔"),
    "使徒卢克的威胁还在继续": MeetNpcFoo("猎手伯恩"),
    # 卢克的实验室86-90
    "黑暗中的使徒卢克": MeetNpcFoo("伊莎贝拉公主"),
    "城内深处": AttacktaskFoo("传说之城秘密区域"),
    "调查工厂": AttacktaskFoo("诞生之圣所"),
    "湮灭之圣所": AttacktaskFoo("湮灭之圣所"),
    "去往下个区域的路": AttacktaskFoo("湮灭之圣所"),
    "突如其来的内讧": AttacktaskFoo("蔓延之圣所"),
    "扩散到工厂内部": AttacktaskFoo("蔓延之圣所"),
    "远处的声音": AttacktaskFoo("蔓延之圣所"),
    "试图阻止卢克的人": AttacktaskFoo("诞生之圣所"),
    "赫尔德的故事": AttacktaskFoo("诞生之圣所"),
    "继续前行": MeetNpcFoo("纳维罗·尤尔根"),
    "艾泽拉的警戒": MeetNpcFoo("伊莎贝拉公主"),
    "准备": AttacktaskFoo("湮灭之圣所"),
    "被遗弃的贝奇": AttacktaskFoo("湮灭之圣所"),
    # 87-95 地轨中心
    "终于抵达魔界": MeetNpcFoo("伊莎贝拉公主"),
    "杂乱的开始": AttacktaskFoo("时间广场"),
    "小魔女斯库尔蒂": AttacktaskFoo("时间广场"),
    "另一个魔女": MeetNpcFoo("伊莎贝拉公主"),
    "善良的魔女贝拉迪尔": AttacktaskFoo("时间广场"),
    "狐狸玛尔切拉": AttacktaskFoo("兽人峡谷"),
    "贝拉迪尔的感谢": AttacktaskFoo("时间广场"),
    "依然警戒": MeetNpcFoo("达娜·多纳特"),
    "不安的艾泽拉": MeetNpcFoo("伊莎贝拉公主"),
    "发现泰拉石": AttacktaskFoo("时间广场"),
    "为了避开帝国的耳目": AttacktaskFoo("时间广场"),
    "将泰拉石送往帝国": MeetNpcFoo("达娜·多纳特"),
    "被掠走的帝国军": AttacktaskFoo("时间广场"),
    "报恩的狐狸": AttacktaskFoo("兽人峡谷"),
    "姐妹的秘密": AttacktaskFoo("兽人峡谷"),
    "兽人们的叛变": AttacktaskFoo("兽人峡谷"),
    "永不熄灭的火": AttacktaskFoo("兽人峡谷"),
    "疯狂的诺尔妮和格拉古尔的疯狂": AttacktaskFoo("时间广场"),
    "燃烧的兽人峡谷": AttacktaskFoo("兽人峡谷"),
    "使诺尔妮恢复镇定的方法": AttacktaskFoo("兽人峡谷"),
    "解救诺尔妮": AttacktaskFoo("兽人峡谷"),
    "请求帮助": MeetNpcFoo("艾泽拉·洛伊"),
    "分秒必争": AttacktaskFoo("兽人峡谷"),
    "格拉古尔和诺尔妮": AttacktaskFoo("兽人峡谷"),
    "离别时刻": MeetNpcFoo("艾泽拉·洛伊"),
    # "离别时刻": AttacktaskFoo("时间广场"),
    "充满嘶喊的地方": AttacktaskFoo("恐怖的栖息地"),
    "解救少女": AttacktaskFoo("恐怖的栖息地"),
    "魔界少女比比": AttacktaskFoo("恐怖的栖息地"),
    "传说中的人物": MeetNpcFoo("魔界营地-移动到指定地址触发"),
    "公主登场": AttacktaskFoo("恐怖的栖息地"),
    "伯爵的要求": AttacktaskFoo("恐怖的栖息地"),
    "伊莎贝拉公主的故事": AttacktaskFoo("恐怖的栖息地"),
    "管家亚佐夫和迷之女人": AttacktaskFoo("恐怖的栖息地"),
    "吸血鬼": MeetNpcFoo("伊莎贝拉公主"),
    "比比的不安": MeetNpcFoo("祈求者比比"),
    "比比的决心": AttacktaskFoo("恐怖的栖息地"),
    "记忆中的蕾娅姐姐": AttacktaskFoo("恐怖的栖息地"),
    "令人意外的访客": MeetNpcFoo("艾泽拉·洛伊"),
    "追来的男子": AttacktaskFoo("恐怖的栖息地"),
    "前往疾风地带": AttacktaskFoo("疾风地带"),
    "寻找出路": AttacktaskFoo("疾风地带"),
    "生活在疾风地带的怪物们": AttacktaskFoo("疾风地带"),
    "追击的巴古尔": AttacktaskFoo("疾风地带"),
    "服从魔法": AttacktaskFoo("疾风地带"),
    "魔力不足": AttacktaskFoo("疾风地带"),
    "可靠的同伴": AttacktaskFoo("疾风地带"),
    "抢夺巴古尔的控制权": AttacktaskFoo("疾风地带"),
    "救世主": MeetNpcFoo("移动到魔界营地触发"),
    "可疑的少女": AttacktaskFoo("疾风地带"),
    "穿过疾风地带": AttacktaskFoo("疾风地带"),
    "魔界的森林": AttacktaskFoo("中央公园森林"),
    "痕迹": AttacktaskFoo("中央公园森林"),
    "来自某人的监视": AttacktaskFoo("中央公园森林"),
    "被施了魔法的森林": AttacktaskFoo("中央公园森林"),
    "红色魔女": AttacktaskFoo("红色魔女之森"),
    "森林迷宫": AttacktaskFoo("红色魔女之森"),
    "格来德·艾科斯的再次挑战": AttacktaskFoo("红色魔女之森"),
    "视死如归的格来德·艾科斯": AttacktaskFoo("红色魔女之森"),
    "追踪阿斯兰": AttacktaskFoo("红色魔女之森"),
    "到达中央公园": MeetNpcFoo("尼巫"),
    "相遇": AttacktaskFoo("红色魔女之森"),
    "召唤师凯蒂": MeetNpcFoo("凯蒂"),
    "凯蒂的故事": MeetNpcFoo("凯蒂"),
    "森林里的光": AttacktaskFoo("红色魔女之森"),
    "再次回到寂静城": MeetNpcFoo("凯蒂"),
    "怀着希望前往克洛诺斯岛": MeetNpcFoo("猎手伯恩"),
    "尽快找到卢克": AttacktaskFoo("蔓延之圣所"),
    "援军参战": MeetNpcFoo("伊莎贝拉公主"),
    "光明之祭坛": AttacktaskFoo("光明之祭坛"),
    "黑暗之祭坛": AttacktaskFoo("黑暗之祭坛"),
    "前往卢克的实验室": AttacktaskFoo("机械王座"),
    "使徒卢克": AttacktaskFoo("机械王座"),
    "皇女归来": MeetNpcFoo("伊莎贝拉公主"),
    "尤尔根的豪言壮语": MeetNpcFoo("纳维罗·尤尔根"),
    "艾泽拉的下落": AttacktaskFoo("机械王座"),
    "永别了， 艾泽拉": MeetNpcFoo("学霸罗伊"),
    "分崩离析的人们": MeetNpcFoo("海德·伯恩·克鲁格"),
    "皇女艾丽婕的委托": MeetNpcFoo("皇女艾丽婕"),
    "向凯蒂报告": MeetNpcFoo("凯蒂"),
    "未来之路": AttacktaskFoo("红色魔女之森"),
    "微弱的声音": AttacktaskFoo("中央公园外围森林"),
    "前往中央公园": MeetNpcFoo("凯蒂"),
    "逃走的孩子": MeetNpcFoo("派伊"),
    "派伊的决心": MeetNpcFoo("凯蒂"),
    "前往哈林": AttacktaskFoo("荒芜之地"),
    "逃亡者们": AttacktaskFoo("堕落之森"),
    "黑暗的森林深处": AttacktaskFoo("堕落之森"),
    "哈林的市场": MeetNpcFoo("南瓜球"),
    "猎人们 (1 / 2)": AttacktaskFoo("亡命杀镇"),
    "猎人们 (2 / 2)": AttacktaskFoo("亡命杀镇"),
    "归途": MeetNpcFoo("凯蒂"),
    "奴隶少年": AttacktaskFoo("红色魔女"),
    "重返哈林": AttacktaskFoo("荒芜之地"),
    "黑市": MeetNpcFoo("科布"),
    "黑市的商人": MeetNpcFoo("红鼻子德拉-----需要打开商店购买商品"),
    "调查全蚀市场": AttacktaskFoo("全蚀市场"),
    "拯救奴隶": AttacktaskFoo("全蚀市场"),
    "追上来的商人们": AttacktaskFoo("全蚀市场"),
    "变成怪物的奴隶们": AttacktaskFoo("全蚀市场"),
    "恳求": AttacktaskFoo("全蚀市场"),
    "寻找孩子": AttacktaskFoo("全蚀市场"),
    "愤怒的商人们": AttacktaskFoo("全蚀市场"),
    # "拯救奴隶": AttacktaskFoo("全蚀市场"),
    "寻找科布": AttacktaskFoo("全蚀市场"),
    "狂信徒": AttacktaskFoo("全蚀市场"),
    "狂热者迪欧尔贝": AttacktaskFoo("全蚀市场"),
    "幸存的孩子": AttacktaskFoo("全蚀市场"),
    "前往黑暗都市": AttacktaskFoo("黑暗都市"),
    "黑暗都市": MeetNpcFoo("派伊"),
    "奇怪的女人": AttacktaskFoo(""),
    "赛贝琳的要求": AttacktaskFoo(""),
    "银发少女": AttacktaskFoo(""),
    "陷入危险的黑暗都市": AttacktaskFoo(""),
    "越来越多的牺牲者": AttacktaskFoo(""),
    "不可能的事": AttacktaskFoo(""),
    "寻找蒙德格林": AttacktaskFoo(""),
    "残酷的蒙德格林": AttacktaskFoo(""),
    "灵魂饲养员蒙德格林": AttacktaskFoo(""),
    "火花坠落的地方": AttacktaskFoo(""),
    "妲可儿的提议": AttacktaskFoo(""),
    "不安的氛围": AttacktaskFoo(""),
    "亡命杀镇的魔剑士": AttacktaskFoo(""),
    "奇妙的魔剑士，瑟尔莫": AttacktaskFoo(""),
    "去找妲可儿": AttacktaskFoo(""),
}


def main():
    pass


if __name__ == '__main__':
    main()
