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
    PressLeft, JiPaoZuo, JiPaoYou, PressAtack, ReleaseAllKey, PressX

from superai.gameapi import GameApiInit, FlushPid, PrintMenInfo, PrintMapInfo, PrintSkillObj, PrintNextMen, PrintMapObj, \
    GetMonsters, IsLive, HaveMonsters, NearestMonster, GetMenXY, GetQuadrant, Quardant, \
    GetMenChaoxiang, RIGHT, Skills, UpdateMonsterInfo, LEFT, HaveGoods, \
    NearestGood, IsNextDoorOpen, GetNextDoor, IsCurrentInBossFangjian, GetCurrentMapXy, GetMenInfo, \
    BIG_RENT, CanbePickup, WithInManzou, GetFangxiang, CanBeAttack, MonsterIsToofar, ATTACK_V_WIDTH

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

    injipao = False

    def __init__(self):
        self.stateMachine = StateMachine(self)

    def ChangeState(self, state):
        self.stateMachine.ChangeState(state)

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

    def Kasi(self):
        pass

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

    def ChaoxiangFangxiang(self, menx, objx):
        # 是否面向对方

        guaiwuweizhi = GetFangxiang(menx, objx)
        renwufangxiang = GetMenChaoxiang()

        if guaiwuweizhi != renwufangxiang:
            # 调整朝向
            if renwufangxiang == RIGHT and guaiwuweizhi == LEFT:
                print("调整朝向 人物: %d 怪物: %d, 向左调整" % (renwufangxiang, guaiwuweizhi))
                PressLeft()
            else:
                print("调整朝向 人物: %d 怪物: %d, 向右调整" % (renwufangxiang, guaiwuweizhi))
                PressRight()

    # 靠近
    def Seek(self, destx, desty):
        menx, meny = GetMenXY()
        quad, rent = GetQuadrant(menx, meny, destx, desty)

        if quad == Quardant.CHONGDIE:
            self.UpLatestKey()
            print("seek: 本人(%.f, %.f) 目标(%.f, %.f)在%s, 重叠" % (menx, meny, destx, desty, quad.name))
            return

        jizou = not WithInManzou(menx, meny, destx, desty)

        jizoustr = ""
        if jizou:
            jizoustr = "疾走"

        if rent == BIG_RENT:
            if self.KeyDowned():
                if self.latestDown == quad:
                    self.DownKey(quad)
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


# 初次进图,加buff
class FirstInMap(State):
    def Execute(self, player):
        if player.skills.HaveBuffCanBeUse():
            skills = player.skills.GetCanBeUseBuffSkills()
            for skill in skills:
                skill.Use()
                player.skills.Update()

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

        men = GetMenInfo()

        # TODO. 靠近怪物攻击范围 1. 普通攻击状态  2. 技能释放状态

        if CanBeAttack(men.x, men.y, obj.x, obj.y):
            # 上一次的跑动的按键恢复
            player.UpLatestKey()

            # 朝向更新
            player.ChaoxiangFangxiang(men.x, obj.x)
            print("SeekAndAttackMonster: 开始攻击 %.f, %.f" % (obj.x, obj.y))

            # TODO. 微小调整

            if random.uniform(0, 1) < 0.3:
                time.sleep(0.1)
                PressAtack()
            else:
                skill = player.skills.GetMaxLevelAttackSkill()
                if skill is not None:
                    # TODO. 1. 在范围内,攻击 2. 范围太近,远离 3. 范围太远靠近

                    print("使用技能 %s" % skill.name)
                    skill.Use()
                    player.skills.Update()

        else:
            if GetFangxiang(men.x, obj.x) == RIGHT:
                player.Seek(obj.x, obj.y)
            else:
                player.Seek(obj.x, obj.y)


# 靠近并捡取物品
class SeekAndPickUp(State):
    def Execute(self, player):
        obj = NearestGood()

        # 如果没有物品了,那么切换状态
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
            player.UpLatestKey()
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

    time.sleep(0.8)

    player = Player()
    player.ChangeState(FirstInMap())

    player.skills.Update()
    player.skills.FlushAllTime()

    try:
        while True:
            Sleep(30)
            player.Update()
    except KeyboardInterrupt:
        player.UpLatestKey()
        sys.exit()


if __name__ == "__main__":
    main()
