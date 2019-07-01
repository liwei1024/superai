import sys
import os
import time

import win32con
import win32gui
from win32api import Sleep

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import math

from superai.yijianshu import YijianshuInit, DownZUO, DownYOU, DownXIA, DownSHANG, DownZUOSHANG, DownZUOXIA, \
    DownYOUSHANG, DownYOUXIA, UpZUO, UpYOU, UpSHANG, UpXIA, UpZUOSHANG, UpZUOXIA, UpYOUSHANG, UpYOUXIA, PressRight, \
    PressLeft, JiPaoZuo, JiPaoYou, PressAtack, ReleaseAllKey, PressX

from superai.gameapi import GameApiInit, FlushPid, PrintMenInfo, PrintMapInfo, PrintSkillObj, PrintNextMen, PrintMapObj, \
    GetMonsters, IsLive, HaveMonsters, NearestMonster, GetMenXY, GetQuadrant, Quardant, IsClosed, GetFangxiang, \
    GetMenChaoxiang, RIGHT, WithInDistance, WithInDistanceExtra, Skills, UpdateMonsterInfo, LEFT, HaveGoods, \
    NearestGood, IsInEqualLocation, IsNextDoorOpen, GetNextDoor, IsCurrentInBossFangjian, GetCurrentMapXy

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


class StateMachine:
    currentState = None

    owner = None

    def __init__(self, owner):
        self.owner = owner

    def ChangeState(self, newState):
        tmp = self.currentState
        self.currentState = newState
        print("状态切换 %s -> %s" % (type(tmp), type(self.currentState)))

    def Update(self):
        if self.currentState is not None:
            self.currentState.Execute(self.owner)


class Player:
    # 状态机
    stateMachine: StateMachine

    # 上一次按下的键
    latestDown = None

    # 正在疾跑
    injipao = False

    # 持有技能
    skills = Skills()

    def __init__(self):
        self.stateMachine = StateMachine(self)

    def ChangeState(self, state):
        self.stateMachine.ChangeState(state)

    def Update(self):
        self.stateMachine.Update()

    # 靠近到攻击范围内
    def Seek(self, objx, objy):
        menx, meny = GetMenXY()

        # 是否在范围内
        if IsClosed(menx, meny, objx, objy):
            print("seek: 目标(%.f, %.f)在范围内" % (objx, objy))

            # 上一次的按键恢复
            self.UpLatestKey()
            self.ChaoxiangFangxiang(menx, objx)

        else:
            quad = GetQuadrant(menx, meny, objx, objy)

            withined, dis, kuandu, changdu = WithInDistanceExtra(menx, meny, objx, objy)
            jipao = not withined

            print("seek: 目标: %s 在慢走范围内: %d 疾跑: %d 距离: %d 宽度: %d 长度: %d" %
                  (quad.name, withined, jipao, dis, kuandu, changdu))

            if self.KeyDowned():
                if self.latestDown == quad:
                    print("seek: 目标(%.f, %.f)在%s, 维持" % (objx, objy, quad.name))
                    self.DownKey(quad)
                else:
                    print("seek: 目标(%.f, %.f)在%s, 更换方向" % (objx, objy, quad.name))
                    self.UpLatestKey()

                    if jipao:
                        self.KeyJiPao(quad)
                    self.DownKey(quad)
            else:
                print("seek: 目标(%.f, %.f)在%s, 首次靠近" % (objx, objy, quad.name))

                if jipao:
                    self.KeyJiPao(quad)
                self.DownKey(quad)

    # 靠近到具体位置
    def Seek2(self, objx, objy):
        menx, meny = GetMenXY()

        # 是否处于相同位置
        if IsInEqualLocation(menx, meny, objx, objy):
            # 上一次的按键恢复
            self.UpLatestKey()

            print("seek: 目标(%.f, %.f)在范围内" % (objx, objy))

            self.ChaoxiangFangxiang(menx, objx)

        else:
            quad = GetQuadrant(menx, meny, objx, objy)

            withined, dis, kuandu, changdu = WithInDistanceExtra(menx, meny, objx, objy)
            jipao = not withined

            print("seek: 目标: %s 在慢走范围内: %d 疾跑: %d 距离: %d 宽度: %d 长度: %d" %
                  (quad.name, withined, jipao, dis, kuandu, changdu))

            if self.KeyDowned():
                if self.latestDown == quad:
                    print("seek: 目标(%.f, %.f)在%s, 维持" % (objx, objy, quad.name))
                    self.DownKey(quad)
                else:
                    print("seek: 目标(%.f, %.f)在%s, 更换方向" % (objx, objy, quad.name))
                    self.UpLatestKey()

                    if jipao:
                        self.KeyJiPao(quad)
                    self.DownKey(quad)
            else:
                print("seek: 目标(%.f, %.f)在%s, 首次靠近" % (objx, objy, quad.name))

                if jipao:
                    self.KeyJiPao(quad)
                self.DownKey(quad)

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

    # 开启疾跑状态
    def KeyJiPao(self, quad):
        if self.injipao:
            return
        if quad in [Quardant.ZUO, Quardant.ZUOSHANG, Quardant.ZUOXIA, Quardant.SHANG, Quardant.XIA]:
            JiPaoZuo()

        if quad in [Quardant.YOU, Quardant.YOUSHANG, Quardant.YOUXIA]:
            JiPaoYou()

        self.injipao = True

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
            QuadKeyUpMap[self.latestDown]()

            ReleaseAllKey()
            self.ResetKey()
            # 疾跑 -> 八方位移动.  恢复站立状态 -> 疾跑状态关闭
            self.injipao = False


class State:
    def Execute(self, player):
        raise NotImplementedError()


# 图内站立
class StandState(State):
    def Execute(self, player):
        if HaveMonsters():
            player.ChangeState(SeekAndAttackMonsterInstance)
        elif HaveGoods():
            player.ChangeState(SeekAndPickUpInstance)
        elif (not IsCurrentInBossFangjian()) and IsNextDoorOpen():
            player.ChangeState(DoorOpenGotoNextInstance)
        else:
            print("state can not switch")


# 靠近并攻击怪物
class SeekAndAttackMonster(State):
    # selectedMonster = None

    def Execute(self, player):

        # # 更新选中怪物信息
        # if self.selectedMonster is not None:
        #     self.selectedMonster = UpdateMonsterInfo(self.selectedMonster)
        #
        # # 如果选中的怪物死亡了, 或者没有选中怪物
        # if self.selectedMonster is None:
        #     obj = NearestMonster()
        #     self.selectedMonster = obj
        # else:
        #     obj = self.selectedMonster

        obj = NearestMonster()

        # 如果没有怪物了,那么切换状态
        if obj is None:
            player.ChangeState(StandStateInstance)
            return

        if obj.hp < 1:
            return

        objx, objy = obj.x, obj.y
        menx, meny = GetMenXY()
        if IsClosed(menx, meny, objx, objy):
            # 上一次的跑动的按键恢复
            player.UpLatestKey()

            # 朝向更新
            player.ChaoxiangFangxiang(menx, objx)

            print("SeekAndAttackMonster: 开始攻击 %.f, %.f" % (objx, objy))

            time.sleep(0.15)
            PressAtack()

            # 普通攻击后判断一下血量
            newobj = UpdateMonsterInfo(obj)
            if newobj is None or newobj.hp < 1:
                return

            # 普通攻击后判断一下朝向
            objx, objy = newobj.x, newobj.y
            menx, meny = GetMenXY()
            player.ChaoxiangFangxiang(menx, objx)

            skill = player.skills.GetMaxLevelAttackSkill()
            if skill is not None:
                print("使用技能 %s" % skill.name)
                skill.Use()
                player.skills.Update()
            else:
                print("没有技能可释放")
        else:
            player.Seek(objx, objy)


# 靠近并捡取物品
class SeekAndPickUp(State):
    def Execute(self, player):
        obj = NearestGood()

        # 如果没有物品了,那么切换状态
        if obj is None:
            player.ChangeState(StandStateInstance)
            return

        objx, objy = obj.x, obj.y
        menx, meny = GetMenXY()
        if IsInEqualLocation(menx, meny, objx, objy):
            # 上一次的跑动的按键恢复
            player.UpLatestKey()
            print("捡取")
            time.sleep(0.35)
            PressX()
        else:
            player.Seek2(objx, objy)


# 门已开,去过图
class DoorOpenGotoNext(State):
    currentx = None
    currenty = None

    def Execute(self, player):
        # 进到新的地图
        curx, cury = GetCurrentMapXy()
        if curx != self.currentx and cury != self.currenty:
            player.ChangeState(StandStateInstance)
            self.currentx = curx
            self.currenty = cury
            return
        else:
            door = GetNextDoor()
            if door.x == 0 and door.y == 0:
                player.ChangeState(StandStateInstance)
                return
            player.Seek2(door.x, door.y)


StandStateInstance = StandState()
SeekAndAttackMonsterInstance = SeekAndAttackMonster()
SeekAndPickUpInstance = SeekAndPickUp()
DoorOpenGotoNextInstance = DoorOpenGotoNext()


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
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 800, 600,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetForegroundWindow(hwnd)

    player = Player()
    player.ChangeState(StandStateInstance)

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
