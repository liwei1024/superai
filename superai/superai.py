import sys
import os
import time

import win32con
import win32gui
from win32api import Sleep

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import math
import random

from superai.yijianshu import YijianshuInit, DownZUO, DownYOU, DownXIA, DownSHANG, DownZUOSHANG, DownZUOXIA, \
    DownYOUSHANG, DownYOUXIA, UpZUO, UpYOU, UpSHANG, UpXIA, UpZUOSHANG, UpZUOXIA, UpYOUSHANG, UpYOUXIA, PressRight, \
    PressLeft, JiPaoZuo, JiPaoYou, PressAtack, ReleaseAllKey, PressX, PressHouTiao

from superai.gameapi import GameApiInit, FlushPid, PrintMenInfo, PrintMapInfo, PrintSkillObj, PrintNextMen, PrintMapObj, \
    GetMonsters, IsLive, HaveMonsters, NearestMonster, GetMenXY, GetQuadrant, Quardant, \
    GetMenChaoxiang, RIGHT, Skills, UpdateMonsterInfo, LEFT, HaveGoods, \
    NearestGood, IsNextDoorOpen, GetNextDoor, IsCurrentInBossFangjian, GetCurrentMapXy, GetMenInfo, \
    BIG_RENT, CanbePickup, WithInManzou, GetFangxiang, MonsterIsToofar, ATTACK_V_WIDTH, simpleAttackSkill

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

# 多少毫秒执行一次状态机
StateMachineSleep = 20


class StateMachine:
    currentState = None

    owner = None

    globalState = None

    def __init__(self, owner):
        self.owner = owner

    def ChangeState(self, newState):
        tmp = self.currentState
        self.currentState = newState
        print("状态切换 %s -> %s" % (type(tmp), type(self.currentState)))

    def Update(self):
        if self.globalState is not None:
            self.globalState.Execute(self.owner)

        if self.currentState is not None:
            self.currentState.Execute(self.owner)


class Player:
    # 状态机
    stateMachine: StateMachine

    # 上一次按下的键
    latestDown = None

    # 持有技能
    skills = Skills()

    # 是否在疾跑状态
    injipao = False

    # 当前选择的技能 (保存临时选择的状态,释放完毕才能选择下一个技能)
    curskill = None

    def __init__(self):
        self.stateMachine = StateMachine(self)

    def ChangeState(self, state):
        self.UpLatestKey()
        self.stateMachine.ChangeState(state)

    def SetGlobalState(self, state):
        self.stateMachine.globalState = state

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
        if random.uniform(0, 1) < 0.3:
            self.curskill = simpleAttackSkill
        else:
            self.curskill = self.skills.GetMaxLevelAttackSkill()
            if self.curskill is None:
                self.curskill = simpleAttackSkill

    # 使用掉随机选择的技能
    def UseSkill(self):
        self.curskill.Use()
        self.skills.Update()
        print("使用技能 %s" % self.curskill.name)
        self.curskill = None

    # 是否已经选择了技能
    def HasSkillHasBeenSelect(self):
        return self.curskill is not None

    def ChaoxiangFangxiang(self, menx, objx):
        # 是否面向对方
        monlocation = GetFangxiang(menx, objx)
        menfangxiang = GetMenChaoxiang()

        if monlocation != menfangxiang:
            # 调整朝向
            if menfangxiang == RIGHT and monlocation == LEFT:
                print("调整朝向 人物: %d 怪物: %d, 向左调整" % (menfangxiang, monlocation))
                PressLeft()
            else:
                print("调整朝向 人物: %d 怪物: %d, 向右调整" % (menfangxiang, monlocation))
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

    # 疾跑斜方向象限移动到水平或垂直位置时. 保留一个方向的速度. 并按键弹起释放另一个方向的速度
    def SwitchFangxiang(self, quad) -> bool:
        if not self.KeyDowned():
            return False

        if self.latestDown == quad:
            raise NotImplementedError()

        # 左上 -> 左 弹起上
        # 左上 -> 上 弹起左

        # 左 -> 左上 不处理
        # 左 -> 左下 不处理
        # ...

        if self.latestDown == Quardant.ZUO:
            if quad == Quardant.ZUOSHANG:
                DownZUOSHANG()
                self.latestDown = Quardant.ZUOSHANG
            elif quad == Quardant.ZUOXIA:
                DownZUOXIA()
                self.latestDown = Quardant.ZUOXIA
            else:
                return False

        if self.latestDown == Quardant.YOU:
            if quad == Quardant.YOUSHANG:
                DownYOUSHANG()
                self.latestDown = Quardant.YOUSHANG
            elif quad == Quardant.YOUXIA:
                DownYOUXIA()
                self.latestDown = Quardant.YOUXIA
            else:
                return False

        if self.latestDown == Quardant.ZUOSHANG:
            if quad == Quardant.ZUO:
                UpSHANG()
                self.latestDown = Quardant.ZUO
            elif quad == Quardant.SHANG:
                UpZUO()
                self.latestDown = Quardant.SHANG
            else:
                return False

        if self.latestDown == Quardant.YOUSHANG:
            if quad == Quardant.YOU:
                UpSHANG()
                self.latestDown = Quardant.YOU
            elif quad == Quardant.SHANG:
                UpYOU()
                self.latestDown = Quardant.SHANG
            else:
                return False

        if self.latestDown == Quardant.ZUOXIA:
            if quad == Quardant.ZUO:
                UpXIA()
                self.latestDown = Quardant.ZUO
            elif quad == Quardant.XIA:
                UpZUO()
                self.latestDown = Quardant.XIA
            else:
                return False

        if self.latestDown == Quardant.YOUXIA:
            if quad == Quardant.YOU:
                UpXIA()
                self.latestDown = Quardant.YOU
            elif quad == Quardant.XIA:
                UpYOU()
                self.latestDown = Quardant.XIA
            else:
                return False

        return True

    # 靠近
    def Seek(self, destx, desty):
        menx, meny = GetMenXY()
        quad, rent = GetQuadrant(menx, meny, destx, desty)

        if quad == Quardant.CHONGDIE:
            # 已经重叠了, 调用者(靠近怪物, 捡物, 过门 应该不会再次调用seek了). 频繁发生就说明写错了
            self.UpLatestKey()
            print("seek: 本人(%.f, %.f) 目标(%.f, %.f)在%s, 重叠" % (menx, meny, destx, desty, quad.name))
            return

        jizou = not WithInManzou(menx, meny, destx, desty)
        jizoustr = "" if not jizou else "疾走"

        if rent == BIG_RENT:
            if self.KeyDowned():
                if self.latestDown == quad:
                    self.DownKey(quad)
                    # print("seek: 本人(%.f, %.f) 目标(%.f, %.f)在%s, 维持 %s" %
                    # (menx, meny, destx, desty, quad.name, jizoustr))

                elif self.SwitchFangxiang(quad):
                    pass
                    # print("seek: 本人(%.f, %.f) 目标(%.f, %.f)在%s, 维持 %s" %
                    # (menx, meny, destx, desty, quad.name, jizoustr))
                else:
                    print(
                        "seek: 本人(%.f, %.f) 目标(%.f, %.f)在%s, 更换方向 %s" % (menx, meny, destx, desty, quad.name, jizoustr))
                    self.UpLatestKey()
                    if jizou:
                        self.KeyJiPao(quad)
                    self.DownKey(quad)

            else:
                self.UpLatestKey()
                print("seek: 本人(%.f, %.f) 目标(%.f, %.f)在%s, 首次靠近 %s" % (menx, meny, destx, desty, quad.name, jizoustr))
                if jizou:
                    self.KeyJiPao(quad)
                self.DownKey(quad)
        else:
            self.UpLatestKey()
            print("seek: 本人(%.f, %.f) 目标(%.f, %.f)在%s, 微小距离靠近" % (menx, meny, destx, desty, quad.name))
            QuadKeyDownMap[quad]()
            time.sleep(0.2)
            ReleaseAllKey()


class State:
    def Execute(self, player):
        raise NotImplementedError()


# 防卡死状态机
class StuckGlobalState(State):
    counter = 0
    beginx = None
    beginy = None

    def Reset(self):
        self.counter = 0
        self.beginx = None
        self.beginy = None

    def Execute(self, player):

        if isinstance(player.stateMachine.currentState, SeekAndPickUp) or \
                isinstance(player.stateMachine.currentState, DoorOpenGotoNext) or \
                isinstance(player.stateMachine.currentState, SeekAndAttackMonster):
            self.counter += 1

        if isinstance(player.stateMachine.currentState, StandState):
            self.Reset()

        # 重置坐标
        if self.counter == 1:
            self.beginx, self.beginy = GetMenXY()

        # 1s过去了
        if self.counter >= 1000 / StateMachineSleep:
            curx, cury = GetMenXY()
            if math.isclose(curx, self.beginx) and math.isclose(cury, self.beginy):
                self.Reset()
                player.ChangeState(StandState())
                print("卡死了, 重置状态")
            else:
                self.Reset()


# 初次进图,加buff
class FirstInMap(State):
    def Execute(self, player):
        if player.skills.HaveBuffCanBeUse():
            skills = player.skills.GetCanBeUseBuffSkills()
            for skill in skills:
                # 没有用过才释放
                # if not player.skills.DidSkillHavebeenUsed(skill.name):
                time.sleep(0.1)
                skill.Use()
                player.skills.Update()
                time.sleep(0.1)
                #
                #     # 按键了 没有释放出来. 再次释放..
                #     time.sleep(0.3)
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
        elif (not IsCurrentInBossFangjian()) and IsNextDoorOpen():
            player.ChangeState(DoorOpenGotoNext())
            return

        time.sleep(0.3)
        print("state can not switch")


# 靠近并攻击怪物
class SeekAndAttackMonster(State):

    def Execute(self, player):
        obj = NearestMonster()

        # 如果没有怪物了,那么切换状态
        if obj is None:
            player.ChangeState(StandState())
            return

        # 怪物血量太少, 重新进入 Execute 选择怪物
        if obj.hp < 1:
            return

        # 怪物在太远的距离, 有物品捡物
        if MonsterIsToofar() and HaveGoods():
            player.ChangeState(SeekAndPickUp())
            return

        # 没有选择技能就选择一个
        if not player.HasSkillHasBeenSelect():
            player.SelectSkill()

        men = GetMenInfo()

        # 在水平宽度内并且垂直宽度太近了, 远离
        if player.curskill.IsH_WInRange(men.y, obj.y) and \
                player.curskill.IsV_WTOOClose(men.x, obj.x):
            seekx, seeky = player.curskill.GetSeekXY(men.x, men.y, obj.x, obj.y)
            print("目标太接近,无法攻击,选择合适位置: men:(%d,%d) obj:(%d,%d) seek(%d,%d), 技能%s 太靠近垂直水平(%d,%d)" %
                  (men.x, men.y, obj.x, obj.y, seekx, seeky, player.curskill.name,
                   player.curskill.skilldata.too_close_v_w, player.curskill.skilldata.h_w))

            # 后跳解决问题
            player.UpLatestKey()
            if random.uniform(0, 1) < 0.8:
                PressHouTiao()
                time.sleep(0.2)
            else:
                player.Seek(seekx, seeky)
                time.sleep(0.1)
            return

        # 在攻击的水平宽度和垂直宽度之内,攻击
        if player.curskill.IsH_WInRange(men.y, obj.y) and \
                player.curskill.isV_WInRange(men.x, obj.x):
            print("目标在技能:%s 的攻击范围之内, 垂直水平: (%d,%d)" %
                  (player.curskill.name, player.curskill.skilldata.v_w, player.curskill.skilldata.h_w))
            player.UpLatestKey()
            player.ChaoxiangFangxiang(men.x, obj.x)
            player.UseSkill()
            return

        # 靠近
        seekx, seeky = player.curskill.GetSeekXY(men.x, men.y, obj.x, obj.y)
        player.Seek(seekx, seeky)


# 靠近并捡取物品
class SeekAndPickUp(State):
    def Execute(self, player):
        obj = NearestGood()

        # 如果没有物品了,那么切换图内状态
        if obj is None:
            player.ChangeState(StandState())
            return

        # 有怪物在范围内,紧急切换
        if not MonsterIsToofar():
            player.ChangeState(SeekAndAttackMonster())
            return

        menx, meny = GetMenXY()
        if CanbePickup(menx, meny, obj.x, obj.y):
            # 上一次的跑动的按键恢复
            player.UpLatestKey()
            print("捡取 (%d,%d)" % (obj.x, obj.y))
            time.sleep(0.1)
            PressX()
            time.sleep(0.3)
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
            return
        else:
            player.Seek(door.x, door.y)


def main():
    if GameApiInit():
        print("Init helpdll-xxiii.dll ok")
    else:
        print("Init helpdll-xxiii.dll err")
        exit(0)

    if YijianshuInit():
        print("Init 易键鼠 ok")
    else:
        print("Init 易键鼠 err")
        exit(0)

    FlushPid()
    ReleaseAllKey()

    hwnd = win32gui.FindWindow("地下城与勇士", "地下城与勇士")
    # win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 800, 600,
    #                       win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetForegroundWindow(hwnd)

    time.sleep(1.2)

    player = Player()
    player.ChangeState(FirstInMap())
    player.SetGlobalState(StuckGlobalState())

    player.skills.Update()
    player.skills.FlushAllTime()

    try:
        while True:
            Sleep(StateMachineSleep)
            player.Update()
    except KeyboardInterrupt:
        player.UpLatestKey()
        sys.exit()


if __name__ == "__main__":
    main()
