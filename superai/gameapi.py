import copy
import sys
import os
import time
from enum import Enum

import math
from win32api import Sleep

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.yijianshu import PressSkill, RanSleep
from superai.vkcode import VK_CODE
from superai.defer import defer

from ctypes import *

if os.path.exists("c:/win/x64/Release/"):
    lib = CDLL("c:/win/x64/Release/helpdll-xxiii.dll", RTLD_GLOBAL)
else:
    lib = CDLL("E:/win/reference/project/xxiii/x64/Release/helpdll-xxiii.dll", RTLD_GLOBAL)


class MenInfo(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("z", c_float),
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
                "obj: 0x%08X 名称: %s 等级: %d hp: %d mp: %d 疲劳: %d/%d 状态: %s 方向: %d 人物坐标 (%.f,%.f,%.f)  负重 (%d,%d)" % (
            self.object, self.name, self.level, self.hp, self.mp,
            self.maxpilao - self.curpilao, self.maxpilao, self.statestr, self.fangxiang, self.x, self.y, self.z,
            self.fuzhongcur, self.fuzhongmax))


class Door(Structure):
    _fields_ = [
        ("x", c_int32),
        ("y", c_int32),
        ("xf", c_int32),
        ("yf", c_int32),

        ("cx", c_int32),
        ("cy", c_int32),

        ("prevcx", c_int32),
        ("prevcy", c_int32),

        ("firstcx", c_int32),
        ("firstcy", c_int32),

        ("secondcx", c_int32),
        ("secondcy", c_int32),
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
        ("doorslen", c_uint32),
        ("doors", c_uint32 * 100),
        ("roomw", c_uint32),
        ("roomh", c_uint32),
    ]

    def __str__(self):
        str_ = "地图对象: 0x%08X 地图名称: %s 地图编号: %d 起始位置: (%d,%d) BOSS位置: (%d,%d) 当前位置: (%d, %d) 宽高: (%d,%d) 开门: %d\n" % (
            self.mapobj, self.name, self.mapid, self.beginx, self.beginy, self.bossx, self.bossy, self.curx, self.cury,
            self.w, self.h, self.kaimen)
        str_ = str_ + "房间宽: %d 房间高: %d" % (self.roomw, self.roomh)
        return str_


class MapObj(Structure):
    _fields_ = [
        ("object", c_uint32),
        ("type", c_uint32),
        ("zhenying", c_uint32),
        ("name", c_wchar * 100),
        ("x", c_float),
        ("y", c_float),
        ("z", c_float),
        ("hp", c_uint32),
        ("code", c_uint32),
        ("width", c_uint32),
        ("height", c_uint32),
    ]

    def __str__(self):
        return (
                "对象: 0x%08X 类型: 0x%X 阵营: 0x%X 名称: %s 坐标:(%.f,%.f,%.f)  生命: %d 代码: %d w: %d h: %d" % (
            self.object, self.type, self.zhenying, self.name, self.x, self.y, self.z, self.hp,
            self.code, self.width, self.height))


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
        ("cx", c_int32),
        ("cy", c_int32),
        ("prevcx", c_int32),
        ("prevcy", c_int32),

        ("firstcx", c_int32),
        ("firstcy", c_int32),

        ("secondcx", c_int32),
        ("secondcy", c_int32),
    ]

    def __str__(self):
        return (
                "%d %d" % (
            self.cx, self.cy))


lib.Init.argtypes = []
lib.Init.restype = c_bool

lib.FlushPid.argtypes = []
lib.FlushPid.restype = c_bool

lib.Free.argtypes = [c_void_p]

lib.ExGetMenInfo.argtypes = [POINTER(MenInfo)]

lib.ExGetMapInfo.argtypes = [POINTER(MapInfo)]

lib.ExGetMapObj.argtypes = [POINTER(POINTER(MapObj)), POINTER(c_int)]

lib.ExGetMapMonsters.argtypes = [POINTER(POINTER(MapObj)), POINTER(c_int)]

lib.ExGetMapGoods.argtypes = [POINTER(POINTER(MapObj)), POINTER(c_int)]

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
HUANGJINCHONG = 0x78  # 黄金虫子

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
    CHONGDIE = 8


# 大矩阵
MOVE_BIG_V_WIDTH = 80 / 2
MOVE_BIG_H_WIDTH = 80 / 2

# 误差
MOVE_SMALL_V_WIDTH = 20 / 2
MOVE_SMALL_H_WIDTH = 20 / 2

# 大小矩阵
BIG_RENT = 1
SMALL_RENT = 2

# 慢走矩形
MANZOU_V_WIDTH = 200 / 2
MANZOU_H_WIDTH = 200 / 2

# 拾取矩形
PICKUP_V_WIDTH = 40 / 2
PICKUP_H_WIDTH = 40 / 2

# 怪物在太远的距离,先捡物品
PICK_DISTANCE = 300

# 普通攻击矩形
ATTACK_V_WIDTH = 160 / 2
ATTACK_H_WIDTH = 40 / 2

# 攻击太靠近的垂直宽度
ATTACK_TOO_CLOSE_V_WIDTH = 1 / 2


def QuardrantWithOutRent(x2, y2, chuizhikuandu, shuipingkuandu):
    # 同一个垂直位置
    if abs(x2) < chuizhikuandu:
        if y2 > 0:
            return Quardant.XIA
        else:
            return Quardant.SHANG

    # 同一个水平位置
    if abs(y2) < shuipingkuandu:
        if x2 > 0:
            return Quardant.YOU
        else:
            return Quardant.ZUO

    # 右上,右下
    if x2 > 0:
        if y2 > 0:
            return Quardant.YOUXIA
        else:
            return Quardant.YOUSHANG

    # 左上,左下
    if x2 < 0:
        if y2 > 0:
            return Quardant.ZUOXIA
        else:
            return Quardant.ZUOSHANG

    raise NotImplementedError()


# 象限 (x1,y1,x2,y2) 是左上角开始算的坐标系
def GetQuadrant(x1, y1, x2, y2):
    # 转换成以x1, y1为坐标起点的坐标系
    newx2, newy2 = x2 - x1, y2 - y1
    if abs(newx2) < MOVE_BIG_V_WIDTH and abs(newy2) < MOVE_BIG_H_WIDTH:
        # 在中间的小矩阵
        if abs(newx2) < MOVE_SMALL_V_WIDTH and abs(newy2) < MOVE_SMALL_H_WIDTH:
            return Quardant.CHONGDIE, SMALL_RENT
        return QuardrantWithOutRent(newx2, newy2, MOVE_SMALL_V_WIDTH, MOVE_SMALL_H_WIDTH), SMALL_RENT
    return QuardrantWithOutRent(newx2, newy2, MOVE_BIG_V_WIDTH, MOVE_BIG_H_WIDTH), BIG_RENT


# 获得水平方向反向
def GetFleeQuadrant(x1, y1, x2, y2):
    quad, rent = GetQuadrant(x1, y1, x2, y2)
    if quad in [Quardant.YOU, Quardant.YOUXIA, Quardant.YOUSHANG]:
        return Quardant.ZUO, rent
    if quad in [Quardant.ZUO, Quardant.ZUOXIA, Quardant.ZUOSHANG]:
        return Quardant.YOU, rent
    if quad in [Quardant.SHANG, Quardant.XIA, Quardant.CHONGDIE]:
        if GetFangxiang(x1, x2) == RIGHT:
            return Quardant.ZUO
        else:
            return Quardant.YOU


# 是否在捡取范围
def CanbePickup(x1, y1, x2, y2):
    V_WIDTH = abs(x2 - x1)
    H_WIDTH = abs(y2 - y1)
    if V_WIDTH < PICKUP_V_WIDTH and H_WIDTH < PICKUP_H_WIDTH:
        return True
    return False


# 是否在慢走范围内
def WithInManzou(x1, y1, x2, y2):
    V_WIDTH = abs(x2 - x1)
    H_WIDTH = abs(y2 - y1)
    if V_WIDTH < MANZOU_V_WIDTH and H_WIDTH < MANZOU_H_WIDTH:
        return True
    return False


# 获取对象在右边还是左边
def GetFangxiang(x1, x2):
    if x2 - x1 > 0:
        return RIGHT
    else:
        return LEFT


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
    objs = POINTER(MapObj)()
    count = c_int(0)
    lib.ExGetMapMonsters(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst = []
    for i in range(count.value):
        outlst.append(copy.deepcopy(objs[i]))
    return outlst


# 获取物品
def GetGoods():
    objs = POINTER(MapObj)()
    count = c_int(0)
    lib.ExGetMapGoods(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst = []
    for i in range(count.value):
        outlst.append(copy.deepcopy(objs[i]))
    return outlst


# 有怪物
def HaveMonsters():
    monsters = GetMonsters()
    return len(monsters) > 0


# 怪物太远了
def MonsterIsToofar():
    monster = NearestMonster()
    if monster is None:
        return True
    men = GetMenInfo()
    if distance(men.x, men.y, monster.x, monster.y) > PICK_DISTANCE:
        return True
    return False


# 地面有物品
def HaveGoods():
    goods = GetGoods()
    return len(goods) > 0


# 最近怪物对象
def NearestMonster():
    menInfo = GetMenInfo()
    monsters = GetMonsters()
    if len(monsters) < 1:
        return None
    return min(monsters, key=lambda mon: distance(mon.x, mon.y, menInfo.x, menInfo.y))


# 最近物品对象
def NearestGood():
    menInfo = GetMenInfo()
    goods = GetGoods()
    if len(goods) < 1:
        return None
    return min(goods, key=lambda good: distance(good.x, good.y, menInfo.x, menInfo.y))


# 没死亡
def IsLive():
    meninfo = GetMenInfo()
    return meninfo.hp >= 1


# 获取人物x,y坐标
def GetMenXY():
    meninfo = GetMenInfo()
    return meninfo.x, meninfo.y


# 获得朝向
def GetMenChaoxiang():
    meninfo = GetMenInfo()
    return meninfo.fangxiang


# 更新怪物对象信息
def UpdateMonsterInfo(monster):
    objs = GetMonsters()
    for obj in objs:
        if obj.object == monster.object and obj.hp > 0:
            return obj
    return None


# 获取门是否开的信息
def IsNextDoorOpen():
    door = GetNextDoor()
    return door.cx != 0 and door.cy != 0


# 是否当前处在boss房间
def IsCurrentInBossFangjian():
    mapinfo = GetMapInfo()

    if mapinfo.curx == mapinfo.bossx and \
            mapinfo.cury == mapinfo.bossy:
        return True

    return False


# 获取当前房间的x,y
def GetCurrentMapXy():
    mapinfo = GetMapInfo()
    return mapinfo.curx, mapinfo.cury


# 技能包装.

idxkeymap = {
    0: VK_CODE['a'], 1: VK_CODE['s'], 2: VK_CODE['d'], 3: VK_CODE['f'], 4: VK_CODE['g'], 5: VK_CODE['h'],
    6: VK_CODE['q'], 7: VK_CODE['w'], 8: VK_CODE['e'], 9: VK_CODE['r'], 10: VK_CODE['t'], 11: VK_CODE['y'],
}


# 技能种类
class SkillType(Enum):
    Yidong = 1,
    Gongji = 2,
    Buff = 3


# 技能属性包装
class SkillData:
    # 技能种类
    type = None

    # 攻击垂直宽度
    v_w = ATTACK_V_WIDTH
    # 攻击水平宽度
    h_w = ATTACK_H_WIDTH

    # 攻击太靠近的垂直宽度
    too_close_v_w = ATTACK_TOO_CLOSE_V_WIDTH

    # 释放级别. 越高级的越先释放
    level = 0

    # 按键延迟时间
    delaytime = 0.1

    # 事后时间
    afterdelay = 0.05

    def __init__(self, **kw):
        for k, w in kw.items():
            setattr(self, k, w)


# 初始化技能配置. 因为内存中读取不到
skillSettingMap = {

    # 通用

    # 移动
    "后跳": SkillData(type=SkillType.Yidong),

    # 阿修罗

    # buff
    "波动刻印": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.8),
    "杀意波动": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.8),

    # 近
    "上挑": SkillData(type=SkillType.Gongji, level=3),
    "鬼斩": SkillData(type=SkillType.Gongji, level=5),
    "裂波斩": SkillData(type=SkillType.Gongji, level=7, afterdelay=0.3),
    "鬼连斩": SkillData(type=SkillType.Gongji, level=8),
    "波动爆发": SkillData(type=SkillType.Gongji, level=11),
    "无双波": SkillData(type=SkillType.Gongji, level=13),

    # 远
    "地裂 · 波动剑": SkillData(type=SkillType.Gongji, level=10, v_w=200 / 2, h_w=40 / 2),
    "鬼印珠": SkillData(type=SkillType.Gongji, level=12, v_w=400 / 2, h_w=40 / 2, too_close_v_w=140 / 2, delaytime=0.5),
    "邪光斩": SkillData(type=SkillType.Gongji, level=15, v_w=400 / 2, h_w=40 / 2, delaytime=0.6),
    "冰刃 · 波动剑": SkillData(type=SkillType.Gongji, level=16, v_w=400 / 2, h_w=40 / 2),
    "爆炎 · 波动剑": SkillData(type=SkillType.Gongji, level=14, v_w=400 / 2, h_w=40 / 2),

    # 神龙天女
    "神谕之祈愿": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.8),

}


# 技能包装
class Skill:
    # 是否存在
    exist = False
    # 内存读出来的冷却时间
    cooding = 0
    # 名称
    name = ""
    # 内存上次使用时间
    gamelatestusedtime = 0
    # 快捷键
    key = None
    # python内部记录 实际上次使用时间
    lastusedtime = 0
    # python对技能的配置
    skilldata = SkillData(type=SkillType.Gongji)

    def __init__(self, **kw):
        for k, w in kw.items():
            setattr(self, k, w)

    # 是否垂直宽度太靠近致使攻击不能命中
    def IsV_WTOOClose(self, menx, objx):
        newx = objx - menx
        return abs(newx) < self.skilldata.too_close_v_w

    # 是否水平宽度在技能范围内
    def IsH_WInRange(self, meny, objy):
        newy = objy - meny
        return abs(newy) < self.skilldata.h_w

    # 是否垂直宽度在技能范围内
    def isV_WInRange(self, menx, objx):
        newx = objx - menx
        return abs(newx) < self.skilldata.v_w

    # 人物靠近怪物时不靠近怪物坐标,而是靠近到该技能的范围中点
    def GetSeekXY(self, menx, meny, objx, objy):
        if GetFangxiang(menx, objx) == RIGHT:
            return objx - (self.skilldata.v_w - self.skilldata.too_close_v_w) / 2 - self.skilldata.too_close_v_w, objy

        if GetFangxiang(menx, objx) == LEFT:
            return objx + (self.skilldata.v_w - self.skilldata.too_close_v_w) / 2 + self.skilldata.too_close_v_w, objy

        raise NotImplementedError()

    # 可以使用
    def CanbeUsed(self):
        # 是否存在
        if not self.exist:
            return False

        # 是否从未使用
        if self.cooding == 0 and self.gamelatestusedtime == 0:
            return True

        # 使用过,并且 当且时间减去过去时间 大于冷却时间
        escaped = (int(time.time()) - self.lastusedtime) * 1000
        if escaped > self.cooding:
            return True

        return False

    # 设置按键
    def SetKey(self, idx):
        self.key = idxkeymap[idx]

    # 更新python内部使用时间
    def UpdateUsedTime(self):
        self.lastusedtime = int(time.time())

    # 初始化技能在内存中的设置
    def Init(self):
        if self.name in skillSettingMap:
            self.skilldata = skillSettingMap[self.name]

    # 使用
    def Use(self):
        PressSkill(self.key, self.skilldata.delaytime, self.skilldata.afterdelay)


# 普通攻击
simpleAttackSkill = Skill(exit=True, key=VK_CODE['x'], name="普通攻击")
simpleAttackSkill.skilldata.delaytime = 0.8
simpleAttackSkill.skilldata.afterdelay = 0.05


# 技能列表
class Skills:
    def __init__(self):
        self.skilllst = []
        for i in range(12):
            self.skilllst.append(Skill())

    # 用完技能马上更新一下状态. (释放时间变化, python内部释放时间就变化)
    def Update(self):
        objs = GetSkillObj()
        for obj in objs:
            self.skilllst[obj.idx].exist = True
            self.skilllst[obj.idx].cooding = obj.cooling
            self.skilllst[obj.idx].name = obj.name

            if self.skilllst[obj.idx].gamelatestusedtime != obj.sendtime:
                self.skilllst[obj.idx].UpdateUsedTime()

            self.skilllst[obj.idx].gamelatestusedtime = obj.sendtime
            self.skilllst[obj.idx].SetKey(obj.idx)

            self.skilllst[obj.idx].Init()

        # 技能对象是否存在
        for skillobj in self.skilllst:
            skillobj.exist = False

        for obj in objs:
            self.skilllst[obj.idx].exist = True

    # 刷新所有冷却时间 (python内部)
    def FlushAllTime(self):
        for skill in self.skilllst:
            skill.lastusedtime = 0

    # 获取可以使用的技能列表
    def GetCanBeUsedAttackSkills(self):
        outlst = []
        for skill in self.skilllst:
            if skill.CanbeUsed() and skill.skilldata.type == SkillType.Gongji:
                outlst.append(skill)
        return outlst

    # 获取可使用Buff技能的列表
    def GetCanBeUseBuffSkills(self):
        outlst = []
        for skill in self.skilllst:
            if skill.CanbeUsed() and skill.skilldata.type == SkillType.Buff:
                outlst.append(skill)
        return outlst

    # 获得高等级的技能释放
    def GetMaxLevelAttackSkill(self):
        skills = self.GetCanBeUsedAttackSkills()
        if len(skills) < 1:
            return None
        return max(skills, key=lambda skill: skill.skilldata.level)

    # 有技能可以被释放
    def HaveSkillCanBeUse(self):
        skills = self.GetCanBeUsedAttackSkills()
        return len(skills) > 0

    # 有buff可以被释放
    def HaveBuffCanBeUse(self):
        skills = self.GetCanBeUseBuffSkills()
        return len(skills) > 0

    # 某个技能是否被释放过(比如修罗的技能
    def DidSkillHavebeenUsed(self, skillname):
        objs = GetSkillObj()
        for obj in objs:
            if obj.name == skillname:
                if obj.sendtime != 0:
                    return True
        return False


# 打印可以被使用的技能
def PrintCanBeUsedSkill():
    skills = Skills()
    skills.Update()
    skills.FlushAllTime()

    while True:
        RanSleep(1)
        print("===可以使用的技能===")
        skills.Update()
        canbeused = skills.GetCanBeUsedAttackSkills()
        for skill in canbeused:
            print(skill.name)


# 不断打印坐标
def PrintXY():
    while True:
        x, y = GetMenXY()
        print(x, y)
        RanSleep(1)


def main():
    if GameApiInit():
        print("Init helpdll-xxiii.dll ok")
    else:
        print("Init helpdll-xxiii.dll err")

    FlushPid()

    # while True:
    #     PrintMenInfo()
    #     RanSleep(0.1)
    # PrintMenInfo()
    PrintMapInfo()
    # PrintMapObj()
    # PrintBagObj()
    # PrintEquipObj()
    # PrintSkillObj()
    # PrintTaskObj()
    # PrintNextMen()

    # PrintMonsterXY()

    # PrintCanBeUsedSkill()

    # print(GetNextDoor())

    # print(IsCurrentInBossFangjian())
    #
    # print(GetNextDoor())

    # PrintXY()


if __name__ == "__main__":
    main()
