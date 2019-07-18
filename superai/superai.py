import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import win32gui
import math
import random
import time

from superai.vkcode import VK_CODE

from superai.common import Log

from superai.yijianshu import YijianshuInit, DownZUO, DownYOU, DownXIA, DownSHANG, DownZUOSHANG, DownZUOXIA, \
    DownYOUSHANG, DownYOUXIA, PressRight, \
    PressLeft, JiPaoZuo, JiPaoYou, ReleaseAllKey, PressX, PressHouTiao, RanSleep, UpZUO, UpYOU, UpSHANG, \
    UpXIA, UpZUOSHANG, UpZUOXIA, UpYOUSHANG, UpYOUXIA, PressKey

from superai.gameapi import GameApiInit, FlushPid, \
    HaveMonsters, NearestMonster, GetMenXY, GetQuadrant, Quardant, \
    GetMenChaoxiang, RIGHT, Skills, LEFT, HaveGoods, \
    NearestGood, IsNextDoorOpen, GetNextDoor, IsCurrentInBossFangjian, GetMenInfo, \
    BIG_RENT, CanbePickup, WithInManzou, GetFangxiang, ClosestMonsterIsToofar, simpleAttackSkill, GetBossObj, \
    IsClosedTo, \
    NearestBuf, HaveBuffs, CanbeGetBuff, GetMapInfo, SpecifyMonsterIsToofar, IsManInSelectMap, XUANTU, TUNEI, \
    IsManInMap, IsManInChengzhen, QuardantMap, IsManJipao, NearestMonsterWrap, IsWindowTop, IsEscTop

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
        Log("状态切换 %s -> %s" % (type(tmp), type(self.currentState)))

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

        # 是否在疾跑状态
        self.injipao = False

        # 当前选择的技能 (保存临时选择的状态,释放完毕才能选择下一个技能)
        self.curskill = None

        # 状态机
        self.stateMachine = StateMachine(self)

    # 更改当前状态机
    def ChangeState(self, state):
        self.UpLatestKey()
        self.stateMachine.ChangeState(state)

    # 更改全局状态机
    def SetGlobalState(self, state):
        self.stateMachine.globalState = state

    # 更改之前的状态机
    def SetLatestState(self, state):
        self.stateMachine.latestState = state

    # 保存当前状态,并且切换到什么也不做的状态机
    def SaveCurrentContext(self):
        if isinstance(self.stateMachine.currentState, EmptyState):
            return

        Log("状态保存 currentState: %s" % type(self.stateMachine.currentState))
        self.SetLatestState(self.stateMachine.currentState)
        self.ChangeState(EmptyState())

    # 恢复状态机
    def RestoreContext(self):
        if isinstance(self.stateMachine.currentState, EmptyState):
            Log("状态恢复 latestState: %s" % type(self.stateMachine.latestState))
            self.ChangeState(self.stateMachine.latestState)
            self.SetLatestState(None)

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
        if self.KeyDowned():
            # QuadKeyUpMap[self.latestDown]()
            ReleaseAllKey()
            self.ResetKey()
            # 疾跑 -> 八方位移动.  恢复站立状态 -> 疾跑状态关闭
            self.injipao = False

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
        monlocation = GetFangxiang(menx, objx)
        menfangxiang = GetMenChaoxiang()
        if monlocation != menfangxiang:
            return False
        return True

    # 朝向对方
    def ChaoxiangFangxiang(self, menx, objx):
        while not self.IsChaoxiangDuifang(menx, objx):
            monlocation = GetFangxiang(menx, objx)
            menfangxiang = GetMenChaoxiang()

            # 调整朝向
            if menfangxiang == RIGHT and monlocation == LEFT:
                # Log("调整朝向 人物: %d 怪物: %d, 向左调整" % (menfangxiang, monlocation))
                PressLeft()
            else:
                # Log("调整朝向 人物: %d 怪物: %d, 向右调整" % (menfangxiang, monlocation))
                PressRight()

    # 疾跑
    def KeyJiPao(self, quad):
        if self.injipao:
            return
        if quad in [Quardant.SHANG, Quardant.XIA]:
            return
        elif quad in [Quardant.ZUO, Quardant.ZUOSHANG, Quardant.ZUOXIA]:
            JiPaoZuo()
        elif quad in [Quardant.YOU, Quardant.YOUSHANG, Quardant.YOUXIA]:
            JiPaoYou()
        else:
            raise NotImplementedError()
        self.injipao = True

    # 靠近
    def Seek(self, destx, desty, obj=None):
        menx, meny = GetMenXY()
        quad, rent = GetQuadrant(menx, meny, destx, desty)

        if quad == Quardant.CHONGDIE:
            # 已经重叠了, 调用者(靠近怪物, 捡物, 过门 应该不会再次调用seek了). 频繁发生就说明写错了
            self.UpLatestKey()
            # Log("seek: 本人(%.f, %.f) 目标(%.f, %.f)在%s, 重叠" % (menx, meny, destx, desty, quad.name))
            return

        objname = "name:%s obj:0x%X hp:%d " % (obj.name, obj.object, obj.hp) if obj is not None else ""
        jizou = not WithInManzou(menx, meny, destx, desty)
        jizoustr = "" if not jizou else "疾走"

        # 大范围移动
        if rent == BIG_RENT:
            # 之前按过键
            if self.KeyDowned():
                # 方向相同
                if self.latestDown == quad:
                    if jizou and not IsManJipao():
                        self.UpLatestKey()
                        return

                    self.DownKey(quad)
                    RanSleep(0.05)
                    Log("seek: 本人(%.f, %.f) 目标(%.f, %.f)在%s, 方向完全相同 %s" %
                        (menx, meny, destx, desty, quad.name, jizoustr))

                # 和人物朝向不同
                elif not self.IsChaoxiangDuifang(menx, destx):
                    Log(
                        "seek: 本人(%.f, %.f) 目标%s (%.f, %.f)在%s, 朝向不同,重新移动 %s" % (
                            menx, meny, objname, destx, desty, quad.name, jizoustr))
                    self.UpLatestKey()
                    if jizou:
                        self.KeyJiPao(quad)
                    self.DownKey(quad)
                    RanSleep(0.025)

                # 方向类似
                else:
                    if jizou and not IsManJipao():
                        self.UpLatestKey()
                        return

                    # 上次和本次按键的分解
                    latestDecompose = QuardantMap[self.latestDown]
                    currentDecompose = QuardantMap[quad]

                    # 上次的按键在本次方向中没找到就弹起
                    for keydown in latestDecompose:
                        if keydown not in currentDecompose:
                            QuadKeyUpMap[keydown]()
                    self.DownKey(quad)
                    Log(
                        "seek: 本人(%.f, %.f) 目标%s (%.f, %.f)在%s, 保持部分移动方向 %s" % (
                            menx, meny, objname, destx, desty, quad.name, jizoustr))
            # 没有按过键
            else:
                self.UpLatestKey()
                Log("seek: 本人(%.f, %.f) 目标%s(%.f, %.f)在%s, 首次靠近 %s" % (
                    menx, meny, objname, destx, desty, quad.name, jizoustr))
                if jizou:
                    self.KeyJiPao(quad)
                self.DownKey(quad)
        # 小范围移动
        else:
            self.UpLatestKey()
            Log("seek: 本人(%.f, %.f) 目标%s(%.f, %.f)在%s, 微小距离靠近" %
                (menx, meny, objname, destx, desty, quad.name))
            self.DownKey(quad)
            RanSleep(0.05)
            self.UpLatestKey()


class State:
    def Execute(self, player):
        raise NotImplementedError()


class EmptyState:
    def Execute(self, player):
        pass


# 防卡死状态机
class StuckGlobalState(State):

    def __init__(self):
        self.beginx = None
        self.beginy = None
        self.latesttime = None

    def Reset(self):
        self.beginx = None
        self.beginy = None
        self.latesttime = None

    def Execute(self, player):
        if IsWindowTop():
            # 保留当前状态
            player.SaveCurrentContext()
            PressKey(VK_CODE["spacebar"])
            RanSleep(0.2)
            return
        else:
            # 恢复之前的状态
            player.RestoreContext()
            pass

        # 目前只判断几种情况
        if isinstance(player.stateMachine.currentState, SeekAndPickUp) or \
                isinstance(player.stateMachine.currentState, PickBuf) or \
                isinstance(player.stateMachine.currentState, SeekAndAttackMonster) or \
                isinstance(player.stateMachine.currentState, DoorOpenGotoNext) or \
                isinstance(player.stateMachine.currentState, DoorStuckGoToPrev):
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
            if math.isclose(curx, self.beginx) and math.isclose(cury, self.beginy):
                if isinstance(player.stateMachine.currentState, DoorOpenGotoNext):
                    self.Reset()
                    player.ChangeState(DoorStuckGoToPrev())
                    Log("进门的时候卡死了, 回退一些再进门")
                else:
                    self.Reset()
                    player.ChangeState(StandState())
                    Log("卡死了, 重置状态")
            else:
                self.Reset()


# 初始化
class Setup(State):
    def Execute(self, player):
        if IsManInMap():
            player.ChangeState(FirstInMap())
            RanSleep(0.5)
            return

        if IsManInChengzhen():
            player.ChangeState(InChengzhen())
            RanSleep(0.5)
            return

        RanSleep(0.5)


# 城镇
class InChengzhen(State):
    def Execute(self, player):
        if IsManInMap():
            player.ChangeState(FirstInMap())
            RanSleep(0.5)
            return

        RanSleep(0.5)


# 副本结束, 尝试退出
class FubenOver(State):
    def Execute(self, player):
        PressKey(VK_CODE["esc"])
        RanSleep(0.5)
        PressKey(VK_CODE["F12"])
        if IsManInChengzhen():
            RanSleep(1.0)

            while IsEscTop():
                PressKey(VK_CODE["esc"])
                RanSleep(0.5)

            player.ChangeState(InChengzhen())

        # if IsManInMap() and not IsCurrentInBossFangjian():
        #     player.ChangeState(FirstInMap())
        #     RanSleep(0.5)
        #     return

        RanSleep(0.5)


# 初次进图,加buff
class FirstInMap(State):
    def Execute(self, player):
        if player.skills.HaveBuffCanBeUse():
            skills = player.skills.GetCanBeUseBuffSkills()
            for skill in skills:
                # 没有用过才释放
                # if not player.skills.DidSkillHavebeenUsed(skill.name):

                Log("使用buff: %s" % skill.name)
                skill.Use()
                player.skills.Update()
                #
                #     # 按键了 没有释放出来. 再次释放..
                #     RanSleep(0.3)
                #     if not player.skills.DidSkillHavebeenUsed(skill.name):
                #         return

        player.ChangeState(StandState())


# 图内站立
class StandState(State):
    def Execute(self, player):
        if HaveMonsters():
            player.ChangeState(SeekAndAttackMonster())
            return
        elif HaveGoods():
            player.ChangeState(SeekAndPickUp())
            return
        elif HaveBuffs():
            player.ChangeState(PickBuf())
            return
        elif (not IsCurrentInBossFangjian()) and IsNextDoorOpen():
            player.ChangeState(DoorOpenGotoNext())
            return
        elif IsCurrentInBossFangjian() and IsNextDoorOpen():

            # 打死boss后判断下物品
            RanSleep(2.0)
            if HaveGoods():
                player.ChangeState(SeekAndPickUp())
                return
            else:
                player.ChangeState(FubenOver())
                return

        RanSleep(0.3)
        Log("state can not switch")


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

        # Log("选择了 %s (%.f, %.f)" % ( obj.name, obj.x, obj.y))

        # 没有选择技能就选择一个
        if not player.HasSkillHasBeenSelect():
            player.SelectSkill()

        men = GetMenInfo()

        # 在水平宽度内并且垂直宽度太近了, 远离
        if player.curskill.IsH_WInRange(men.y, obj.y) and \
                player.curskill.IsV_WTOOClose(men.x, obj.x):
            seekx, seeky = player.curskill.GetSeekXY(men.x, men.y, obj.x, obj.y)
            Log("目标太接近,无法攻击,选择合适位置: men:(%d,%d) obj:(%d,%d) seek(%d,%d), 技能%s 太靠近垂直水平(%d,%d)" %
                (men.x, men.y, obj.x, obj.y, seekx, seeky, player.curskill.name,
                 player.curskill.skilldata.too_close_v_w, player.curskill.skilldata.h_w))

            # 后跳解决问题
            player.UpLatestKey()
            if random.uniform(0, 1) < 0.8:
                PressHouTiao()
                RanSleep(0.05)
            else:
                player.Seek(seekx, seeky)
                RanSleep(0.05)
            return

        # 在攻击的水平宽度和垂直宽度之内,攻击
        if player.curskill.IsH_WInRange(men.y, obj.y) and \
                player.curskill.isV_WInRange(men.x, obj.x):
            Log("目标在技能:%s 的攻击范围之内, 垂直水平: (%d,%d)" %
                (player.curskill.name, player.curskill.skilldata.v_w, player.curskill.skilldata.h_w))
            player.UpLatestKey()
            player.ChaoxiangFangxiang(men.x, obj.x)
            player.UseSkill()
            return

        # 靠近
        seekx, seeky = player.curskill.GetSeekXY(men.x, men.y, obj.x, obj.y)
        player.Seek(seekx, seeky, obj)


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
            Log("捡取 (%d,%d)" % (obj.x, obj.y))
            RanSleep(0.05)
            PressX()
        else:
            player.Seek(obj.x, obj.y)


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
            Log("捡取buff (%d,%d)" % (obj.x, obj.y))
            RanSleep(0.1)
        else:
            player.Seek(obj.x, obj.y)


# 门已开,去过图
class DoorOpenGotoNext(State):
    def Execute(self, player):
        # 进到新的地图
        door = GetNextDoor()
        if not IsNextDoorOpen():
            # 进入到了新的门
            player.ChangeState(StandState())
        else:
            player.Seek(door.secondcx, door.secondcy)


# 走门时卡死,走到离门远一些的地方
class DoorStuckGoToPrev(State):
    def Execute(self, player):
        menx, meny = GetMenXY()
        door = GetNextDoor()
        if not IsNextDoorOpen():
            player.ChangeState(StandState())
        elif IsClosedTo(menx, meny, door.prevcx, door.prevcy):
            player.ChangeState(DoorOpenGotoNext())
        else:
            player.Seek(door.prevcx, door.prevcy)


def main():
    if GameApiInit():
        Log("Init helpdll-xxiii.dll ok")
    else:
        Log("Init helpdll-xxiii.dll err")
        exit(0)

    if YijianshuInit():
        Log("Init 易键鼠 ok")
    else:
        Log("Init 易键鼠 err")
        exit(0)

    FlushPid()
    ReleaseAllKey()

    hwnd = win32gui.FindWindow("地下城与勇士", "地下城与勇士")
    # win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 800, 600,
    #                       win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetForegroundWindow(hwnd)

    time.sleep(1.2)

    player = Player()
    player.ChangeState(Setup())
    player.SetGlobalState(StuckGlobalState())

    player.skills.Update()
    player.skills.FlushAllTime()

    try:
        while True:
            time.sleep(StateMachineSleep)
            player.Update()
    except KeyboardInterrupt:
        player.UpLatestKey()
        sys.exit()


if __name__ == "__main__":
    main()
