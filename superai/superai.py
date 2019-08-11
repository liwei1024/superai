import logging
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

logger = logging.getLogger(__name__)

import threading
import win32gui
import math
import random
import time

from superai.common import InitLog

from superai.astarpath import GetPaths, GetCorrectDoorXY, idxToZuobiao, CoordToManIdx, SafeGetDAndOb
from superai.astartdemo import idxToXY

from superai.flannfind import FlushImg, IsCartoonTop, IsVideoTop, SetThreadExit, \
    IsConfirmTop, GetConfirmPos

from superai.vkcode import VK_CODE

from superai.yijianshu import YijianshuInit, DownZUO, DownYOU, DownXIA, DownSHANG, DownZUOSHANG, DownZUOXIA, \
    DownYOUSHANG, DownYOUXIA, PressRight, \
    PressLeft, JiPaoZuo, JiPaoYou, ReleaseAllKey, PressX, PressHouTiao, RanSleep, UpZUO, UpYOU, UpSHANG, \
    UpXIA, UpZUOSHANG, UpZUOXIA, UpYOUSHANG, UpYOUXIA, PressKey, MouseMoveTo, MouseLeftClick, PressUp, PressDown

from superai.gameapi import GameApiInit, FlushPid, \
    HaveMonsters, GetMenXY, GetQuadrant, Quardant, \
    GetMenChaoxiang, RIGHT, Skills, LEFT, HaveGoods, \
    NearestGood, IsNextDoorOpen, IsCurrentInBossFangjian, GetMenInfo, \
    CanbePickup, WithInManzou, GetFangxiang, ClosestMonsterIsToofar, simpleAttackSkill, IsClosedTo, \
    NearestBuf, HaveBuffs, CanbeGetBuff, SpecifyMonsterIsToofar, IsManInMap, IsManInChengzhen, QuardantMap, IsManJipao, \
    NearestMonsterWrap, IsWindowTop, IsEscTop, IsFuBenPass, IsJiZhouSpecifyState, GetouliuObj, GetNextDoorWrap, \
    GetObstacle, WithInRange

QuadKeyDownMap = {
    Quardant.ZUO: DownZUO,
    Quardant.YOU: DownYOU,
    Quardant.SHANG: DownSHANG,
    Quardant.XIA: DownXIA,
    Quardant.ZUOSHANG: DownZUOSHANG,
    Quardant.ZUOXIA: DownZUOXIA,
    Quardant.YOUSHANG: DownYOUSHANG,
    Quardant.YOUXIA: DownYOUXIA
}

QuadKeyUpMap = {
    Quardant.ZUO: UpZUO,
    Quardant.YOU: UpYOU,
    Quardant.SHANG: UpSHANG,
    Quardant.XIA: UpXIA,
    Quardant.ZUOSHANG: UpZUOSHANG,
    Quardant.ZUOXIA: UpZUOXIA,
    Quardant.YOUSHANG: UpYOUSHANG,
    Quardant.YOUXIA: UpYOUXIA
}

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

    # 更改当前状态机
    def ChangeState(self, state):
        self.UpLatestKey()
        self.ClearPathfindingLst()
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
        if random.uniform(0, 1) < 0.1:
            self.curskill = simpleAttackSkill
        else:
            self.curskill = self.skills.GetMaxLevelAttackSkill()
            if self.curskill is None:
                self.curskill = simpleAttackSkill

    # 使用掉随机选择的技能
    def UseSkill(self):
        self.curskill.Use()
        self.skills.Update()
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

        objname = ""
        if obj is not None:
            objname = "name:%s obj:0x%X hp:%d " % (obj.name, obj.object, obj.hp) if obj is not None else ""
        if dummy is not None:
            objname = "dummy: %s" % dummy

        jizou = not WithInManzou(menx, meny, destx, desty)
        jizoustr = "" if not jizou else "疾走"

        if quad == Quardant.CHONGDIE:
            # 已经重叠了, 调用者(靠近怪物, 捡物, 过门 应该不会再次调用seek了). 频繁发生就说明写错了
            self.UpLatestKey()
            RanSleep(0.05)
            logger.info("seek: 本人(%.f, %.f) 目标%s (%.f, %.f)在%s, 重叠 %s" % (
                menx, meny, objname, destx, desty, quad.name, jizoustr))
            return

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
            self.DownKey(quad)
            RanSleep(0.05)
            logger.info("seek: 本人(%.f, %.f) 目标%s (%.f, %.f)在%s, 保持部分移动方向 %s" % (
                menx, meny, objname, destx, desty, quad.name, jizoustr))
        else:
            # 没有按过键
            self.UpLatestKey()
            if jizou:
                self.KeyJiPao(GetFangxiang(menx, destx))
            self.DownKey(quad)
            RanSleep(0.05)
            logger.info("seek: 本人(%.f, %.f) 目标%s(%.f, %.f)在%s, 首次靠近 %s" % (
                menx, meny, objname, destx, desty, quad.name, jizoustr))

    # 靠近(带寻路)
    def SeekWithPathfinding(self, destx, desty, obj=None, dummy=None):
        menx, meny = GetMenXY()
        menx, meny = int(menx), int(meny)

        # 方向是否有障碍物
        self.ob.UpdateObstacle(GetObstacle())
        quad, _ = GetQuadrant(menx, meny, destx, desty)

        if quad == Quardant.CHONGDIE:
            logger.info("寻路 重叠了")
            return

        if quad != Quardant.CHONGDIE:
            if self.ob.ManQuadHasObstacle(quad, menx, meny):
                logger.info("方向上有障碍物, 攻击")
                self.UpLatestKey()
                PressX()
                return

        if len(self.pathfindinglst) == 0:
            # 范围内有麻烦就路径规划一下

            if self.ob.ManQuadHasTrouble(quad, menx, meny):
                logger.warning("前往目的地有障碍物, 开始规划(%d, %d) -> (%d, %d)" % (menx, meny, destx, desty))
                lst, err = GetPaths(self.d, self.ob, [menx, meny], [destx, desty])

                # 如果没有点,a*规划错了. 点必然最少也是2个以上,起始点和终点
                if err is not None or len(lst) < 2:
                    # 把当前所有缓存刷新下
                    logger.warning("规划错误,刷新地图缓存 (%d, %d) -> (%d, %d)" % (menx, meny, destx, desty))
                    self.NewMapCache()
                    self.SeekWithPathfinding(destx, desty, obj, dummy)
                    return

                if len(lst) == 2:
                    logger.info("路径规划点为2个(起点,终点), 直接过去: (%d, %d)" % (destx, desty))
                    self.Seek(destx, desty, obj, dummy)
                    return
                else:
                    s = ""
                    for v in lst:
                        curpoint = idxToXY(v, self.d.mapw // 10)
                        s += "(%d, %d) " % (curpoint[0], curpoint[1])

                    logger.info("路径规划一共%d 个路程点 %s" % (len(lst), s))
                    self.pathfindinglst = lst
                    self.SeekWithPathfinding(destx, desty, obj, dummy)
                    return

            else:
                logger.info("没有障碍物直接过去 (%d, %d)" % (destx, desty))
                self.Seek(destx, desty, obj, dummy)
                return
        elif len(self.pathfindinglst) == 1:
            del self.pathfindinglst[0]
            logger.info("就一个最终目的规划点了,直接过去 (%d, %d)" % (destx, desty))
            self.Seek(destx, desty, obj, dummy)
            return
        elif len(self.pathfindinglst) >= 2:
            # 路径规划过
            curpoint = idxToXY(self.pathfindinglst[0], self.d.mapw // 10)

            nowcoord = idxToZuobiao(CoordToManIdx(menx, meny, self.d.mapw // 10, self.ob), self.d.mapw // 10)
            nextcoord = idxToZuobiao(self.pathfindinglst[1], self.d.mapw // 10)

            flag = self.ob.CanTwoPointBeMove(nowcoord, nextcoord)
            logger.info("检测 %s -> %s 是否连通 %d" % (nowcoord, nextcoord, flag))

            # 是否直接到达位置
            if not flag:
                if IsClosedTo(menx, meny, curpoint[0], curpoint[1]):
                    flag = True
                    logger.info("直接设置到达位置 (%d, %d) (%d, %d)" % (menx, meny, curpoint[0], curpoint[1]))

            if flag:
                del self.pathfindinglst[0]
                logger.info("到达了规划点 (%d, %d) 剩余 %d" % (destx, desty, len(self.pathfindinglst)))
                return
            else:
                dummy = "" if dummy is None else dummy
                self.Seek(curpoint[0], curpoint[1], obj, dummy=dummy + "(寻路)")
                return

    # 因为到达目的地了清空当前寻路
    def ClearPathfindingLst(self):
        self.pathfindinglst = []

    # 每次进图缓存一下当前的 1. 地形 2. 障碍 3. 门位置.
    def NewMapCache(self):
        t1 = time.time()
        meninfo = GetMenInfo()
        self.d, self.ob = SafeGetDAndOb(meninfo.w, meninfo.h)

        if not IsCurrentInBossFangjian():
            door = GetNextDoorWrap()
            self.doorx, self.doory = GetCorrectDoorXY(self.d.mapw, self.d.maph, door, self.ob)
            logger.info("下一个门的坐标: (%d, %d) ->修正 (%d, %d) " % (door.x, door.y, self.doorx, self.doory))

        self.ClearPathfindingLst()
        t2 = time.time()

        logger.info("获取了地图地形,障碍物数据 共花费: %f", t2 - t1)

    # 切换到新的图
    def CheckInToNewMap(self):
        self.UpLatestKey()
        RanSleep(0.1)
        logger.info("进了新的房间")
        self.NewMapCache()
        self.ChangeState(StandState())


class State:
    def Execute(self, player):
        raise NotImplementedError()


FOR_DUIHUA = 0
FOR_CARTOON = 1
FOR_VIDEO = 2
FOR_CONFIRM = 3


# 什么也不做的状态机. 一般是由于对话,动画或者视频才进入到这里,读取信息供外面恢复
class EmptyState:
    def __init__(self, forwhat):
        self.forwhat = forwhat

    def Execute(self, player):
        pass

    def IsForwhat(self, forwat):
        return self.forwhat == forwat


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
        # 对话处理
        if player.IsEmptyFor(FOR_DUIHUA):
            logger.info("对话状态")
            PressKey(VK_CODE["spacebar"])
            RanSleep(0.2)
            if not IsWindowTop():
                player.RestoreContext()
            return
        # 动画处理
        elif player.IsEmptyFor(FOR_CARTOON):
            logger.info("动画状态")
            PressKey(VK_CODE["esc"])
            RanSleep(0.5)
            if not IsCartoonTop():
                player.RestoreContext()
            return
        # 视频处理
        elif player.IsEmptyFor(FOR_VIDEO):
            logger.info("视频状态")
            PressKey(VK_CODE["esc"])
            RanSleep(0.5)
            if IsConfirmTop():
                confirmPos = GetConfirmPos()
                if confirmPos != (0, 0):
                    logger.info("移动到: %d %d" % (confirmPos[0], confirmPos[1]))
                    MouseMoveTo(confirmPos[0], confirmPos[1])
                    MouseLeftClick()
                    RanSleep(0.2)
            else:
                logger.info("确认按钮没有置顶")
            RanSleep(0.5)
            if not IsVideoTop():
                player.RestoreContext()
            return
        # 确认处理
        elif player.IsEmptyFor(FOR_CONFIRM):
            logger.info("确认状态")
            if IsConfirmTop():
                confirmPos = GetConfirmPos()
                if confirmPos != (0, 0):
                    logger.info("移动到: %d %d" % (confirmPos[0], confirmPos[1]))
                    MouseMoveTo(confirmPos[0], confirmPos[1])
                    MouseLeftClick()
                    RanSleep(0.2)
            else:
                logger.info("确认按钮没有置顶")
            RanSleep(0.5)
            if not IsConfirmTop():
                player.RestoreContext()
            return

        # 对话判断
        if not player.IsEmptyFor(FOR_DUIHUA) and IsWindowTop():
            player.SaveAndChangeToEmpty(FOR_DUIHUA)
        # 动画判断
        elif not player.IsEmptyFor(FOR_CARTOON) and IsCartoonTop():
            player.SaveAndChangeToEmpty(FOR_CARTOON)
            return
        # 视频判断
        elif not player.IsEmptyFor(FOR_VIDEO) and IsVideoTop():
            player.SaveAndChangeToEmpty(FOR_VIDEO)
            return
        # 确认按钮
        elif not player.IsEmptyFor(FOR_CONFIRM) and IsConfirmTop():
            player.SaveAndChangeToEmpty(FOR_CONFIRM)
            return

        # 在图内需要判断卡死的状态
        MapStateList = [SeekAndPickUp, PickBuf, SeekAndAttackMonster, DoorOpenGotoNext, DoorStuckGoToPrev,
                        FuckDuonierState]

        # 防止卡死目前只判断几种情况
        def MapStateCheck(curstate):
            for state in MapStateList:
                if isinstance(curstate, state):
                    return True
            return False

        if MapStateCheck(player.stateMachine.currentState):
            pass
        else:
            self.Reset()
            return

        # 重置坐标
        if self.latesttime is None:
            self.latesttime = time.time()
            self.beginx, self.beginy = GetMenXY()

        # 检查时间过去了
        if time.time() - self.latesttime > 0.5:

            curx, cury = GetMenXY()

            if isinstance(player.stateMachine.currentState, DoorOpenGotoNext):
                # 去下一个门的情况下.坐标判断宽松些
                if WithInRange(curx, cury, self.beginx, self.beginy, 30):
                    self.Reset()
                    # 刷新障碍物
                    logger.warning("进门的时候卡死了, 回退一些再进门")
                    player.NewMapCache()
                    player.ChangeState(DoorStuckGoToPrev())
                else:
                    self.Reset()

            elif math.isclose(curx, self.beginx) and math.isclose(cury, self.beginy):
                self.Reset()
                # 刷新障碍物
                logger.warning("卡死了, 重置状态")
                player.NewMapCache()
                player.ChangeState(StandState())
            else:
                self.Reset()


# 初始化
class Setup(State):
    def Execute(self, player):
        if IsManInMap():
            player.ChangeState(FirstInMap())
            RanSleep(0.2)
            return

        if IsManInChengzhen():
            player.ChangeState(InChengzhen())
            RanSleep(0.2)
            return

        RanSleep(0.2)


# 城镇
class InChengzhen(State):
    def Execute(self, player):
        if IsManInMap():
            player.ChangeState(FirstInMap())
            RanSleep(0.2)
            return

        RanSleep(0.2)


# 副本结束, 尝试退出
class FubenOver(State):
    def Execute(self, player):
        PressKey(VK_CODE["esc"])
        RanSleep(0.2)
        PressKey(VK_CODE["F12"])
        if IsManInChengzhen():
            while IsEscTop():
                PressKey(VK_CODE["esc"])
                RanSleep(0.2)
            player.ChangeState(InChengzhen())
            return


# 测试计数器
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
        if player.skills.HaveBuffCanBeUse():

            if not CanbeMovTest():
                logger.warning("没法移动位置 可能被什么遮挡了, 临时退出状态机")
                time.sleep(0.5)
                return
            RanSleep(0.5)
            if not CanbeMovTest():
                logger.warning("没法移动位置 可能被什么遮挡了, 临时退出状态机")
                time.sleep(0.5)
                return

            skills = player.skills.GetCanBeUseBuffSkills()
            for skill in skills:
                logger.info("使用buff: %s" % skill.name)
                skill.Use()
                player.skills.Update()

        player.skills.Update()

        player.NewMapCache()
        player.ChangeState(StandState())


# 图内站立
class StandState(State):
    def Execute(self, player):
        if IsJiZhouSpecifyState():
            player.ChangeState(FuckDuonierState())
            return
        if HaveMonsters():
            player.ChangeState(SeekAndAttackMonster())
            return
        elif HaveGoods():
            player.ChangeState(SeekAndPickUp())
            return
        elif HaveBuffs():
            player.ChangeState(PickBuf())
            return
        elif not IsCurrentInBossFangjian() and IsNextDoorOpen():
            player.ChangeState(DoorOpenGotoNext())
            return
        elif IsFuBenPass():
            # 打死boss后判断下物品
            RanSleep(0.5)
            if HaveGoods():
                player.ChangeState(SeekAndPickUp())
                return
            else:
                player.ChangeState(FubenOver())
                return
        elif not IsCurrentInBossFangjian() and not IsNextDoorOpen():
            pass
            # 打死怪物后, 门可能不是马上就开, 直接靠近门
            # player.ChangeState(DoorDidnotOpen())
        else:
            if IsCurrentInBossFangjian():
                # 得不到怪物对象. 可能副本结束的瞬间 按esc吧!
                PressKey(VK_CODE["esc"])
                RanSleep(0.1)
                # 把它再点掉,投机取巧
                if IsEscTop():
                    PressKey(VK_CODE["esc"])

        RanSleep(0.3)
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
        if SpecifyMonsterIsToofar(obj) and HaveGoods():
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
                PressHouTiao()
                RanSleep(0.05)
            else:
                player.SeekWithPathfinding(seekx, seeky, dummy="合适攻击位置")
                RanSleep(0.05)
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
        obj = NearestGood()

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
            logger.info("捡取 (%d,%d)" % (obj.x, obj.y))
            RanSleep(0.05)
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
            RanSleep(0.1)
        else:
            player.SeekWithPathfinding(obj.x, obj.y, dummy="捡取buff")


# 门已开,去过图
class DoorOpenGotoNext(State):
    def Execute(self, player):
        # 进到新的地图
        if IsCurrentInBossFangjian():
            player.CheckInToNewMap()
        if not IsNextDoorOpen():
            if IsCurrentInBossFangjian():
                logger.info("进到了boss房间")
            player.CheckInToNewMap()
        else:
            player.SeekWithPathfinding(player.doorx, player.doory, dummy="靠近门")


# 走门时卡死,走到离门远一些的地方
class DoorStuckGoToPrev(State):
    def Execute(self, player):
        menx, meny = GetMenXY()
        door = GetNextDoorWrap()
        if not IsNextDoorOpen():
            if IsCurrentInBossFangjian():
                logger.info("进到了boss房间")
            player.CheckInToNewMap()
        elif IsClosedTo(menx, meny, door.prevcx, door.prevcy):
            player.ChangeState(DoorOpenGotoNext())
        else:
            player.SeekWithPathfinding(door.prevcx, door.prevcy, dummy="靠近门前")



def main():

    InitLog()

    if GameApiInit():
        logger.info("Init helpdll-xxiii.dll ok")
    else:
        logger.info("Init helpdll-xxiii.dll err")
        exit(0)

    if YijianshuInit():
        logger.info("Init 易键鼠 ok")
    else:
        logger.info("Init 易键鼠 err")
        exit(0)

    FlushPid()
    ReleaseAllKey()

    hwnd = win32gui.FindWindow("地下城与勇士", "地下城与勇士")
    # win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 800, 600,
    #                       win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetForegroundWindow(hwnd)

    time.sleep(1.2)

    # 截图线程
    t = threading.Thread(target=FlushImg)
    t.start()

    # 状态机 主线程
    player = Player()
    player.ChangeState(Setup())
    player.SetGlobalState(GlobalState())

    player.skills.Update()

    try:
        while True:
            time.sleep(StateMachineSleep)
            player.Update()
    except KeyboardInterrupt:
        ReleaseAllKey()
        SetThreadExit()
        t.join()
        logger.info("main thread exit")
        sys.exit()


if __name__ == "__main__":
    main()
