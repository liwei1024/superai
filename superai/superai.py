import pythoncom

import ctypes
import json
import logging
import os
import subprocess
import sys
import threading

import cv2
import names
import win32api
import win32gui

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

logger = logging.getLogger(__name__)

from superai.hanhua import Getyulu
from superai.subnodeapi import subnodeapi
from superai.screenshots import WindowCaptureToMem, WindowCaptureToFile

import random
import time

from superai.vercode import verifyfile

from superai.location import IsinSailiya

from superai.login import GetDaqu, GetMainregionPos, GetRegionPos

from superai.subnodedb import DbStateUpdate, DbStateSelect, IsTodayHavePilao, GetToSelectIdx, UpdateMenState, \
    DbEventAppend, AccountRoles, InitDb, AccountXingyunxingRule, DayCreateJueseNum, CreateJueses, CreateJueseAppend, \
    IsAccoutnZhicai

from superai.pathsetting import GetImgDir, GameFileDir, GetvercodeDir

from superai.accountsetup import IsAccountSetted, PrintSwitchTips, BlockGetSetting, GetAccount, GetRegion, \
    GetSettingAccounts, SetCurrentAccount

from superai.dealequip import DealEquip
from superai.equip import Equips
from superai.plot import TaskCtx, HasPlot, plotMap, OpenSelect, ResetAllChongming
from superai.learnskill import Occupationkills
from superai.common import InitLog, GameWindowToTop, HideConsole, ClientWindowToTop
from superai.astarpath import GetPaths, GetCorrectDoorXY, idxToZuobiao, SafeGetDAndOb, Zuobiao
from superai.astartdemo import idxToXY

from superai.flannfind import SetThreadExit, \
    IsConfirmTop, GetConfirmPos, FlushImg, IsShipinTop, Picture

from superai.vkcode import VK_CODE

from superai.yijianshu import YijianshuInit, PressRight, \
    PressLeft, JiPaoZuo, JiPaoYou, ReleaseAllKey, PressX, PressHouTiao, RanSleep, PressKey, MouseMoveTo, MouseLeftClick, \
    PressUp, PressDown, KongjianSleep, DeleteAll, KeyInputString, MouseMoveToLogin

from superai.gameapi import GameApiInit, FlushPid, \
    HaveMonsters, GetMenXY, GetQuadrant, GetMenChaoxiang, RIGHT, Skills, LEFT, HaveGoods, \
    NearestGood, IsNextDoorOpen, IsCurrentInBossFangjian, GetMenInfo, \
    CanbePickup, WithInManzou, GetFangxiang, ClosestMonsterIsToofar, simpleAttackSkill, IsClosedTo, \
    NearestBuf, HaveBuffs, CanbeGetBuff, SpecifyMonsterIsToofar, IsManInMap, IsManInChengzhen, QuardantMap, IsManJipao, \
    NearestMonsterWrap, IsWindowTop, IsEscTop, IsFuBenPass, IsJiZhouSpecifyState, GetouliuObj, GetNextDoorWrap, \
    GetObstacle, QuadKeyDownMap, QuadKeyUpMap, GetTaskObj, Clear, IsMenDead, IsLockedHp, UnLockHp, IsFuzhongGou, \
    Zuobiaoyidong, Autoshuntu, GetCurmapXy, HavePilao, GetMapInfo, IsShitmoGu, BagHasFenjieEquip, GetSelectObj, \
    GetCurSelectIdx, IsFirstSelect, IsLastSelect, BagWuseNum, IsCurrentSupport, Openesc, IsCurrentInTrain, \
    GetRemaindPilao, IsZhicai

gamebegin = Picture(GetImgDir() + "gamebegin2.png")
selectregion = Picture(GetImgDir() + "select_region.png", classname="TWINCONTROL", windowname="地下城与勇士登录程序")
waitagain = Picture(GetImgDir() + "wait.png", classname="TWINCONTROL", windowname="地下城与勇士登录程序")
maoxiantuanshezhi = Picture(GetImgDir() + "mao'xuan'tuanshezhi.png")
closebtn = Picture(GetImgDir() + "closebtn.png")
quedingbtn = Picture(GetImgDir() + "queding.png")
fanhuibtn = Picture(GetImgDir() + "fanhuibtn.png")
quxiaobtn = Picture(GetImgDir() + "quxiaobtn.png")
keyishiyong = Picture(GetImgDir() + "keyishiyong.png")
queren3 = Picture(GetImgDir() + "queren3.png")
shitqueding = Picture(GetImgDir() + "shitqueding.png")  # TODO
loginqueding = Picture(GetImgDir() + "loginqueding.png", classname="TWINCONTROL", windowname="地下城与勇士登录程序")
lingqubtn1 = Picture(GetImgDir() + "lingqubtn.png", dx=158, dy=108, dw=36, dh=22)
lingqubtn2 = Picture(GetImgDir() + "lingqubtn.png", dx=211, dy=109, dw=36, dh=22)
lingqubtn3 = Picture(GetImgDir() + "lingqubtn.png", dx=263, dy=108, dw=36, dh=22)
lingqubtn4 = Picture(GetImgDir() + "lingqubtn.png", dx=315, dy=107, dw=36, dh=22)
yingbi = Picture(GetImgDir() + "yingbi.png", dx=156, dy=16, dw=22, dh=17)
xinfeng = Picture(GetImgDir() + "xinfeng.png", dx=179, dy=244, dw=14, dh=10)
pindaoxuanze = Picture(GetImgDir() + "pindaoxuanze.png", dx=362, dy=40, dw=54, dh=14)
putongjuese = Picture(GetImgDir() + "putongjuese.png")
aerwenfangxian = Picture(GetImgDir() + "aierwenfangxian.png")
lingqingnewbtn = Picture(GetImgDir() + "lingqingnewbtn.png", dx=381, dy=380, dw=41, dh=13)
dianxin = Picture(GetImgDir() + "dianxin.png", classname="TWINCONTROL", windowname="地下城与勇士登录程序")
youjian = Picture(GetImgDir() + "youjian.png", dx=241, dy=471, dw=300, dh=78)
xuanzejieshou = Picture(GetImgDir() + "xuanzejieshou.png")
queren_youjian = Picture(GetImgDir() + "queren_youjian.png")

# 多少毫秒执行一次状态机
StateMachineSleep = 0.01


class StateMachine:
    def __init__(self, owner):
        self.latestState = None
        self.currentState = None
        self.globalState = None
        self.owner = owner

    def ChangeState(self, newState):
        tmp = self.currentState
        self.currentState = newState
        logger.info("状态切换 %s -> %s" % (type(tmp), type(self.currentState)))

    def Update(self):
        if self.globalState is not None:
            self.globalState.Execute(self.owner)

        if self.currentState is not None:
            self.currentState.Execute(self.owner)


class Player:

    def __init__(self):
        # 上一次按下的键
        self.latestDown = None

        # 持有技能
        self.skills = Skills()

        # 当前选择的技能 (保存临时选择的状态,释放完毕才能选择下一个技能)
        self.curskill = None

        # 状态机
        self.stateMachine = StateMachine(self)

        # 移动路径列表
        self.pathfindinglst = []

        # 上一个等级 (用于判断是否需要加点)
        self.latestlevel = 0

        # 任务上下文
        self.taskctx = TaskCtx()

        # 障碍数据, 障碍数据包装 NewMapCache 更新
        self.d, self.ob = None, None

        # 下一个门的x, y  NewMapCache 更新
        self.doorx, self.doory = 0, 0

        # 上次clear的时间点,用于防止频繁clear
        self.latestClear = None

        # 上次发动锁血技能的时候
        self.latestlockhp = None

        # 上次所检查地图卡死时间 / 上次的疲劳
        self.latestfucktime = None
        self.latestpilao = None

        # 上次的所在小地图位置
        self.latestpos = None

        # 上次的地图名称(日志用)
        self.latestmapname = None

        # 累计金币/无色/时间
        self.latestmoney = None
        self.latestwuse = None
        self.latestusedtime = None

        # 流水表写入时间戳
        self.followingtimepoint = None

        # 上次检查卡死时间
        self.latestcheckkasi = None
        self.latestcheckpic = None

        # 上次喊话时间
        self.latestspeektimepoint = None

        # 上次鼠标移动
        self.latestmousemovetimepoint = None

    # 重置地图卡死信息
    def ResetStuckInfo(self):
        self.latestfucktime = None
        self.latestpilao = None

    # 更改当前状态机
    def ChangeState(self, state):
        self.UpLatestKey()
        self.ClearPathfindingLst()
        self.taskctx.Clear()
        self.stateMachine.ChangeState(state)

    # 更改全局状态机
    def SetGlobalState(self, state):
        self.stateMachine.globalState = state

    # 更改之前的状态机
    def SetLatestState(self, state):
        self.stateMachine.latestState = state

    # 保存当前状态,并且切换到什么也不做的状态机
    def SaveAndChangeToEmpty(self, forwhat):
        logger.info("状态保存 currentState: %s" % type(self.stateMachine.currentState))
        self.SetLatestState(self.stateMachine.currentState)
        self.ChangeState(EmptyState(forwhat))

    # 恢复状态机
    def RestoreContext(self):
        logger.info("状态恢复 latestState: %s" % type(self.stateMachine.latestState))
        self.ChangeState(self.stateMachine.latestState)
        self.SetLatestState(None)

    # 状态机为空白
    def InEmptyState(self):
        if isinstance(self.stateMachine.currentState, EmptyState):
            return True
        else:
            return False

    # 当前空白状态机是否是因指定原因进入的
    def IsEmptyFor(self, forwhat):
        if isinstance(self.stateMachine.currentState, EmptyState) and \
                self.stateMachine.currentState.IsForwhat(forwhat):
            return True
        return False

    # 更新状态机
    def Update(self):
        self.stateMachine.Update()

    # 键已经按过
    def KeyDowned(self):
        return self.latestDown is not None

    # 重置键盘
    def ResetKey(self):
        self.latestDown = None

    # 按下键
    def DownKey(self, quad):
        QuadKeyDownMap[quad]()
        self.latestDown = quad

    # 恢复之前按的键
    def UpLatestKey(self):
        ReleaseAllKey()
        self.ResetKey()

    # 随机选择一种技能
    def SelectSkill(self):
        self.skills.Update()
        if random.uniform(0, 1) < 0.05:
            self.curskill = simpleAttackSkill
        else:
            self.curskill = self.skills.GetMaxLevelAttackSkill()
            if self.curskill is None:
                self.curskill = simpleAttackSkill

    # 使用掉随机选择的技能
    def UseSkill(self):
        self.curskill.Use()
        self.curskill = None

    # 是否已经选择了技能
    def HasSkillHasBeenSelect(self):
        return self.curskill is not None

    # 是否面向对方
    def IsChaoxiangDuifang(self, menx, objx):
        objlocation = GetFangxiang(menx, objx)
        menfangxiang = GetMenChaoxiang()
        if objlocation != menfangxiang:
            return False
        return True

    # 朝向对方
    def ChaoxiangFangxiang(self, menx, objx):
        monlocation = GetFangxiang(menx, objx)
        menfangxiang = GetMenChaoxiang()
        # 调整朝向
        if menfangxiang == RIGHT and monlocation == LEFT:
            logger.info("调整朝向 人物: %d 怪物: %d, 向左调整" % (menfangxiang, monlocation))
            PressLeft()
        elif menfangxiang == LEFT and monlocation == RIGHT:
            logger.info("调整朝向 人物: %d 怪物: %d, 向右调整" % (menfangxiang, monlocation))
            PressRight()

    # 疾跑
    def KeyJiPao(self, fangxiang):
        if fangxiang == RIGHT:
            JiPaoYou()
        else:
            JiPaoZuo()

    # 靠近
    def Seek(self, destx, desty, obj=None, dummy=None):
        menx, meny = GetMenXY()
        quad, rent = GetQuadrant(menx, meny, destx, desty)

        # 方向是否有障碍物
        if self.ob.ManQuadHasObstacle(quad, menx, meny):
            self.ChaoxiangFangxiang(menx, destx)
            logger.info("方向上有障碍物, 攻击")
            self.UpLatestKey()
            self.SelectSkill()
            self.UseSkill()
            self.ob.UpdateObstacle(GetObstacle())
            return

        objname = ""
        if obj is not None:
            objname = "name:%s obj:0x%X hp:%d " % (obj.name, obj.object, obj.hp) if obj is not None else ""
        if dummy is not None:
            objname = "dummy: %s" % dummy

        jizou = not WithInManzou(menx, meny, destx, desty)
        jizoustr = "" if not jizou else "疾走"

        if self.KeyDowned():
            if jizou and not IsManJipao():
                logger.info("不在疾跑退出状态,重新来过")
                self.UpLatestKey()
                return

            latestDecompose = QuardantMap[self.latestDown]
            currentDecompose = QuardantMap[quad]

            # 上次的按键在本次方向中没找到就弹起
            for keydown in latestDecompose:
                if keydown not in currentDecompose:
                    QuadKeyUpMap[keydown]()
            self.DownKey(quad), RanSleep(0.02)
            logger.info("seek: 本人(%.f, %.f) 目标%s (%.f, %.f)在%s, 保持部分移动方向 %s" % (
                menx, meny, objname, destx, desty, quad.name, jizoustr))
        else:
            # 没有按过键
            self.UpLatestKey()
            if jizou:
                self.KeyJiPao(GetFangxiang(menx, destx))
            self.DownKey(quad), RanSleep(0.02)
            logger.info("seek: 本人(%.f, %.f) 目标%s(%.f, %.f)在%s, 首次靠近 %s" % (
                menx, meny, objname, destx, desty, quad.name, jizoustr))

    # 靠近(带寻路)
    def SeekWithPathfinding(self, destx, desty, obj=None, dummy=None):
        if IsShitmoGu():
            self.Seek(destx, desty, obj, dummy=dummy)
            return

        menx, meny = GetMenXY()
        menx, meny = int(menx), int(meny)

        quad, _ = GetQuadrant(menx, meny, destx, desty)

        if len(self.pathfindinglst) == 0:
            # 范围内有麻烦就路径规划一下

            if self.ob.ManQuadHasTrouble(quad, menx, meny):
                self.UpLatestKey(), RanSleep(0.02)
                menx, meny = GetMenXY()
                menx, meny = int(menx), int(meny)

                logger.warning("前往目的地有障碍物, 开始规划(%d, %d) -> (%d, %d)" % (menx, meny, destx, desty))
                lst, err = GetPaths(self.d, self.ob, [menx, meny], [destx, desty])

                # 如果没有点,a*规划错了. 点必然最少也是2个以上,起始点和终点
                if err is not None or len(lst) < 2:
                    # 把当前所有缓存刷新下
                    logger.warning("规划错误,刷新地图缓存 (%d, %d) -> (%d, %d)" % (menx, meny, destx, desty))
                    self.NewMapCache()
                    # self.SeekWithPathfinding(destx, desty, obj, dummy)
                    return

                s = ""
                for v in lst:
                    firstPoint = idxToXY(v, self.d.mapw // 10)
                    s += "(%d, %d) " % (firstPoint[0], firstPoint[1])

                logger.info("路径规划一共%d 个路程点 %s" % (len(lst), s))
                self.pathfindinglst = lst
                # self.SeekWithPathfinding(destx, desty, obj, dummy)
                return

            else:
                logger.info("没有障碍物直接过去 (%d, %d)" % (destx, desty))
                self.Seek(destx, desty, obj, dummy)
                return
        elif len(self.pathfindinglst) == 1:
            point = idxToXY(self.pathfindinglst[0], self.d.mapw // 10)
            logger.info("就一个最终目的规划点了,直接过去 (%d, %d)" % (point[0], point[1]))
            del self.pathfindinglst[0]
            self.Seek(point[0], point[1], obj, dummy)
            return
        elif len(self.pathfindinglst) >= 2:
            # 路径规划过
            firstPoint = idxToXY(self.pathfindinglst[0], self.d.mapw // 10)
            secondPoint = idxToZuobiao(self.pathfindinglst[1], self.d.mapw // 10)

            menCoord = Zuobiao(menx, meny)
            flag = False
            if IsClosedTo(menCoord.x, menCoord.y, firstPoint[0], firstPoint[1]):
                flag = True
                logger.info("直接设置到达当前点 (%d, %d) (%d, %d)" % (
                    menCoord.x, menCoord.y, firstPoint[0], firstPoint[1]))

            if not flag:
                flag = self.ob.CanTwoPointBeMove(menCoord, secondPoint)
                logger.info("检测 %s -> %s 是否连通下一个点: %d" % (menCoord, secondPoint, flag))

            if flag:
                logger.info("到达了规划点 (%d, %d) 剩余 %d" % (firstPoint[0], firstPoint[1], len(self.pathfindinglst) - 1))
                del self.pathfindinglst[0]
                # self.SeekWithPathfinding(destx, desty, obj, dummy)
                return
            else:
                dummy = "" if dummy is None else dummy
                self.Seek(firstPoint[0], firstPoint[1], obj, dummy=dummy + "(寻路)")
                return

    # 因为到达目的地了清空当前寻路
    def ClearPathfindingLst(self):
        self.pathfindinglst = []

    # 每次进图缓存一下当前的 1. 地形 2. 障碍 3. 门位置.
    def NewMapCache(self):
        if not IsManInMap():
            return

        mapinfo = GetMapInfo()
        self.latestpos = (mapinfo.curx, mapinfo.cury)
        self.ClearPathfindingLst()

        t1 = time.time()
        meninfo = GetMenInfo()

        try:
            self.d, self.ob = SafeGetDAndOb(meninfo.w, meninfo.h)
        except Exception as err:
            logger.warning("获取障碍物发生错误 %s" % err)
            return

        if not IsCurrentInBossFangjian():
            door = GetNextDoorWrap()

            if IsShitmoGu():
                self.doorx, self.doory = door.x + door.w // 2, door.y + door.h // 2
            else:
                self.doorx, self.doory = GetCorrectDoorXY(self.d.mapw, self.d.maph, door, self.ob)
            logger.info("下一个门的坐标: (%d, %d) ->修正 (%d, %d) " % (door.x, door.y, self.doorx, self.doory))

        t2 = time.time()

        logger.info("获取了地图地形,障碍物数据 共花费: %f", t2 - t1)

    # 切换到新的图
    def CheckInToNewMap(self):
        self.UpLatestKey()
        self.ResetStuckInfo()
        logger.info("进了新的房间")
        RanSleep(0.3)
        self.NewMapCache()
        self.ChangeState(StandState())

    # 是否等级变化
    def HasLevelChanged(self):
        meninfo = GetMenInfo()

        # 角色等级1,处理一下
        if meninfo.level == 1 and self.latestlevel == 0:
            self.latestlevel = meninfo.level
            return True

        if self.latestlevel == 0:
            # 刚初始化 (不加) TODO
            self.latestlevel = meninfo.level
            return True
        elif self.latestlevel != meninfo.level:
            # 变化了等级
            self.latestlevel = meninfo.level
            return True
        else:
            # 没有变化等级
            return False

    # 是否小地图位置发生变化
    def IsMapPosChange(self, pos):
        return self.latestpos != pos


class State:
    def Execute(self, player):
        pass


FOR_DUIHUA = 0
FOR_CONFIRM = 1
FOR_SHIPIN = 2


# 什么也不做的状态机. 一般是由于对话,动画或者视频才进入到这里,读取信息供外面恢复
class EmptyState:
    def __init__(self, forwhat):
        self.forwhat = forwhat

    def Execute(self, player):
        pass

    def IsForwhat(self, forwat):
        return self.forwhat == forwat


# 有视频的包装
def IsShiPinTopWrap():
    if IsManInChengzhen():
        return IsShipinTop()

    return False


# 全局状态机
class GlobalState(State):
    def __init__(self):
        self.beginx = None
        self.beginy = None
        self.latesttime = None

    def Reset(self):
        self.beginx = None
        self.beginy = None
        self.latesttime = None

    def Execute(self, player):
        if isinstance(player.stateMachine.currentState, OpenGame):
            return

        # 领取
        if IsManInChengzhen() and not isinstance(player.stateMachine.currentState, Setup):
            # 领取 (阶段奖励)
            if xinfeng.Match():
                lingqus = [lingqubtn1, lingqubtn2, lingqubtn3, lingqubtn4]
                for lingqu in lingqus:
                    if lingqu.Match():
                        pos = lingqu.Pos()
                        MouseMoveTo(pos[0] + lingqu.dx, pos[1] + lingqu.dy), KongjianSleep()
                        MouseLeftClick(), KongjianSleep()

            # 选择地图,艾尔文防线
            if aerwenfangxian.Match():
                pos = aerwenfangxian.Pos()
                MouseMoveTo(pos[0], pos[1]), KongjianSleep()
                MouseLeftClick(), KongjianSleep()

            # 领取 (黄色按钮那个)
            if lingqingnewbtn.Match():
                pos = lingqingnewbtn.Pos()
                MouseMoveTo(pos[0], pos[1]), KongjianSleep()
                MouseLeftClick(), KongjianSleep()

                PressKey(VK_CODE['esc']), KongjianSleep()

            # 每隔5分钟讲一句台词
            if player.latestspeektimepoint is None or time.time() - player.latestspeektimepoint > 5 * 60:
                if player.latestspeektimepoint is None:
                    player.latestspeektimepoint = time.time()
                    logger.info("第一次不喊话! 过5分钟再喊")
                else:
                    player.latestspeektimepoint = time.time()
                    logger.info("开始喊话")
                    PressKey(VK_CODE['esc']), KongjianSleep()
                    PressKey(VK_CODE['enter']), KongjianSleep()
                    KeyInputString(Getyulu()), RanSleep(0.3)
                    PressKey(VK_CODE['enter']), KongjianSleep()
                    RanSleep(1.0)
                    logger.info("喊话成功")

            # 每隔30s 随便移动下鼠标
            t = random.uniform(5, 30)
            if player.latestmousemovetimepoint is None or time.time() - player.latestmousemovetimepoint > t:
                logger.info("随机移动鼠标")
                player.latestmousemovetimepoint = time.time()
                dx = int(random.uniform(0, 800))
                dy = int(random.uniform(0, 600))
                MouseMoveTo(dx, dy), RanSleep(1)

            # 制裁判断
            if IsZhicai():
                menname = GetMenInfo().name
                logger.warning("制裁了!!!!! %s %s %s 游戏结束" % (GetAccount(), GetRegion(), menname))
                DbEventAppend(GetAccount(), GetRegion(), menname, "制裁了")
                DbStateUpdate(GetAccount(), GetRegion(), kicktime=int(time.time()),
                              kicklong=24 * 60 * 60)  # 默认24小时吧
                os.system("taskkill /F /im DNF.exe"), RanSleep(5.0)
                return

        states = [SelectJuese, CreateRole, OpenGame, Train]

        def IsCurstateFlag(curstate):
            for s in states:
                if isinstance(curstate, s):
                    return True
            return False

        # 在游戏状态中
        if not IsCurstateFlag(player.stateMachine.currentState) and \
                (player.latestcheckkasi is None or (time.time() - player.latestcheckkasi) > 60):
            # 60s检查下是否卡死或者闪退了
            if player.latestcheckpic is not None:

                curpic = WindowCaptureToMem("地下城与勇士", "地下城与勇士")

                if (curpic == player.latestcheckpic).all():
                    logger.warning("超过60s游戏画面未动,关闭dnf")
                    os.system("taskkill /F /im DNF.exe"), RanSleep(5.0)
                    player.ChangeState(OpenGame())

                    player.latestcheckpic = None
                    player.latestcheckkasi = None
                    return

                player.latestcheckkasi = time.time()
                player.latestcheckpic = curpic

            else:
                player.latestcheckkasi = time.time()
                player.latestcheckpic = WindowCaptureToMem("地下城与勇士", "地下城与勇士")

            #  游戏进程不存在
            if not checkIfProcessRunning("DNF.exe"):
                player.ChangeState(OpenGame())
                player.latestcheckpic = None
                player.latestcheckkasi = None
                return

        # 锁血处理
        if IsLockedHp():
            if player.latestlockhp is None:
                player.latestlockhp = time.time()
            elif time.time() - player.latestlockhp > 10.0:
                logger.info("解除锁血")
                UnLockHp()
                player.latestlockhp = None

        # 视频处理
        if player.IsEmptyFor(FOR_SHIPIN):
            logger.info("视频状态")
            PressKey(VK_CODE["esc"]), RanSleep(0.3)
            PressKey(VK_CODE["spacebar"]), KongjianSleep()
            if not IsShiPinTopWrap():
                player.RestoreContext()
            return
        # 对话处理
        elif player.IsEmptyFor(FOR_DUIHUA):

            # 对话框有,但是被视频挡住了,临时切过去
            if IsShipinTop():
                player.ChangeState(EmptyState(FOR_SHIPIN))
                return

            logger.info("对话状态")
            PressKey(VK_CODE["spacebar"]), KongjianSleep()
            if not IsWindowTop():
                player.RestoreContext()
            return
        # 确认处理
        elif player.IsEmptyFor(FOR_CONFIRM):
            logger.info("确认状态")
            if IsConfirmTop():
                confirmPos = GetConfirmPos()
                if confirmPos != (0, 0):
                    MouseMoveTo(confirmPos[0], confirmPos[1]), KongjianSleep()
                    MouseLeftClick(), KongjianSleep()
                else:
                    logger.info("没有找到确认按钮位置")
            else:
                logger.info("确认按钮没有置顶")

            RanSleep(0.1)
            if not IsConfirmTop():
                player.RestoreContext()
            return

        # 视频判断
        if not player.IsEmptyFor(FOR_SHIPIN) and IsShiPinTopWrap():
            player.SaveAndChangeToEmpty(FOR_SHIPIN)
            return
        # 对话判断
        elif not player.IsEmptyFor(FOR_DUIHUA) and IsWindowTop():
            player.SaveAndChangeToEmpty(FOR_DUIHUA)
            return
        # 确认按钮
        elif not player.IsEmptyFor(FOR_CONFIRM) and IsConfirmTop():
            player.SaveAndChangeToEmpty(FOR_CONFIRM)
            return

        # 特定状态下才进行判断卡死
        if IsManInMap() and not isinstance(player.stateMachine.currentState, FubenOver):
            if self.latesttime is None:
                self.latesttime = time.time()
                self.beginx, self.beginy = GetMenXY()

            # 多久时间判断一次
            checktime = 1.5
            if len(player.pathfindinglst) > 0:
                checktime = 2.0

            if time.time() - self.latesttime > checktime:
                latestx, latesty = self.beginx, self.beginy
                curx, cury = GetMenXY()
                self.Reset()

                # 去下一个门的时候卡死了
                if isinstance(player.stateMachine.currentState, DoorOpenGotoNext):
                    if IsClosedTo(latestx, latesty, curx, cury, 40):
                        logger.warning("去下一个门的时候卡死了, 回退一些再进门")
                        player.NewMapCache()
                        player.ChangeState(DoorStuckGoToPrev())
                    else:
                        logger.info("坐标不相同: (%d, %d)   (%d, %d)" % (latestx, latesty, curx, cury))

                elif IsClosedTo(latestx, latesty, curx, cury):
                    logger.warning("卡死了,重置状态")
                    player.NewMapCache()
                    player.ChangeState(StandState())
                else:
                    logger.info("坐标在移动")
        else:
            self.Reset()

        if IsManInMap() and not isinstance(player.stateMachine.currentState, FubenOver):
            if player.latestfucktime is None:
                player.latestfucktime = time.time()
                player.latestpilao = GetRemaindPilao()
            elif time.time() - player.latestfucktime > 90:
                if player.latestpilao == GetRemaindPilao():
                    logger.warning("90s了疲劳还没有变,纠正一下")
                    player.ChangeState(StuckShit())
                player.ResetStuckInfo()

        # 流水表,不影响图内效率
        # if not IsManInMap():
        #     pass


import psutil


def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


# 初始化
class Setup(State):
    def Execute(self, player):
        # 当前游戏没运行
        if not checkIfProcessRunning("DNF.exe"):
            player.ChangeState(OpenGame())
            return

        # 设置当前账号和大区
        if not IsAccountSetted():

            meninfo = GetMenInfo()
            if meninfo.account != 0 and meninfo.region != "":

                accounts = GetSettingAccounts()
                for i, account in enumerate(accounts):
                    if int(account.account) == meninfo.account and \
                            meninfo.region in account.region:
                        logger.info("寻找到了账号 大区 %d %s" % (int(account.account), account.region))
                        SetCurrentAccount(account.account, account.region)
                        break

                else:
                    PrintSwitchTips()
                    BlockGetSetting()

            if not IsAccountSetted():
                logger.warning("本账号或许没有在配置文件中出现")
                PrintSwitchTips()
                BlockGetSetting()

        # 选择角色
        if gamebegin.Match():
            player.ChangeState(SelectJuese())
            return

        # 焦点移动到DNF
        RanSleep(1.0), GameWindowToTop()
        MouseMoveTo(1, 1), KongjianSleep()
        MouseLeftClick(), KongjianSleep()

        # 重新选择角色
        if IsManInChengzhen() and not IsCurrentSupport():
            if not Openesc():
                logger.warning("打开esc失败")
                return
            if not OpenSelect():
                logger.warning("返回选择角色失败")
                return
            player.ChangeState(SelectJuese())
            return

        if IsManInMap():
            player.ChangeState(FirstInMap())
            return

        if IsManInChengzhen():
            player.ChangeState(InChengzhen())
            return

        logger.warning("setup状态...")
        RanSleep(0.1)


# 城镇
class InChengzhen(State):
    def Execute(self, player):
        meninfo = GetMenInfo()
        deal = DealEquip()
        eq = Equips()

        # 频道选择界面 (让你选频道说明网络不好呀)
        if pindaoxuanze.Match():
            logger.warning("频道切换?")
            os.system("taskkill /F /im DNF.exe"), RanSleep(5.0)
            player.ChangeState(OpenGame())
            return

        # 关闭弹窗
        if closebtn.Match():
            logger.info("关闭弹窗!")
            pos = closebtn.Pos()
            MouseMoveTo(pos[0], pos[1]), KongjianSleep()
            MouseLeftClick(), KongjianSleep()

        # 只有一个角色是一级, 并且在城镇
        if AccountRoles(GetAccount(), GetRegion()) == 1 and IsManInChengzhen() and GetMenInfo().level == 1:
            logger.info("开启跳过所有动画")
            if not Openesc():
                logger.warning("打开esc失败")
                return

            # "游戏设置"
            MouseMoveTo(280, 452), KongjianSleep()
            MouseLeftClick(), RanSleep(1)

            # "系统"
            MouseMoveTo(312, 168), KongjianSleep()
            MouseLeftClick(), RanSleep(1)

            # "自动跳过动画" 下拉框
            MouseMoveTo(419, 416), KongjianSleep()
            MouseLeftClick(), RanSleep(1)

            # "跳过所有动画"
            MouseMoveTo(321, 452), KongjianSleep()
            MouseLeftClick(), RanSleep(1)

            # "保存"
            MouseMoveTo(371, 448), KongjianSleep()
            MouseLeftClick(), RanSleep(1)

            RanSleep(3)

        # 如果在图内,切换到图内
        if IsManInMap():
            player.ChangeState(FirstInMap())
            return

        # 领取邮件
        if youjian.Match():
            player.ChangeState(GetEmail())
            return

        # 等级发生变化, 技能加点
        if player.HasLevelChanged():
            player.ChangeState(SettingSkill())
            return

        # 等级 >= 10, 身上,背包没有合适的幸运星武器
        if meninfo.level >= 10 and not eq.DoesHaveHireEquip() and \
                AccountXingyunxingRule(GetAccount(), GetRegion()) > 0 and \
                (meninfo.fuzhongmax > 0.0 and meninfo.fuzhongcur / meninfo.fuzhongmax < 0.70):
            player.ChangeState(HireEquip())
            return

        # 需要领取称号
        if eq.NeedGetChenghao():
            player.ChangeState(GetChenghao())
            return

        # 背包有更好的装备,更换装备
        if eq.DoesBagHaveBetterEquip():
            player.ChangeState(ChangeEquip())
            return

        # 负重超过一定程度,分解 (需要先到副本外)
        if meninfo.fuzhongmax > 0.0 and meninfo.fuzhongcur / meninfo.fuzhongmax > 0.65:
            pos = deal.GetFenjieJiPos()
            if pos is not None and pos != (0, 0):
                player.ChangeState(FenjieEquip())
                return

        # 疲劳没有了清空下背包
        # if not HavePilao() and meninfo.fuzhongcur / meninfo.fuzhongmax > 0.3:
        #     pos = deal.GetFenjieJiPos()
        #     if pos is not None and pos != (0, 0):
        #         player.ChangeState(FenjieEquip())
        #         return

        # 耐久小于25%,修理 (需要先到副本外)
        if deal.NeedRepair():
            pos = deal.GetFenjieJiPos()
            if pos is not None and pos != (0, 0):
                player.ChangeState(RepairEquip())
                return

        # 疲劳没了
        if not HavePilao():
            player.ChangeState(NoPilao())
            return

        # 做剧情任务
        if HasPlot():
            player.ChangeState(TaskState())
            return

        logger.info("城镇内,没有切换至其他状态"), RanSleep(0.1)


# 技能加点,移除不需要的技能,放入需要的技能
class SettingSkill(State):
    def Execute(self, player):
        logger.info("增加技能点")
        Clear()
        oc = Occupationkills()
        oc.AddSkillPoints()
        oc.RemoveNotInStrategy()
        oc.EquipSkillInStrategy()
        oc.CloseSkillScene()
        logger.info("加点完毕")
        player.ChangeState(InChengzhen())


# 换装备
class ChangeEquip(State):
    def Execute(self, player):
        logger.info("换装备")
        eq = Equips()
        eq.ChangeEquip()

        from superai.equip import CloseBagScene
        CloseBagScene()
        logger.info("换装备完毕")
        player.ChangeState(InChengzhen())


# 租聘武器
class HireEquip(State):
    def Execute(self, player):
        logger.info("租聘武器")
        eq = Equips()
        if eq.HaveEnoughXingyunxing():
            eq.ZupinWuqi()
            eq.CloseZupin()
        logger.info("租聘武器完毕")
        player.ChangeState(InChengzhen())


# 获取称号
class GetChenghao(State):
    def Execute(self, player):
        logger.info("获取称号")
        eq = Equips()
        if eq.NeedGetChenghao():
            eq.GetChenghao()
        logger.info("获取称号完毕")
        player.ChangeState(InChengzhen())


# 分解装备
class FenjieEquip(State):
    def Execute(self, player):
        logger.info("分解装备")
        deal = DealEquip()
        deal.FenjieAll()
        deal.CloseFenjie()
        logger.info("分解装备完毕")
        player.ChangeState(InChengzhen())

        UpdateMenState()


# 修理装备
class RepairEquip(State):
    def Execute(self, player):
        logger.info("修理装备")
        deal = DealEquip()
        deal.RepairAll()
        deal.CloseSell()
        logger.info("修理装备")
        player.ChangeState(InChengzhen())

        UpdateMenState()


# 副本结束, 尝试退出
class FubenOver(State):
    def Execute(self, player):
        PressKey(VK_CODE["esc"]), KongjianSleep()
        PressKey(VK_CODE["F12"]), KongjianSleep()
        if IsManInChengzhen():
            meninfo = GetMenInfo()
            DbEventAppend(account=GetAccount(), region=GetRegion(), role=meninfo.name,
                          content="副本:%s 刷完, 剩余: %d疲劳" % (player.latestmapname, GetRemaindPilao()))

            while IsEscTop():
                PressKey(VK_CODE["esc"]), KongjianSleep()
            player.ChangeState(InChengzhen())
            return

        if IsShipinTop():
            PressKey(VK_CODE["esc"]), RanSleep(0.3)
            PressKey(VK_CODE["spacebar"]), KongjianSleep()
            return

        UpdateMenState()

        RanSleep(0.1)


# 测试计数器 (无关大局)
testi = 0


# 随机移动判断是否坐标能够改变
def CanbeMovTest():
    global testi

    x1, y1 = GetMenXY()
    if testi % 4 == 0:
        PressLeft()
    elif testi % 4 == 1:
        PressRight()
    elif testi % 4 == 2:
        PressUp()
    elif testi % 4 == 3:
        PressDown()

    x2, y2 = GetMenXY()
    if x1 == x2 and y1 == y2:
        testi += 1
        return False
    testi = 0
    return True


# 初次进图,加buff
class FirstInMap(State):
    def Execute(self, player):
        if IsManInChengzhen():
            player.ChangeState(InChengzhen())
            return

        player.skills.Update()
        player.NewMapCache()
        player.ResetStuckInfo()

        if player.skills.HaveBuffCanBeUse():
            if not CanbeMovTest():
                logger.warning("没法移动位置 可能被什么遮挡了, 临时退出状态机"), RanSleep(0.5)
                return

            player.skills.Update()
            skills = player.skills.GetCanBeUseBuffSkills()
            for skill in skills:
                logger.info("使用buff: %s" % skill.name)
                skill.Use()
        else:
            logger.info("没有buffer可以使用")

        player.skills.Update()
        player.ChangeState(StandState())

        mapinfo = GetMapInfo()
        player.latestmapname = mapinfo.name


# 图内站立
class StandState(State):
    def Execute(self, player):
        if IsManInChengzhen():
            player.ChangeState(InChengzhen())
            return
        elif IsFuBenPass():
            # 打死boss后判断下物品
            RanSleep(0.2)
            if HaveGoods(player) and IsFuzhongGou():
                player.ChangeState(SeekAndPickUp())
                return
            else:
                player.ChangeState(FubenOver())
                return
        elif IsMenDead():
            player.ChangeState(DeadState())
            return
        elif IsJiZhouSpecifyState():
            player.ChangeState(FuckDuonierState())
            return
        elif HaveMonsters():
            player.ChangeState(SeekAndAttackMonster())
            return
        elif HaveGoods(player) and IsFuzhongGou():
            player.ChangeState(SeekAndPickUp())
            return
        elif HaveBuffs():
            player.ChangeState(PickBuf())
            return
        elif not IsCurrentInBossFangjian() and IsNextDoorOpen():
            player.ChangeState(DoorOpenGotoNext())
            return
        elif not IsCurrentInBossFangjian() and not IsNextDoorOpen():
            # 打死怪物后, 门可能不是马上就开, 直接靠近门
            player.ChangeState(DoorDidnotOpen())
            return
        else:
            if IsCurrentInBossFangjian():
                # 得不到怪物对象. 可能副本结束的瞬间 按esc吧!
                PressKey(VK_CODE["esc"]), KongjianSleep()

                # 把它再点掉,投机取巧
                if IsEscTop():
                    PressKey(VK_CODE["esc"]), KongjianSleep()

        RanSleep(0.1)
        player.UpLatestKey()
        logger.info("state can not switch")


# 靠近并攻击怪物
class SeekAndAttackMonster(State):

    def Execute(self, player):
        obj = NearestMonsterWrap()

        # 如果没有怪物了,那么切换状态
        if obj is None:
            player.ChangeState(StandState())
            return

        # 怪物在太远的距离, 有物品捡物
        if SpecifyMonsterIsToofar(obj) and HaveGoods(player) and IsFuzhongGou():
            player.ChangeState(SeekAndPickUp())
            return

        # 怪物在太远的距离, 有buff捡
        if SpecifyMonsterIsToofar(obj) and HaveBuffs():
            player.ChangeState(PickBuf())
            return

        # 没有选择技能就选择一个
        if not player.HasSkillHasBeenSelect():
            player.SelectSkill()
        men = GetMenInfo()

        # 在水平宽度内并且垂直宽度太近了, 远离
        if player.curskill.IsH_WInRange(men.y, obj.y) and \
                player.curskill.IsV_WTOOClose(men.x, obj.x):
            seekx, seeky = player.curskill.GetSeekXY(men.x, men.y, obj.x, obj.y)
            logger.info("目标太接近,无法攻击,选择合适位置: men:(%d,%d) obj:(%d,%d) seek(%d,%d), 技能%s 太靠近垂直水平(%d,%d)" %
                        (men.x, men.y, obj.x, obj.y, seekx, seeky, player.curskill.name,
                         player.curskill.skilldata.too_close_v_w, player.curskill.skilldata.h_w))

            # 后跳解决问题
            player.UpLatestKey()
            player.ClearPathfindingLst()
            if random.uniform(0, 1) < 0.8:
                PressHouTiao(), RanSleep(0.05)
            else:
                player.SeekWithPathfinding(seekx, seeky, dummy="合适攻击位置"), RanSleep(0.05)
            return

        # 在攻击的水平宽度和垂直宽度之内,攻击
        if player.curskill.IsH_WInRange(men.y, obj.y) and \
                player.curskill.isV_WInRange(men.x, obj.x):
            logger.info("目标在技能:%s 的攻击范围之内, 垂直水平: (%d,%d)" %
                        (player.curskill.name, player.curskill.skilldata.v_w, player.curskill.skilldata.h_w))
            player.UpLatestKey()
            player.ClearPathfindingLst()
            player.ChaoxiangFangxiang(men.x, obj.x)
            if player.IsChaoxiangDuifang(men.x, obj.x):
                player.UseSkill()

            # 阿甘左强行判断:
            if 28 <= men.level <= 32 and obj.name == "领主 - 阿甘左" and obj.hp <= 281818:
                PressKey(VK_CODE["6"]), KongjianSleep()
                logger.info("给阿甘左吃点香料")
            return

        # 靠近
        seekx, seeky = player.curskill.GetSeekXY(men.x, men.y, obj.x, obj.y)
        player.SeekWithPathfinding(seekx, seeky, obj)


# 极昼多尼尔难以攻击,攻击肉瘤状态
class FuckDuonierState(State):
    def Execute(self, player):
        if not IsJiZhouSpecifyState():
            player.ChangeState(StandState())
            return

        logger.info("fuck 多尼尔")
        obj = GetouliuObj()
        if obj is None:
            player.ChangeState(StandState())
            return

        men = GetMenInfo()
        if simpleAttackSkill.IsH_WInRange(men.y, obj.y) and \
                simpleAttackSkill.isV_WInRange(men.x, obj.x):
            logger.info("肉瘤在技能:%s 的攻击范围之内, 垂直水平: (%d,%d)" %
                        (simpleAttackSkill.name, simpleAttackSkill.skilldata.v_w, simpleAttackSkill.skilldata.h_w))
            player.UpLatestKey()
            player.ClearPathfindingLst()
            player.ChaoxiangFangxiang(men.x, obj.x)
            if player.IsChaoxiangDuifang(men.x, obj.x):
                simpleAttackSkill.Use()
            return

        # 靠近
        seekx, seeky = simpleAttackSkill.GetSeekXY(men.x, men.y, obj.x, obj.y)
        player.SeekWithPathfinding(seekx, seeky, dummy="多尼尔:" + obj.name)


# 靠近并捡取物品
class SeekAndPickUp(State):
    def Execute(self, player):
        obj = NearestGood(player)

        # 如果没有物品了,那么切换图内状态
        if obj is None:
            player.ChangeState(StandState())
            return

        # 有怪物在范围内,紧急切换
        if not ClosestMonsterIsToofar():
            player.ChangeState(SeekAndAttackMonster())
            return

        menx, meny = GetMenXY()
        if CanbePickup(menx, meny, obj.x, obj.y):
            # 上一次的跑动的按键恢复
            player.UpLatestKey()
            player.ClearPathfindingLst()
            logger.info("捡取 (%d,%d)" % (obj.x, obj.y)), RanSleep(0.05)
            PressX()
        else:
            player.SeekWithPathfinding(obj.x, obj.y, dummy="物品:" + obj.name)


# 靠近并捡起buff
class PickBuf(State):
    def Execute(self, player):
        obj = NearestBuf()

        # 如果没有buff了,那么切换图内状态
        if obj is None:
            player.ChangeState(StandState())
            return

        # 有怪物在范围内,紧急切换
        if not ClosestMonsterIsToofar():
            player.ChangeState(SeekAndAttackMonster())
            return

        menx, meny = GetMenXY()
        if CanbeGetBuff(menx, meny, obj.x, obj.y):
            # 上一次的跑动的按键恢复
            player.UpLatestKey()
            player.ClearPathfindingLst()
            logger.info("捡取buff (%d,%d)" % (obj.x, obj.y))
        else:
            player.SeekWithPathfinding(obj.x, obj.y, dummy="捡取buff")


# 门已开,去过图
class DoorOpenGotoNext(State):
    def __init__(self):
        self.begintime = time.time()

    def Execute(self, player):
        if time.time() - self.begintime > 10.0:
            player.ChangeState(StandState())
            return
        elif HaveMonsters():
            player.ChangeState(SeekAndAttackMonster())
            return
        elif HaveGoods(player) and IsFuzhongGou():
            player.ChangeState(SeekAndPickUp())
            return

        if player.IsMapPosChange(GetCurmapXy()):
            player.CheckInToNewMap()
        else:
            player.SeekWithPathfinding(player.doorx, player.doory, dummy="靠近门")


# 走门时卡死,走到离门远一些的地方
class DoorStuckGoToPrev(State):
    def __init__(self):
        self.begintime = time.time()

    def Execute(self, player):
        if time.time() - self.begintime > 10.0:
            player.ChangeState(StandState())
            return
        elif HaveMonsters():
            player.ChangeState(SeekAndAttackMonster())
            return
        elif HaveGoods(player) and IsFuzhongGou():
            player.ChangeState(SeekAndPickUp())
            return

        menx, meny = GetMenXY()
        door = GetNextDoorWrap()
        if player.IsMapPosChange(GetCurmapXy()):
            player.CheckInToNewMap()
        elif IsClosedTo(menx, meny, door.prevcx, door.prevcy):
            player.ChangeState(DoorOpenGotoNext())
        else:
            player.SeekWithPathfinding(door.prevcx, door.prevcy, dummy="靠近门前")


# 门还没开的瞬间
class DoorDidnotOpen(State):
    def __init__(self):
        self.begintime = time.time()

    def Execute(self, player):
        if time.time() - self.begintime > 2.0:
            player.ChangeState(StandState())
            return
        elif HaveMonsters():
            player.ChangeState(SeekAndAttackMonster())
            return
        elif HaveGoods(player) and IsFuzhongGou():
            player.ChangeState(SeekAndPickUp())
            return

        if player.IsMapPosChange(GetCurmapXy()):
            player.CheckInToNewMap()
        else:
            player.SeekWithPathfinding(player.doorx, player.doory, dummy="靠近门")


# 死亡
class DeadState(State):
    def Execute(self, player):
        meninfo = GetMenInfo()

        if meninfo.hp > 1:
            player.ChangeState(StandState())
            return

        if IsManInChengzhen():
            player.ChangeState(InChengzhen())
            return

        PressX(), RanSleep(0.3)


# 卡点模式
class StuckShit(State):
    def Execute(self, player):
        player.UpLatestKey()

        if HaveMonsters():
            obj = NearestMonsterWrap()
            if obj is not None:
                RanSleep(1.0)
                Zuobiaoyidong(obj.x, obj.y, 0)
            player.ChangeState(StandState())
        elif not IsCurrentInBossFangjian():
            RanSleep(1.0)
            Autoshuntu()
            player.ChangeState(StandState())
        elif IsFuBenPass():
            player.ChangeState(FubenOver())
            return
        else:
            logger.warning("不知道该怎么办,联系作者吧")
            player.ChangeState(StandState())


# 做任务状态机
class TaskState(State):
    def Execute(self, player):
        if not HasPlot():
            player.ChangeState(InChengzhen())
            return

        if IsManInMap():
            player.ChangeState(FirstInMap())
            return

        tasks = GetTaskObj()
        for v in tasks:
            if v.name in plotMap.keys():
                plotMap[v.name](player)

                if IsManInChengzhen():
                    eq = Equips()
                    # 背包有更好的装备,更换装备
                    if eq.DoesBagHaveBetterEquip():
                        player.ChangeState(ChangeEquip())
                        return

                break

        RanSleep(0.1)


# 没有疲劳,切换角色
class NoPilao(State):
    def Execute(self, player):
        logger.warning("疲劳没有了"), RanSleep(0.3)

        # 重新选择角色
        if IsManInChengzhen():
            if not Openesc():
                logger.warning("打开esc失败")
                return
            if not OpenSelect():
                logger.warning("返回选择角色失败")
                return

            player.ChangeState(SelectJuese())


# 选择角色
class SelectJuese(State):
    def Execute(self, player):
        if not IsAccountSetted():
            PrintSwitchTips()
            BlockGetSetting()

        # 焦点移动到DNF
        RanSleep(1.0), GameWindowToTop()
        MouseMoveTo(1, 1), KongjianSleep()
        MouseLeftClick(), KongjianSleep()

        outlst = GetSelectObj()
        if len(outlst) > 48:
            logger.warning("h获取角色列表失败")
            return

        for obj in outlst:
            DbStateUpdate(account=GetAccount(), region=GetRegion(), role=obj.name, curlevel=obj.level)

        if len(outlst) == 0 or not IsTodayHavePilao(account=GetAccount(), region=GetRegion()):
            curnums = AccountRoles(account=GetAccount(), region=GetRegion())
            daycreatenums = DayCreateJueseNum(account=GetAccount(), region=GetRegion())
            if curnums < 2 and daycreatenums < 2:
                logger.info("当前角色数量: %d , 小于2个, 创建角色" % curnums)
                player.ChangeState(CreateRole())
                return

            logger.warning("这个号不能再刷了"), RanSleep(0.3)

            for i in range(10):
                logger.warning("游戏即将结束!!! : %d" % (10 - i)), time.sleep(1)

            os.system("taskkill /F /im DNF.exe"), RanSleep(5.0)
            player.ChangeState(OpenGame())
            return

        # 选中第一个角色
        MouseMoveTo(128, 184), KongjianSleep()
        MouseLeftClick(), KongjianSleep()

        toselectidx = GetToSelectIdx(account=GetAccount(), region=GetRegion())

        logger.info("要选择角色的下标: %d" % toselectidx)
        logger.info("要选中角色: %s 等级: %d" % (outlst[toselectidx].name, outlst[toselectidx].level))

        curpress = PressRight

        for i in range(32):
            if toselectidx == GetCurSelectIdx().menidx:
                break

            if IsFirstSelect():
                curpress = PressRight
            elif IsLastSelect():
                curpress = PressLeft

            curpress(), RanSleep(0.3)

        if toselectidx != GetCurSelectIdx().menidx:
            logger.warning("没有选中要选择的角色")
            return

        RanSleep(1.0)

        # "游戏开始" 按钮. 按2下
        for i in range(2):
            MouseMoveTo(401, 543), KongjianSleep()
            MouseLeftClick(), KongjianSleep()

        for i in range(20):
            # 一级角色训练场景
            if IsCurrentInTrain():
                RanSleep(1), UpdateMenState()
                player.ChangeState(Train())
                RanSleep(1.0), GameWindowToTop()
                MouseMoveTo(2, 2), KongjianSleep()
                return
            elif IsManInChengzhen() and IsinSailiya():
                RanSleep(1), UpdateMenState()
                player.ChangeState(Setup())
                RanSleep(1.0), GameWindowToTop()
                MouseMoveTo(2, 2), KongjianSleep()
                ResetAllChongming()
                return
            elif closebtn.Match():
                # 关闭弹窗
                logger.info("关闭弹窗!")
                pos = closebtn.Pos()
                MouseMoveTo(pos[0], pos[1]), KongjianSleep()
                MouseLeftClick(), KongjianSleep()
            elif IsManInChengzhen():
                # 进入城镇后去掉一些弹出来的窗口
                PressKey(VK_CODE['esc']), KongjianSleep()
                while IsEscTop():
                    PressKey(VK_CODE['esc']), KongjianSleep()
            else:
                logger.info("等待进入城镇 %d " % i), RanSleep(1.0)

        logger.warning("在选择角色页面"), RanSleep(0.1)


jueselst = ["魔枪士", "女圣职者", "守护者", "女格斗家", "男鬼剑士"]  # "枪剑士" 太垃圾, 不放进去了

jueseseall = {
    "枪剑士": (127, 487),
    "女圣职者": (205, 487),
    "魔枪士": (283, 487),
    "男鬼剑士": (361, 487),
    "女鬼剑士": (437, 487),
    "男神枪手": (520, 487),
    "女神枪手": (588, 487),
    "男魔法师": (670, 487),
    "女魔法师": (127, 557),
    "守护者": (205, 557),
    "男格斗家": (283, 557),
    "女格斗家": (361, 557),
    "男圣职者": (437, 557),
    "暗夜使者": (520, 557),
    "黑暗武士": (588, 557),
    "缔造者": (670, 557),
}


# 创建角色
class CreateRole(State):
    def Execute(self, player):
        # 创建角色页面 -> 选择角色页面
        for i in range(3):
            if fanhuibtn.Match():
                pos = fanhuibtn.Pos()
                MouseMoveTo(pos[0], pos[1]), KongjianSleep()
                MouseLeftClick(), KongjianSleep()
            else:
                break

            RanSleep(1), logger.info("等待返回到选择角色页面")

        if fanhuibtn.Match():
            logger.warning("还在处于返回角色页面!!")
            return

        # 选择创建角色
        createJueselst = CreateJueses(account=GetAccount(), region=GetRegion())
        juesesetting = jueselst
        for juese in createJueselst:
            juese = juese["juese"]

            if juese in juesesetting:  juesesetting.remove(juese)

        if len(juesesetting) < 1:
            juesesetting = ["男鬼剑士"]

        logger.info("还剩下这些角色可以被创建: " + str(juesesetting))
        idx = random.randint(0, len(juesesetting) - 1)
        logger.info("创建: %s" % juesesetting[idx])

        # 创建角色页面
        for i in range(3):
            if fanhuibtn.Match():
                break
            # 创建角色按钮
            MouseMoveTo(173, 548), KongjianSleep()
            MouseLeftClick(), RanSleep(0.3)
            time.sleep(1), logger.info("等待进入创建角色页面")

        if not fanhuibtn.Match():
            logger.warning("没有在创建角色页面!!!")
            return

        # 取名字页面
        for i in range(3):
            if quxiaobtn.Match():
                break

            # 选择要创建的角色
            pos = jueseseall[juesesetting[idx]]
            MouseMoveTo(pos[0], pos[1]), KongjianSleep()
            MouseLeftClick(), RanSleep(1)

            # 点击 创建角色按钮
            MouseMoveTo(686, 430), KongjianSleep()
            MouseLeftClick(), RanSleep(0.3)

            RanSleep(1), logger.info("等待到取名字界面")

            if putongjuese.Match():
                pos = putongjuese.Pos()
                MouseMoveTo(pos[0], pos[1]), KongjianSleep()
                MouseLeftClick(), KongjianSleep()

        if not quxiaobtn.Match():
            logger.warning("没有在取名字页面!!!")
            return

        # 可以使用的id提示框
        for i in range(3):
            if keyishiyong.Match():
                break

            MouseMoveTo(436, 286), KongjianSleep()
            DeleteAll()

            # 输入名字
            toinput = names.get_full_name().replace(' ', random.choice(
                ['=', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']))
            KeyInputString(toinput), RanSleep(0.3)

            # 重复按钮
            MouseMoveTo(469, 287), KongjianSleep()
            MouseLeftClick(), KongjianSleep()
            MouseMoveTo(1, 1), KongjianSleep()

            RanSleep(1), logger.info("等待到id可以使用提示")

        if not keyishiyong.Match():
            logger.warning("没有出现可以使用的ID!!")
            return

        PressKey(VK_CODE['esc']), KongjianSleep()

        # 点击确认按钮
        MouseMoveTo(364, 353), KongjianSleep()
        MouseLeftClick(), KongjianSleep()
        MouseLeftClick(), KongjianSleep()

        MouseMoveTo(1, 1), KongjianSleep()
        for i in range(3):
            if queren3.Match():
                logger.info("把确认按钮点掉")
                PressKey(VK_CODE['esc']), KongjianSleep()
            RanSleep(1), logger.info("等待确认按钮安全消失")

        player.ChangeState(SelectJuese())
        CreateJueseAppend(account=GetAccount(), region=GetRegion(), juese=juesesetting[idx])


# 打开游戏
class OpenGame(State):
    def Execute(self, player):
        logger.info("开始打开游戏")

        # 游戏/登陆器关闭, 幂等
        for i in range(10):
            if checkIfProcessRunning("DNF.exe"):
                logger.warning("关闭DNF.exe")
                os.system("taskkill /F /im DNF.exe"), RanSleep(5.0)
            elif win32gui.FindWindow("TWINCONTROL", "地下城与勇士登录程序") != 0:
                logger.warning("关闭登陆器")
                os.system("taskkill /F /im Client.exe"), RanSleep(5.0)
            else:
                break
            time.sleep(1), logger.info("等待游戏/登陆器关闭")

        # 重新选择大区在最前面, 幂等
        hwnd = win32gui.FindWindow("TWINCONTROL", "地下城与勇士登录程序")
        if hwnd == 0:
            gamedir = GameFileDir()
            subprocess.Popen(gamedir)

        for i in range(100):
            ClientWindowToTop()
            if selectregion.Match():
                break
            logger.info("启动游戏 %d" % i), time.sleep(1)

        if not selectregion.Match():
            logger.warning("寻找不到 '重新选择大区' 按钮, 重新启动")
            return

        # 直到 "电信" 出现
        for i in range(3):
            if dianxin.Match():
                break

            # 选择 "重新选择大区按钮"
            pos = selectregion.Pos()
            MouseMoveToLogin(pos[0], pos[1]), KongjianSleep()
            MouseLeftClick(), RanSleep(1.0)

        if not dianxin.Match():
            logger.warning("寻找不到 '电信' 按钮, 重新启动")
            return

        # 选择合适的账号
        accounts = GetSettingAccounts()
        selectAccount = None
        # 账号没有在数据库中出现过
        for account in accounts:
            if AccountRoles(account.account, account.region) < 1:
                selectAccount = account
                logger.info("寻找到账号: %s %s 没有录入过数据库登录!" % (account.account, account.region))
                break
            else:

                if IsAccoutnZhicai(account.account):
                    logger.warning("账号制裁: %s %s" % (account.account, account.region))
                    continue

                if IsTodayHavePilao(account.account, account.region):
                    selectAccount = account
                    logger.info("寻找到账号: %s %s 还可以再刷! " % (account.account, account.region))
                    break

        if selectAccount is None:
            for i in range(3600):
                logger.warning("没有可以再刷的帐号了"), RanSleep(1.0)

            return

        SetCurrentAccount(selectAccount.account, selectAccount.region)

        daqu = GetDaqu(selectAccount.region)

        if daqu == "":
            raise Exception("不支持的大区: %s" % selectAccount.region)

        # 选择 "电信/联通"
        if daqu == "电信":
            MouseMoveToLogin(235, 149), RanSleep(1.0)
        if daqu == "联通":
            MouseMoveToLogin(236, 233), RanSleep(1.0)
        MouseLeftClick(), RanSleep(1.0)

        # 选择 "大区"
        logger.info("选择大区")
        pos = GetMainregionPos(selectAccount.region)
        MouseMoveToLogin(pos[0], pos[1]), KongjianSleep()
        MouseLeftClick(), RanSleep(1.0)

        # 选择 "服务器"
        logger.info("选择服务器")
        pos = GetRegionPos(selectAccount.region)
        MouseMoveToLogin(pos[0], pos[1]), KongjianSleep()
        MouseLeftClick(), RanSleep(1.0)

        # 选择 "登录游戏"
        logger.info("登录游戏")
        MouseMoveToLogin(1036, 557), RanSleep(0.3)
        MouseLeftClick(), RanSleep(1.0)

        logger.info("等待进度条加载")
        pic = Picture(GetImgDir() + "login_youxia.png", dx=1135, dy=617, dw=62, dh=20, classname="TWINCONTROL",
                      windowname="地下城与勇士登录程序")

        for i in range(30):
            # 延迟过高时, 点击 "继续等待" 按钮
            if waitagain.Match():
                logger.warning("延迟过大,继续等待"), RanSleep(0.3)
                pos = waitagain.Pos()

                logger.warning("pos: (%d,%d)" % (pos[0], pos[1])), RanSleep(0.3)
                MouseMoveToLogin(pos[0], pos[1]), KongjianSleep()
                MouseLeftClick(), RanSleep(1.0)
            elif pic.Match():
                break
            logger.info("没有加载完成 %d" % i), RanSleep(1)

        if not pic.Match():
            logger.warning("没有加载完成"), RanSleep(0.3)
            return

        # 输入账号
        MouseMoveToLogin(1125, 324), KongjianSleep()
        MouseLeftClick(), RanSleep(1.0)
        DeleteAll()
        KeyInputString(selectAccount.account), RanSleep(0.3)

        # 输入密码
        MouseMoveToLogin(1136, 370), KongjianSleep()
        MouseLeftClick(), RanSleep(1.0)
        # DeleteAll()
        KeyInputString(selectAccount.password), RanSleep(0.3)

        # 点击 "登录游戏"
        MouseMoveToLogin(1040, 500), RanSleep(0.3)
        MouseLeftClick(), KongjianSleep()

        SetCurrentAccount(selectAccount.account, selectAccount.region)

        # 等待6分钟
        for i in range(360):

            # 直接进入创建角色了
            if fanhuibtn.Match():
                pos = fanhuibtn.Pos()
                MouseMoveTo(pos[0], pos[1]), KongjianSleep()
                MouseLeftClick(), KongjianSleep()
            # 验证码
            elif loginqueding.Match():
                vercodepic = WindowCaptureToFile("TWINCONTROL", "地下城与勇士登录程序", GetvercodeDir(), 531, 341, 121, 43)

                if vercodepic == "":
                    logger.warning("截取验证码发生异常!!!!!")

                t = verifyfile(vercodepic)
                t = json.loads(t)

                if not t["result"]:
                    logger.warning("接口验证码识别错误")

                vercode = t["data"]["val"]

                # 输入验证码
                MouseMoveToLogin(514, 365), KongjianSleep()
                MouseLeftClick(), KongjianSleep()
                KeyInputString(vercode), KongjianSleep()

                # 确认验证码
                MouseMoveToLogin(538, 466), KongjianSleep()
                MouseLeftClick(), KongjianSleep()

            # 冒险团 没有设置过!!
            elif maoxiantuanshezhi.Match():
                time.sleep(1)

                MouseMoveTo(398, 289), KongjianSleep()
                MouseLeftClick(), KongjianSleep()
                toinput = names.get_full_name().replace(' ', random.choice(
                    ['=', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']))
                KeyInputString(toinput), RanSleep(0.3)

                # 设置
                MouseMoveTo(347, 425), KongjianSleep()
                MouseLeftClick(), KongjianSleep()

                # 确认
                MouseMoveTo(371, 364), KongjianSleep()
                MouseLeftClick(), KongjianSleep()

                # 确认
                MouseMoveTo(301, 322), KongjianSleep()
                MouseLeftClick(), KongjianSleep()

                # 返回
                MouseMoveTo(767, 21), KongjianSleep()
                MouseLeftClick(), KongjianSleep()

            elif gamebegin.Match():
                break
            logger.info("等待进入游戏 %d" % i), time.sleep(1)

        if gamebegin.Match():
            FlushPid()
            player.ChangeState(SelectJuese())
            return


class Train(State):
    def Execute(self, player):
        logger.info("正在训练场景! 直接退出!")

        for i in range(30):
            if IsManInChengzhen():
                player.ChangeState(InChengzhen())
                return
            else:
                MouseMoveTo(1, 1), KongjianSleep()
                PressKey(VK_CODE["esc"]), RanSleep(0.3)

                # 漫画/视频退出
                if quedingbtn.Match():
                    PressKey(VK_CODE['spacebar']), KongjianSleep()
                # 训练场景退出
                elif IsEscTop():
                    MouseMoveTo(490, 454), KongjianSleep()
                    MouseLeftClick(), KongjianSleep()
                    PressKey(VK_CODE['spacebar']), KongjianSleep()

            GameWindowToTop()
            time.sleep(1), logger.info("训练场景 %d", i)


class GetEmail(State):
    def Execute(self, player):
        logger.info("领取邮件")

        for i in range(3):
            if xuanzejieshou.Match():
                break
            pos = youjian.pos()
            MouseMoveTo(pos[0], pos[1]), KongjianSleep()
            MouseLeftClick(), KongjianSleep()
            RanSleep(1.0), logger.info("等待打开邮件")

        if not xuanzejieshou.Match():
            player.ChangeState(InChengzhen())
            return

        pos = xuanzejieshou.Pos()
        MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        MouseLeftClick(), RanSleep(1)

        if queren_youjian.Match():
            pos = queren_youjian.Pos()
            MouseMoveTo(pos[0], pos[1]), KongjianSleep()
            MouseLeftClick(), KongjianSleep()

        PressKey(VK_CODE['esc']), KongjianSleep()
        player.ChangeState(InChengzhen())


EXIT = False


# 热键监视线程
def Hotkey():
    while True:
        statealt = win32api.GetAsyncKeyState(VK_CODE['alt'])
        statetab = win32api.GetAsyncKeyState(VK_CODE['ctrl'])
        statek = win32api.GetAsyncKeyState(VK_CODE['q'])
        global EXIT
        if (statealt != 0 and statek != 0 and statetab != 0) or EXIT is True:
            EXIT = True
            logger.warning("exit!!!")
            break
        time.sleep(0.005)


# 置顶游戏线程
def GameTop():
    while not EXIT:
        if checkIfProcessRunning("DNF.exe"):
            # if checkIfProcessRunning("CrossProxy.exe"):
            #     logger.warning("发现 CrossProxy.exe, 关闭!!!")
            #     os.system("taskkill /F /im CrossProxy.exe"), RanSleep(1)

            #     if checkIfProcessRunning("TPHelper.exe"):
            #         logger.warning("发现 TPHelper.exe, 关闭!!!")
            #         os.system("taskkill /F /im TPHelper.exe"), RanSleep(1)

            pythoncom.CoInitialize()
            GameWindowToTop()
            time.sleep(10)


def superai():
    InitLog()
    if not GameApiInit():
        sys.exit()
    FlushPid()

    if not YijianshuInit():
        sys.exit()

    # 热键线程
    t = threading.Thread(target=Hotkey)
    t.start()

    # 置顶游戏线程
    t = threading.Thread(target=GameTop)
    t.start()

    GameWindowToTop(), time.sleep(1)

    # 截图线程
    t = threading.Thread(target=FlushImg)
    t.start()

    # 状态机 主线程
    player = Player()
    player.ChangeState(Setup())
    player.SetGlobalState(GlobalState())

    player.skills.Update()

    global EXIT
    try:
        while not EXIT:
            time.sleep(StateMachineSleep)
            player.Update()
    except KeyboardInterrupt:
        pass

    ReleaseAllKey()
    SetThreadExit()  # 截图线程退出
    EXIT = True  # 热键线程退出
    logger.info("main thread exit")


def main():
    # 初始化数据库
    InitDb()

    # jsonrpc websocket 推送
    t = threading.Thread(target=subnodeapi)
    t.start()

    superai()


if __name__ == "__main__":
    main()
