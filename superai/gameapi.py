import copy
import sys
import os
from enum import Enum
from typing import List

import math
from win32api import Sleep

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.defer import defer

from ctypes import *

lib = CDLL("E:/win/reference/project/xxiii/x64/Release/helpdll-xxiii.dll", RTLD_GLOBAL)


class MenInfo(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("money", c_wchar * 100),
        ("fuzhongcur", c_uint32),
        ("fuzhongmax", c_uint32),
        ("object", c_uint32),
        ("name", c_wchar * 100),
        ("level", c_uint32),
        ("hp", c_uint32),
        ("mp", c_uint32),
        ("curpilao", c_uint32),
        ("maxpilao", c_uint32),
        ("state", c_uint32),
        ("statestr", c_wchar * 10),
        ("fangxiang", c_uint32),
    ]

    def __str__(self):
        return (
                "obj: 0x%08X 名称: %s 等级: %d hp: %d mp: %d 疲劳: %d/%d 状态: %s 方向: %d 人物坐标 (%.f,%.f) 负重 (%d,%d)" % (
            self.object, self.name, self.level, self.hp, self.mp,
            self.maxpilao - self.curpilao, self.maxpilao, self.statestr, self.fangxiang, self.x, self.y,
            self.fuzhongcur, self.fuzhongmax))


class Door(Structure):
    _fields_ = [
        ("x", c_uint32),
        ("y", c_uint32),
        ("xf", c_uint32),
        ("yf", c_uint32),

        ("cx", c_uint32),
        ("cy", c_uint32),

        ("prevcx", c_uint32),
        ("prevcy", c_uint32),

        ("firstcx", c_uint32),
        ("firstcy", c_uint32),

        ("secondcx", c_uint32),
        ("secondcy", c_uint32),
    ]


class MapInfo(Structure):
    _fields_ = [
        ("left", Door),  # TODO 未打印
        ("right", Door),  # TODO 未打印
        ("top", Door),  # TODO 未打印
        ("down", Door),  # TODO 未打印
        ("mapid", c_uint32),
        ("beginx", c_uint32),
        ("beginy", c_uint32),
        ("bossx", c_uint32),
        ("bossy", c_uint32),
        ("curx", c_uint32),
        ("cury", c_uint32),
        ("w", c_uint32),
        ("h", c_uint32),
        ("kaimen", c_bool),
        ("mapobj", c_uint32),
        ("name", c_wchar * 100),
        # 	std::vector<DWORD> doors; 开门方式 # TODO 怎么传递std::vector
    ]

    def __str__(self):
        return (
                "地图对象: 0x%08X 地图名称: %s 地图编号: %d 起始位置: (%d,%d) BOSS位置: (%d,%d) 当前位置: (%d, %d) 宽高: (%d,%d) 开门: %d" % (
            self.mapobj, self.name, self.mapid, self.beginx, self.beginy, self.bossx, self.bossy, self.curx, self.cury,
            self.w, self.h,
            self.kaimen))


class MapObj(Structure):
    _fields_ = [
        ("object", c_uint32),
        ("type", c_uint32),
        ("zhenying", c_uint32),
        ("name", c_wchar * 100),
        ("x", c_float),
        ("y", c_float),
    ]

    def __str__(self):
        return (
                "对象: 0x%08X 类型: 0x%X 阵营: 0x%X 名称: %s 坐标:(%.0f,%.0f)" % (
            self.object, self.type, self.zhenying, self.name, self.x, self.y))


class BagObj(Structure):
    _fields_ = [
        ("idx", c_uint32),
        ("object", c_uint32),
        ("num", c_uint32),
        ("color", c_uint32),
        ("name", c_wchar * 100),
    ]

    def __str__(self):
        return (
                "[%d] 对象: 0x%08X 名称: %s 数量: %d 颜色: %d" % (
            self.idx, self.object, self.name, self.num, self.color))


class SkillObj(Structure):
    _fields_ = [
        ("idx", c_uint32),
        ("object", c_uint32),
        ("name", c_wchar * 100),
        ("cooling", c_uint32),
        ("sendtime", c_uint32),
        ("canbeused", c_bool),
    ]

    def __str__(self):
        return (
                "[%d] 对象: 0x%08X 名称: %s 冷却时间: %d 截止时间: %d " % (
            self.idx, self.object, self.name, self.cooling, self.sendtime))


class TaskObj(Structure):
    _fields_ = [
        ("idx", c_uint32),
        ("object", c_uint32),
        ("type", c_uint32),
        ("name", c_wchar * 100),
    ]

    def __str__(self):
        return (
                "[%d]对象: 0x%08X 名称: %s 类型: 0x%X  " % (
            self.idx, self.object, self.name, self.type))


class ExGuoToMenZuoBiao(Structure):
    _fields_ = [
        ("x", c_uint32),
        ("y", c_uint32),
    ]

    def __str__(self):
        return (
                "%d %d" % (
            self.x, self.y))


lib.Init.argtypes = []
lib.Init.restype = c_bool

lib.FlushPid.argtypes = []
lib.FlushPid.restype = c_bool

lib.Free.argtypes = [c_void_p]

lib.ExGetMenInfo.argtypes = [POINTER(MenInfo)]

lib.ExGetMapInfo.argtypes = [POINTER(MapInfo)]

lib.ExGetMapObj.argtypes = [POINTER(POINTER(MapObj)), POINTER(c_int)]

lib.ExGetBagObj.argtypes = [POINTER(POINTER(BagObj)), POINTER(c_int)]

lib.ExGetGetEquipObj.argtypes = [POINTER(POINTER(BagObj)), POINTER(c_int)]

lib.ExGetSkillObj.argtypes = [POINTER(POINTER(SkillObj)), POINTER(c_int)]

lib.ExGetTaskObj.argtypes = [POINTER(POINTER(TaskObj)), POINTER(c_int)]

lib.ExNextDoor.argtypes = [POINTER(ExGuoToMenZuoBiao)]

lib.Free.argtypes = [c_void_p]

# === enum

# 类型
MAN = 0x111  # 人
MONSTER = 0x211  # 怪物
GOOD = 0x121  # 物品

# 阵营
OWN = 0x0  # 己方
ENEMY = 0x64  # 敌人
ENEMY2 = 0x65  # 敌人 召唤
MOGU = 0x32  # 蘑菇人???
ZHAOHUAN = 0x6e  # 召唤物

# 方向
RIGHT = 1  # 右
LEFT = 0  # 左

# 状态
CHENZHEN = 0x0  # 城镇
XUANTU = 0x8  # 选图
TUNEI = 0x1  # 图内

# 门方向
XIA = 0x3
ZUO = 0x0
SHANG = 0x2
YOU = 0x1
DEFAULT_ = 0x4
BOSS_ = 0x5


# 其他
def distance(x1, y1, x2, y2) -> int:
    xseparation = x2 - x1
    yseparation = y2 - y1
    return int(math.sqrt(xseparation * xseparation + yseparation * yseparation))


# 点积
# def Dot(x1, y1, x2, y2):
#     return x1 * x2 + y1 * y2


# 获取对象在右边还是左边
def GetFangxiang(x1, x2):
    if x2 - x1 > 0:
        return 1
    else:
        return 0


# 八个方向
class Quardant(Enum):
    ZUO = 0
    YOU = 1
    SHANG = 2
    XIA = 3
    ZUOSHANG = 4
    YOUSHANG = 5
    ZUOXIA = 6
    YOUXIA = 7
    # CHONGDIE = 8


# 是否靠近 (垂直范围小一些(攻击宽度), 水平范围大一些)
def IsClosedExtra(x1, y1, x2, y2):
    dis = distance(x1, y1, x2, y2)
    kuandu = abs(y1 - y2)
    changdu = abs(x1 - x2)

    if kuandu < 20 and changdu < 120:
        return True, dis, kuandu, changdu

    return False, dis, kuandu, changdu


def IsClosed(x1, y1, x2, y2):
    rtn, _, _, _ = IsClosedExtra(x1, y1, x2, y2)
    return rtn


# 在指定距离内 (慢走过去)
def WithInDistanceExtra(x1, y1, x2, y2):
    dis = distance(x1, y1, x2, y2)
    kuandu = abs(y1 - y2)
    changdu = abs(x1 - x2)

    if kuandu < 50 and changdu < 150:
        return True, dis, kuandu, changdu

    return False, dis, kuandu, changdu


def WithInDistance(x1, y1, x2, y2):
    rtn, _, _, _ = WithInDistanceExtra(x1, y1, x2, y2)
    return rtn


# 象限 (x1,y1,x2,y2) 是左上角开始算的坐标系
def GetQuadrant(x1, y1, x2, y2):
    # 转换成以x1, y1为坐标起点的坐标系
    newx2, newy2 = x2 - x1, y2 - y1

    if newx2 == 0 and newy2 == 0:
        # 不可能会重叠吧
        # return Quardant.CHONGDIE
        return Quardant.YOU

    # 同一个垂直位置
    if abs(newx2) < 15:
        if newy2 > 0:
            return Quardant.XIA
        else:
            return Quardant.SHANG

    # 同一个水平位置
    if abs(newy2) < 15:
        if newx2 > 0:
            return Quardant.YOU
        else:
            return Quardant.ZUO

    # 右上,右下
    if newx2 > 0:
        if newy2 > 0:
            return Quardant.YOUXIA
        else:
            return Quardant.YOUSHANG

    # 左上,左下
    if newx2 < 0:
        if newy2 > 0:
            return Quardant.ZUOXIA
        else:
            return Quardant.ZUOSHANG


# === help dll 基础
def GameApiInit():
    return lib.Init()


def FlushPid():
    lib.FlushPid()


# === help dll 接口包装

# 人物信息
def GetMenInfo():
    menInfo = MenInfo()
    lib.ExGetMenInfo(pointer(menInfo))
    return menInfo


# 地图信息
def GetMapInfo():
    mapInfo = MapInfo()
    lib.ExGetMapInfo(pointer(mapInfo))
    return mapInfo


# 地图对象数组
def GetMapObj():
    objs = POINTER(MapObj)()
    count = c_int(0)
    lib.ExGetMapObj(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst = []
    for i in range(count.value):
        outlst.append(copy.deepcopy(objs[i]))
    return outlst


# 背包数组
def GetBagObj():
    objs = POINTER(BagObj)()
    count = c_int(0)
    lib.ExGetBagObj(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst = []
    for i in range(count.value):
        outlst.append(copy.deepcopy(objs[i]))
    return outlst


# 装备数组
def GetEquipObj():
    objs = POINTER(BagObj)()
    count = c_int(0)
    lib.ExGetGetEquipObj(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst = []
    for i in range(count.value):
        outlst.append(copy.deepcopy(objs[i]))

    return outlst


# 技能数组
def GetSkillObj():
    objs = POINTER(SkillObj)()
    count = c_int(0)
    lib.ExGetSkillObj(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst = []
    for i in range(count.value):
        outlst.append(copy.deepcopy(objs[i]))
    return outlst


# 任务数组
def GetTaskObj():
    objs = POINTER(TaskObj)()
    count = c_int(0)
    lib.ExGetTaskObj(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst = []
    for i in range(count.value):
        outlst.append(copy.deepcopy(objs[i]))
    return outlst


# 下一个门的坐标
def GetNextDoor():
    menzuobiao = ExGuoToMenZuoBiao()
    lib.ExNextDoor(pointer(menzuobiao))
    return menzuobiao


# === 调试打印
def PrintMenInfo():
    menInfo = GetMenInfo()
    print(menInfo)


def PrintMapInfo():
    mapInfo = GetMapInfo()
    print(mapInfo)


def PrintMapObj():
    outlst = GetMapObj()
    for obj in outlst:
        print(obj)


def PrintBagObj():
    outlst = GetBagObj()
    for obj in outlst:
        print(obj)


def PrintEquipObj():
    outlst = GetEquipObj()
    for obj in outlst:
        print(obj)


def PrintSkillObj():
    outlst = GetSkillObj()
    for obj in outlst:
        print(obj)


def PrintTaskObj():
    outlst = GetTaskObj()
    for obj in outlst:
        print(obj)


def PrintNextMen():
    menzuobiao = GetNextDoor()
    print(menzuobiao)


# === 2次包装

# 获取怪物
def GetMonsters():
    outlst = GetMapObj()
    monsters = []
    for obj in outlst:
        if obj.type in [MONSTER, MAN] and \
                obj.zhenying in [ENEMY, ENEMY2, MOGU, ZHAOHUAN]:
            monsters.append(obj)
    return monsters


# 有怪物
def HaveMonsters():
    monsters = GetMonsters()
    return len(monsters) > 0


# 最近怪物对象
def NearestMonster():
    menInfo = GetMenInfo()
    monsters = GetMonsters()
    if len(monsters) < 1:
        return None
    return min(monsters, key=lambda mon: distance(mon.x, mon.y, menInfo.x, menInfo.y))


# 没死亡
def IsLive():
    meninfo = GetMenInfo()
    return meninfo.hp >= 1


# 获取人物x,y坐标
def GetMenXY():
    meninfo = GetMenInfo()
    return meninfo.x, meninfo.y


# 打印和怪物坐标
def PrintMonsterXY():
    while True:
        Sleep(1000)

        menx, meny = GetMenXY()
        monster = NearestMonster()
        if monster is None:
            continue
        objx = monster.x
        objy = monster.y
        quad = GetQuadrant(menx, meny, monster.x, monster.y)
        closed, dis, kuandu, changdu = IsClosedExtra(menx, meny, objx, objy)
        print("%s 靠近: %d 距离: %d 宽度: %d 长度: %d" % (quad.name, closed, dis, kuandu, changdu))


# 获得朝向
def GetMenChaoxiang():
    meninfo = GetMenInfo()
    return meninfo.fangxiang


# class



class Skills:
    skillmap = None

    def Update(self):
        pass


def main():
    if GameApiInit():
        print("Init helpdll-xxiii.dll ok")
    else:
        print("Init helpdll-xxiii.dll err")

    FlushPid()

    # PrintMenInfo()
    # PrintMapInfo()
    # PrintMapObj()
    # PrintBagObj()
    # PrintEquipObj()
    PrintSkillObj()
    # PrintTaskObj()
    # PrintNextMen()

    # PrintMonsterXY()


if __name__ == "__main__":
    main()
