import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

import copy
from enum import Enum
import math

from superai.pathsetting import GetHelpdllLib, GetDriverStartFile
from superai.common import InitLog
from superai.yijianshu import PressSkill, PressKey, DownZUO, DownYOU, DownSHANG, DownXIA, DownZUOSHANG, DownZUOXIA, \
    DownYOUSHANG, DownYOUXIA, UpZUO, UpYOU, UpSHANG, UpXIA, UpZUOSHANG, UpZUOXIA, UpYOUSHANG, UpYOUXIA, RanSleep, \
    MouseMoveTo, KongjianSleep, MouseLeftClick
from superai.vkcode import VK_CODE
from superai.defer import defer

from ctypes import *

lib = GetHelpdllLib()


class MenInfo(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("z", c_float),
        ("money", c_uint32),
        ("fuzhongcur", c_uint32),
        ("fuzhongmax", c_uint32),
        ("object", c_uint32),
        ("name", c_wchar * 100),
        ("zhuanzhihou", c_wchar * 30),
        ("zhuanzhiqian", c_wchar * 30),
        ("level", c_uint32),
        ("hp", c_uint64),
        ("mp", c_uint32),
        ("curpilao", c_uint32),
        ("maxpilao", c_uint32),
        ("state", c_uint32),
        ("statestr", c_wchar * 10),
        ("fangxiang", c_uint32),
        ("jipao", c_bool),
        ("tanchu", c_bool),
        ("esc", c_bool),
        ("w", c_uint32),
        ("h", c_uint32),
        ("chengzhenx", c_float),
        ("chengzheny", c_float),
        ("account", c_uint32),
        ("region", c_wchar * 30),
        ("zhicai", c_uint32)
    ]

    def __str__(self):
        retstr = ""

        retstr += "obj: 0x%08X 名称: %s 等级: %d hp: %d mp: %d 疲劳: %d/%d 状态: %s 方向: %d 疾跑: %d \n" % (
            self.object, self.name, self.level, self.hp, self.mp,
            self.maxpilao - self.curpilao, self.maxpilao, self.statestr, self.fangxiang, self.jipao)
        retstr += " 转职前: %s 转职后: %s\n" % (self.zhuanzhiqian, self.zhuanzhihou)
        retstr += "人物坐标 (%.f,%.f,%.f) w h %d %d\n" % (self.x, self.y, self.z, self.w, self.h)
        retstr += "负重 (%d,%d) 金币: %d\n" % (self.fuzhongcur, self.fuzhongmax, self.money)
        retstr += "弹出 %d esc %d\n" % (self.tanchu, self.esc)
        retstr += "城镇坐标: (%d, %d)\n" % (self.chengzhenx, self.chengzheny)
        retstr += "制裁: %d 账号: %d, 大区: %s\n" % (self.zhicai, self.account, self.region)
        return retstr


class Door(Structure):
    _fields_ = [
        ("x", c_int32),
        ("y", c_int32),
        ("w", c_int32),
        ("h", c_int32),

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
    ]

    def __str__(self):
        str_ = "地图对象: 0x%08X 地图名称: %s 地图编号: %d 起始位置: (%d,%d) BOSS位置: (%d,%d) 当前位置: (%d, %d) 宽高: (%d,%d) 开门: %d\n" % (
            self.mapobj, self.name, self.mapid, self.beginx, self.beginy, self.bossx, self.bossy, self.curx, self.cury,
            self.w, self.h, self.kaimen)
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
        ("hp", c_int32),
        ("code", c_uint32),
        ("w", c_int32),
        ("h", c_int32),
        ("obstacletype", c_uint32),
    ]

    def __str__(self):
        return (
                "对象: 0x%08X 类型: 0x%X 阵营: 0x%X 名称: %s 坐标:(%.f,%.f,%.f)  生命: %d 代码: %d w: %d h: %d obstype: %d" % (
            self.object, self.type, self.zhenying, self.name, self.x, self.y, self.z, self.hp,
            self.code, self.w, self.h, self.obstacletype))


BODYPOS = [14, 15, 16, 17, 18]
WUQIPOS = 12
SHIPINPOS = [19, 20, 21]

ChengHaoRequire = [12, 14, 15, 16, 17, 18, 19, 20, 21]

POSMAP = {
    12: "武器",
    13: "称号",
    14: "上衣",
    15: "头肩",
    16: "下装",
    17: "鞋",
    18: "腰带",
    19: "项链",
    20: "手镯",
    21: "戒指"
}

TYPEMAP = {
    0: "布甲",
    1: "皮甲",
    2: "轻甲",
    3: "重甲",
    4: "板甲"
}


class BagObj(Structure):
    _fields_ = [
        ("idx", c_uint32),
        ("object", c_uint32),
        ("num", c_uint32),
        ("color", c_uint32),  # 0普通 蓝1 紫2 粉3  勇者5 传说6
        ("name", c_wchar * 100),
        ("type", c_uint32),  # 装备2
        ("jiatype", c_uint32),  # 布甲0,皮甲1,轻甲2,重甲3,板甲4
        ("bodypos", c_uint32),  # 12武器,14上衣,15头肩,16下装,17鞋,18腰带
        ("wuqitype", c_wchar * 20),
        ("canbeusedlevel", c_uint32),  # 可使用等级
        ("curnaijiu", c_uint32),
        ("maxnaijiu", c_uint32),
    ]

    def FormatColor(self):
        if self.type == 2:
            m = {
                0: "普通",
                1: "蓝",
                2: "紫",
                3: "粉",
                5: "勇者",
                6: " 传说"
            }
            if self.color in m:
                return m[self.color]
            else:
                return "%d" % self.color
        else:
            return "%d" % self.color

    def FormatJiatype(self):
        if self.type == 2 and self.bodypos in [14, 15, 16, 17, 18]:
            if self.jiatype in TYPEMAP:
                return TYPEMAP[self.jiatype]
            else:
                return "%d" % self.jiatype
        else:
            return "%d" % self.jiatype

    def FormatBodyPos(self):
        if self.type == 2:
            if self.bodypos in POSMAP:
                return POSMAP[self.bodypos]
            else:
                return "%d" % self.bodypos
        else:
            return "%d" % self.bodypos

    def FormatWuqiType(self):
        if self.type == 2 and self.bodypos == 12:
            return self.wuqitype
        else:
            return ""

    def __str__(self):

        if self.type != 2:
            return (
                    "[%d] 对象: 0x%08X 名称: %s 数量: %d 颜色: %s" % (
                self.idx, self.object, self.name, self.num, self.FormatColor()))
        else:
            return (
                    "[%d] 对象: 0x%08X 名称: %s 数量: %d 颜色: %s 位置:%s  甲类型: %s 武器类型: %s 可使用等级 %d 耐久: %d/%d" % (
                self.idx, self.object, self.name, self.num, self.FormatColor(), self.FormatBodyPos(),
                self.FormatJiatype(), self.FormatWuqiType(), self.canbeusedlevel, self.curnaijiu, self.maxnaijiu))


class SkillObj(Structure):
    _fields_ = [
        ("idx", c_uint32),
        ("object", c_uint32),
        ("name", c_wchar * 100),
        ("cooling", c_uint32),
        ("sendtime", c_uint32),
        ("canbeused", c_bool),
        ("level", c_uint32),
    ]

    def __str__(self):
        return (
                "[%d] 对象: 0x%08X 名称: %s 冷却时间: %d 截止时间: %d 能否使用: %d 等级: %d" % (
            self.idx, self.object, self.name, self.cooling, self.sendtime, self.canbeused, self.level))


class TaskObj(Structure):
    _fields_ = [
        ("idx", c_uint32),
        ("object", c_uint32),
        ("type", c_uint32),
        ("name", c_wchar * 100),
        ("id", c_uint32),
        ("coindition", c_wchar * 20),
        ("type2", c_uint32),
        ("fubenid", c_uint32),
        ("mainflag", c_uint32),
        ("desc", c_wchar * 100),
    ]

    def __str__(self):
        return (
                "[%d]对象: 0x%08X 名称: %s 类型: 0x%X id: %d 条件: %s 类型2: 0x%X 副本id: %d 主线flag: 0x%X desc: %s" % (
            self.idx, self.object, self.name, self.type, self.id, self.coindition, self.type2, self.fubenid,
            self.mainflag, self.desc))


class AcceptedTaskObj(Structure):
    _fields_ = [
        ("idx", c_uint32),
        ("object", c_uint32),
        ("type", c_uint32),
        ("name", c_wchar * 100),
        ("needdo", c_uint32),  # 是否还需要做   0 做完了  1还需要做
        ("id", c_uint32),
        ("coindition", c_wchar * 20),
        ("type2", c_uint32),
        ("fubenid", c_uint32),
        ("mainflag", c_uint32),
        ("desc", c_wchar * 100),
    ]

    def __str__(self):
        return (
                "[%d]对象: 0x%08X 名称: %s 类型: 0x%X 还需要做: %d id: %d 条件: %s 类型2: 0x%X 副本id: %d 主线flag: 0x%X desc: %s" % (
            self.idx, self.object, self.name, self.type, self.needdo, self.id, self.coindition, self.type2,
            self.fubenid, self.mainflag, self.desc))


class ExGuoToMenZuoBiao(Structure):
    _fields_ = [
        ("x", c_int32),
        ("y", c_int32),

        ("w", c_int32),
        ("h", c_int32),

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


class DixingObj(Structure):
    _fields_ = [
        ("x", c_int32),
        ("y", c_int32),
        ("flag", c_uint32),
    ]

    def __str__(self):
        return (
                "(%d, %d) %d" % (
            self.x, self.y, self.flag))


class ObstacleObj(Structure):
    _fields_ = [
        ("x", c_int32),
        ("y", c_int32),
        ("w", c_int32),
        ("h", c_int32),
        ("flag", c_uint32),
        ("hp", c_int32),
        ("code", c_uint32)
    ]

    def __str__(self):
        return (
                "(%d, %d) %d %d %d" % (
            self.x, self.y, self.w, self.h, self.flag))

    def CanBeAttack(self):
        if self.code in [109006910, 109006911, 226, 228, 19134, 19135, 18020, 109000583, 109000576, 57522, 109006963,
                         109006964, 230, 52811, 52829, 52830, 52821, 52815, 52814, 52820,
                         11302, 11301, 11300, 11326, 11327, 11328, 11329, 11330, 11257, 11329,
                         15241, 15243, 48404, 52838, 52836, 52837, 52835, 52840, 52827, 52828, 52853,
                         52834, 52833, 52840, 52842, 52841, 52825, 52826, 227]:
            return False

        if self.code in [109007006]:
            return True

        if self.hp > 0 and self.flag in [1, 2]:
            return True

        return False


class SceneInfo(Structure):
    _fields_ = [
        ("w", c_int32),
        ("h", c_int32),
        ("len_c", c_int32),
        ("len_extra_78", c_int32),
    ]

    def __str__(self):
        return (
                "%d, %d , len_c: %d len_extra_78: %d" % (
            self.w, self.h, self.len_c, self.len_extra_78))


class SelectObj(Structure):
    _fields_ = [
        ("obj", c_uint32),
        ("level", c_uint32),
        ("name", c_wchar * 100),
    ]

    def __str__(self):
        return (
                "对象: 0x%08X 名字: %s 等级: %d " % (
            self.obj, self.name, self.level))


class CurSelectIdx(Structure):
    _fields_ = [
        ("menidx", c_uint32),
        ("mapidx", c_uint32),
    ]

    def __str__(self):
        return ("选中角色下标: %d 选中地图下标: %d" % (self.menidx, self.mapidx))


class Xingyunxing(Structure):
    _fields_ = [
        ("num", c_uint32)
    ]

    def __str__(self):
        return ("幸运星数量: %d " % (self.num))


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

lib.ExGetMapBuff.argtypes = [POINTER(POINTER(MapObj)), POINTER(c_int)]

lib.ExGetMapYinghuo.argtypes = [POINTER(POINTER(MapObj)), POINTER(c_int)]

lib.ExGetMapObstacle.argtypes = [POINTER(POINTER(MapObj)), POINTER(c_int)]

lib.ExGetBagObj.argtypes = [POINTER(POINTER(BagObj)), POINTER(c_int)]

lib.ExGetBagEquipObj.argtypes = [POINTER(POINTER(BagObj)), POINTER(c_int)]

lib.ExGetGetEquipObj.argtypes = [POINTER(POINTER(BagObj)), POINTER(c_int)]

lib.ExGetSkillObj.argtypes = [POINTER(POINTER(SkillObj)), POINTER(c_int)]

lib.ExGetAllSkillObj.argtypes = [POINTER(POINTER(SkillObj)), POINTER(c_int)]

lib.ExGetTaskObj.argtypes = [POINTER(POINTER(TaskObj)), POINTER(c_int)]

lib.ExGetAccptedTaskObj.argtypes = [POINTER(POINTER(AcceptedTaskObj)), POINTER(c_int)]

lib.ExNextDoor.argtypes = [POINTER(ExGuoToMenZuoBiao)]

lib.ExGetDixingObjTree.argtypes = [POINTER(POINTER(DixingObj)), POINTER(c_int)]

lib.ExGetDixingObjVector.argtypes = [POINTER(POINTER(DixingObj)), POINTER(c_int)]

lib.ExGetDixingObjExtra.argtypes = [POINTER(POINTER(DixingObj)), POINTER(c_int)]

lib.ExGetObstacleVector.argtypes = [POINTER(POINTER(ObstacleObj)), POINTER(c_int)]

lib.ExGetSceneInfo.argtypes = [POINTER(SceneInfo)]

lib.ExGetSelectObj.argtypes = [POINTER(POINTER(SelectObj)), POINTER(c_int)]

lib.ExGetCurSelectIdx.argtypes = [POINTER(CurSelectIdx)]

lib.ExGetXingyunxing.argtypes = [POINTER(Xingyunxing)]

lib.ExXiGuai.argtypes = []

lib.ExXiWu.argtypes = []

lib.ExZuobiaoyidong.argtypes = [c_float, c_float, c_float]

lib.ExAutoshuntu.argtypes = []

lib.Free.argtypes = [c_void_p]

# === enum

# 类型
MAN = 0x111  # 人
MONSTER = 0x211  # 怪物
GOOD = 0x121  # 物品
BUILD = 0x21  # 建筑

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


# 八方向力的分解
QuardantMap = {
    Quardant.ZUO: [Quardant.ZUO],
    Quardant.YOU: [Quardant.YOU],
    Quardant.SHANG: [Quardant.SHANG],
    Quardant.XIA: [Quardant.XIA],
    Quardant.ZUOSHANG: [Quardant.ZUO, Quardant.SHANG],
    Quardant.YOUSHANG: [Quardant.YOU, Quardant.SHANG],
    Quardant.ZUOXIA: [Quardant.ZUO, Quardant.XIA],
    Quardant.YOUXIA: [Quardant.YOU, Quardant.XIA],
}

# 大矩阵
MOVE_BIG_V_WIDTH = 40 / 2
MOVE_BIG_H_WIDTH = 40 / 2

# 误差
MOVE_SMALL_V_WIDTH = 20 / 2
MOVE_SMALL_H_WIDTH = 20 / 2

# 大小矩阵
BIG_RENT = 1
SMALL_RENT = 2

# 慢走矩形
MANZOU_V_WIDTH = 150 / 2
MANZOU_H_WIDTH = 1000 / 2

# 拾取矩形
PICKUP_V_WIDTH = 45 / 2
PICKUP_H_WIDTH = 45 / 2

# BUFF拾取矩形
BUFF_V_WIDTH = 20 / 2
BUFF_H_WIDTH = 20 / 2

# 怪物在太远的距离,先捡物品
PICK_DISTANCE = 200

# 普通攻击矩形
ATTACK_V_WIDTH = 160 / 2
ATTACK_H_WIDTH = 40 / 2

# 攻击太靠近的垂直宽度
ATTACK_TOO_CLOSE_V_WIDTH = 1.0 / 2

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


# 坐标位置
def QuardrantWithOutRent(x2, y2, chuizhikuandu, shuipingkuandu):
    # 同一个垂直位置
    if abs(x2) <= chuizhikuandu:
        if y2 > 0:
            return Quardant.XIA
        else:
            return Quardant.SHANG

    # 同一个水平位置
    if abs(y2) <= shuipingkuandu:
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


# 判断两个位置是否靠近
def IsClosedTo(x1, y1, x2, y2, rang=None):
    judge = MOVE_SMALL_V_WIDTH

    if rang is not None:
        judge = rang

    newx2, newy2 = x2 - x1, y2 - y1
    return abs(newx2) < judge and abs(newy2) < judge


# 象限 (x1,y1,x2,y2) 是左上角开始算的坐标系
def GetQuadrant(x1, y1, x2, y2):
    # 转换成以x1, y1为坐标起点的坐标系
    newx2, newy2 = x2 - x1, y2 - y1
    if abs(newx2) < MOVE_BIG_V_WIDTH and abs(newy2) < MOVE_BIG_H_WIDTH:
        # 在中间的小矩阵
        return QuardrantWithOutRent(newx2, newy2, 1, 1), SMALL_RENT
    return QuardrantWithOutRent(newx2, newy2, MOVE_BIG_V_WIDTH, MOVE_BIG_H_WIDTH), BIG_RENT


# 是否在捡取范围
def CanbePickup(x1, y1, x2, y2):
    V_WIDTH = abs(x2 - x1)
    H_WIDTH = abs(y2 - y1)
    return V_WIDTH < PICKUP_V_WIDTH and H_WIDTH < PICKUP_H_WIDTH


# 是否在捡取buff范围内
def CanbeGetBuff(x1, y1, x2, y2):
    V_WIDTH = abs(x2 - x1)
    H_WIDTH = abs(y2 - y1)
    return V_WIDTH < BUFF_V_WIDTH and H_WIDTH < BUFF_H_WIDTH


# 是否在慢走范围内
def WithInManzou(x1, y1, x2, y2):
    V_WIDTH = abs(x2 - x1)
    H_WIDTH = abs(y2 - y1)
    return V_WIDTH < MANZOU_V_WIDTH and H_WIDTH < MANZOU_H_WIDTH


# 是否在范围内
def WithInRange(x1, y1, x2, y2, range):
    return distance(x1, y1, x2, y2) < range


# 获取对象在右边还是左边
def GetFangxiang(x1, x2):
    return RIGHT if x2 - x1 > 0 else LEFT


# === help dll 基础
def GameApiInit():
    if lib.Init():
        logger.info("Init helpdll-xxiii.dll ok")
        return True
    else:
        logger.info("Init helpdll-xxiii.dll err, 驱动没有加载成功. 尝试加载")

        os.system("start /wait cmd /c %s" % (GetDriverStartFile()))

        if lib.Init():
            logger.info("Init helpdll-xxiii.dll ok")
            return True
        else:
            logger.info("Init helpdll-xxiii.dll err, 驱动没有加载成功.")
            return False


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


# 获取buff
def GetBuff():
    objs = POINTER(MapObj)()
    count = c_int(0)
    lib.ExGetMapBuff(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst = []
    for i in range(count.value):
        outlst.append(copy.deepcopy(objs[i]))
    return outlst


# 获取营火
def GetYinghuo():
    objs = POINTER(MapObj)()
    count = c_int(0)
    lib.ExGetMapYinghuo(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst = []
    for i in range(count.value):
        outlst.append(copy.deepcopy(objs[i]))
    return outlst


# 获取障碍物
def GetMapObstacle():
    objs = POINTER(MapObj)()
    count = c_int(0)
    lib.ExGetMapObstacle(pointer(objs), pointer(count))
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


# 背包装备数组
def GetBagEquipObj():
    objs = POINTER(BagObj)()
    count = c_int(0)
    lib.ExGetBagEquipObj(pointer(objs), pointer(count))
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


# 所有技能数组
def GetAllSkillObj():
    objs = POINTER(SkillObj)()
    count = c_int(0)
    lib.ExGetAllSkillObj(pointer(objs), pointer(count))
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


# 任务数组(已接受)
def GetAccptedTaskObj():
    objs = POINTER(AcceptedTaskObj)()
    count = c_int(0)
    lib.ExGetAccptedTaskObj(pointer(objs), pointer(count))
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


# 地形二叉树 + 地形数组 + 扩展数组 + 障碍数组 + 宽高
def GetSeceneInfo():
    objs = POINTER(DixingObj)()
    count = c_int(0)
    lib.ExGetDixingObjTree(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst1 = []
    for i in range(count.value):
        outlst1.append(copy.deepcopy(objs[i]))

    objs = POINTER(DixingObj)()
    count = c_int(0)
    lib.ExGetDixingObjVector(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst2 = []
    for i in range(count.value):
        outlst2.append(copy.deepcopy(objs[i]))

    objs = POINTER(DixingObj)()
    count = c_int(0)
    lib.ExGetDixingObjExtra(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst3 = []
    for i in range(count.value):
        outlst3.append(copy.deepcopy(objs[i]))

    objs = POINTER(ObstacleObj)()
    count = c_int(0)
    lib.ExGetObstacleVector(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst4 = []
    for i in range(count.value):
        outlst4.append(copy.deepcopy(objs[i]))

    sceneinfo = SceneInfo()
    lib.ExGetSceneInfo(pointer(sceneinfo))
    return outlst1, outlst2, outlst3, outlst4, sceneinfo


# 单独获取障碍数组
def GetObstacle():
    objs = POINTER(ObstacleObj)()
    count = c_int(0)
    lib.ExGetObstacleVector(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst = []
    for i in range(count.value):
        outlst.append(copy.deepcopy(objs[i]))
    return outlst


# 获取角色列表
def GetSelectObj():
    objs = POINTER(SelectObj)()
    count = c_int(0)
    lib.ExGetSelectObj(pointer(objs), pointer(count))
    defer(lambda: (lib.Free(objs)))
    outlst = []
    for i in range(count.value):
        outlst.append(copy.deepcopy(objs[i]))
    return outlst


# 获取选中下标
def GetCurSelectIdx():
    curselectIdx = CurSelectIdx()
    lib.ExGetCurSelectIdx(pointer(curselectIdx))
    return curselectIdx


# 获取幸运星数量(要打开物品租聘)
def GetXingyunxing():
    xingyunxing = Xingyunxing()
    lib.ExGetXingyunxing(pointer(xingyunxing))
    xingyunxing.num = 100  # TODO 更新了,不好逆向TMD
    return xingyunxing


# 吸怪
def Xiguai():
    lib.ExXiGuai()


# 吸物
def XiWu():
    lib.ExXiWu()


# 坐标移动
def Zuobiaoyidong(x, y, z):
    lib.ExZuobiaoyidong(c_float(x), c_float(y), c_float(z))


# 自动顺图
def Autoshuntu():
    lib.ExAutoshuntu()


# === 调试打印
def PrintMenInfo():
    menInfo = GetMenInfo()
    print("[人物信息]")
    print(menInfo)
    print("===========")


def PrintMapInfo():
    print("[地图信息]")
    mapInfo = GetMapInfo()
    print(mapInfo)
    print("===========")


def PrintMapObj():
    print("[地图对象]")
    outlst = GetMapObj()
    for obj in outlst:
        print(obj)
    print("===========")


def PrintBagObj():
    print("[背包对象]")
    outlst = GetBagObj()
    for obj in outlst:
        print(obj)
    print("===========")


def PrintBagEquipObj():
    print("[背包装备对象]")
    outlst = GetBagEquipObj()
    for obj in outlst:
        print(obj)
    print("===========")


def PrintEquipObj():
    print("[装备对象]")
    outlst = GetEquipObj()
    for obj in outlst:
        print(obj)
    print("===========")


def PrintSkillObj():
    print("[技能对象]")
    outlst = GetSkillObj()
    for obj in outlst:
        print(obj)
    print("===========")


def PrintAllSkillObj():
    print("[所有技能对象]")
    outlst = GetAllSkillObj()
    for obj in outlst:
        print(obj)
    print("===========")


def PrintTaskObj():
    print("[任务对象]")
    outlst = GetTaskObj()
    for obj in outlst:
        try:
            print(obj)
        except Exception as e:
            logger.warning(e)

    print("===========")


def PrintAccpetedTaskObj():
    print("[已接受任务对象]")
    outlst = GetAccptedTaskObj()
    for obj in outlst:
        print(obj)
    print("===========")


def PrintNextMen():
    print("[下一个门位置]")
    menzuobiao = GetNextDoor()
    print("下一个门坐标: %s" % menzuobiao)
    print("===========")


def PrintSceneInfo():
    print("[场景信息]")

    dixinglst, dixingvec, dixingextra, obstacles, wh = GetSeceneInfo()

    print("地形链表")
    for v in dixinglst:
        print(v)

    print("地形数组")
    for v in dixingvec:
        print(v)

    print("地形数组额外")
    for v in dixingextra:
        print(v)

    print("障碍")
    for v in obstacles:
        print(v)

    print("场景宽高")
    print(wh)

    print("===========")


def PrintWH():
    print("[场景宽高]")
    dixinglst, dixingvec, dixingextra, obstacles, wh = GetSeceneInfo()
    print("场景宽高 %s" % wh)
    print("===========")


def PrintSelectObj():
    print("[角色列表对象]")
    outlst = GetSelectObj()
    for obj in outlst:
        print(obj)
    print("===========")


def PrintSelectIdx():
    print("[选择下标信息]")
    selectidx = GetCurSelectIdx()
    print(selectidx)
    print("===========")


def PrintXingyunxing():
    print("[幸运星信息]")
    xingyunxing = GetXingyunxing()
    print(xingyunxing)
    print("===========")


# === 2次包装


# 有怪物
def HaveMonsters():
    monsters = GetMonstersWrap()
    return len(monsters) > 0


# 怪物太远了(boss房间只考虑boss)
def ClosestMonsterIsToofar():
    monster = NearestMonsterWrap()
    if monster is None:
        return True
    men = GetMenInfo()
    if distance(men.x, men.y, monster.x, monster.y) > PICK_DISTANCE:
        return True
    return False


# 指定怪物太远了
def SpecifyMonsterIsToofar(monster):
    men = GetMenInfo()
    if distance(men.x, men.y, monster.x, monster.y) > PICK_DISTANCE:
        return True
    return False


# 最近怪物对象 (极昼先攻击除开多尼尔的怪物)
def NearestMonster():
    menInfo = GetMenInfo()
    monsters = GetMonstersWrap()
    if len(monsters) < 1:
        return None
    mapinfo = GetMapInfo()
    if "极昼" in mapinfo.name:
        if any(mon.name == "多尼尔" for mon in monsters):
            if any(mon.name != "多尼尔" for mon in monsters):
                monsters = filter(lambda mon: mon.name != "多尼尔", monsters)
                monsters = list(monsters)
    elif "暗黑雷鸣废墟" in mapinfo.name:
        pass
    elif "利库天井" in mapinfo.name:
        obstacles = GetMapObstacle()
        obstacles = filter(lambda ob: "哥布林投石车" in ob.name, obstacles)
        obstacles = list(obstacles)
        if len(obstacles) > 0:
            monsters = obstacles

    return min(monsters, key=lambda mon: distance(mon.x, mon.y, menInfo.x, menInfo.y))


# 更新怪物对象信息
def UpdateMonsterInfo(monster):
    objs = GetMonstersWrap()
    for obj in objs:
        if obj.object == monster.object and obj.hp > 0:
            return obj
    return None


# 获取boss对象
def GetBossObj():
    monsters = GetMonstersWrap()
    if len(monsters) < 1:
        return None

    objs = filter(lambda mon: "领主" in mon.name and "dummy" not in mon.name and
                              "领主 - 领主" not in mon.name and
                              "通关用" not in mon.name, monsters)
    objs = list(objs)

    if len(objs) < 1:
        return None
    else:
        # 如果有黄金巨人直接返回黄金巨人
        doubleboss = filter(lambda obj: "黄金巨人" in obj.name, objs)
        doubleboss = list(doubleboss)

        if len(doubleboss) > 0:
            return doubleboss[0]

        boss = objs[0]

        meninfo = GetMenInfo()
        mapinfo = GetMapInfo()
        if meninfo.level < 51 and "斯卡萨之巢" in mapinfo.name:
            if "领主 - 冰龙斯卡萨" == boss.name:
                if boss.hp < 800000:
                    boss.x = 1254
                    boss.y = 745
            return boss

        return boss


# 最近怪物对象wrap,boss房间boss,普通房间普通
def NearestMonsterWrap():
    if IsCurrentInBossFangjian():
        mapinfo = GetMapInfo()

        if "暗黑雷鸣废墟" in mapinfo.name:
            # 暗黑雷鸣废墟有转职任务. 先打小怪,再打boss
            obj = NearestMonster()
        elif "暴君的祭坛" in mapinfo.name:
            # 暴君的祭坛boss可能不及时出现. 给到最近的对象
            obj = NearestMonster()
        elif "绝望的棋局" in mapinfo.name:
            # 绝望的棋局需要打败小兵
            obj = NearestMonster()
        else:

            # 其余都是找boss, boss没有最近的对象
            obj = GetBossObj()
            if obj is None:
                obj = NearestMonster()
    else:
        obj = NearestMonster()

    return obj


# 获取怪物的包装
def GetMonstersWrap():
    monsters = GetMonsters()
    if IsLockedHp():
        monsters = filter(lambda mon: mon.hp > 1, monsters)
        monsters = list(monsters)

    return monsters

# 斯卡迪女王的印章
UnuseFilterStr = u"克尔顿的印章|撒勒的印章|达人HP药剂|达人MP药剂|专家MP药剂|专家HP药剂|熟练MP药剂|熟练HP药剂|血滴石|黑曜石|紫玛瑙|金刚石|海蓝宝石|月饼硬币|飞盘 2|暗黑倾向药剂|命运硬币|肉干|砂砾|天空树果实|燃烧瓶|军用回旋镖|裂空镖|甜瓜|飞镖|轰雷树果实|越桔|神圣葡萄酒|轰爆弹|爆弹|燃烧瓶|精灵香精|魔力之花|石头|苎麻花叶|怒海霸主银币|解密礼盒|无尽的永恒|风化的碎骨|破旧的皮革|最下级砥石|最下级硬化剂|生锈的铁片|碎布片|回旋镖|天界珍珠|朗姆酒|飞盘|魔力之花|卡勒特指令书|入门HP药剂|入门MP药剂|普通HP药剂|普通MP药剂|飞盘2|邪恶药剂|圣杯|肉干"

UnuseFilter = UnuseFilterStr.split("|")


# 获取地面物品的wrap,过滤垃圾
def GetGoodsWrap():
    goods = GetGoods()
    goods = filter(lambda good: good.name not in UnuseFilter, goods)
    goods = list(goods)
    return goods


# 获取地面物品的wrap, 过滤掉不能捡取的s
def GetGoodsCanbePickup(player):
    goods = GetGoodsWrap()
    # if player.d is not None and player.ob is not None:
    #     for good in goods:
    #         if player.ob.TouchedAnything((int(good.x) // 10, int(good.y) // 10)):
    #             goods.remove(good)
    return goods


# 地面有物品
def HaveGoods(player):
    goods = GetGoodsCanbePickup(player)
    return len(goods) > 0


# 最近物品对象
def NearestGood(player):
    menInfo = GetMenInfo()
    goods = GetGoodsCanbePickup(player)
    if len(goods) < 1:
        return None
    return min(goods, key=lambda good: distance(good.x, good.y, menInfo.x, menInfo.y))


# 负重空间够
def IsFuzhongGou():
    meninfo = GetMenInfo()

    if meninfo.fuzhongmax > 0.0:
        return meninfo.fuzhongcur / meninfo.fuzhongmax <= 0.95

    return True


# 获取buf 二次包装
def GetBuffWrap():
    return []

    # mapinfo = GetMapInfo()
    # if mapinfo.name == "格拉卡" and mapinfo.curx == 1 and mapinfo.cury == 0:
    #     return []
    # return GetBuff()


# 地面有buff
def HaveBuffs():
    buffs = GetBuffWrap()
    return len(buffs) > 0


# 最近buf对象
def NearestBuf():
    menInfo = GetMenInfo()
    buffs = GetBuffWrap()
    if len(buffs) < 1:
        return None
    return min(buffs, key=lambda buff: distance(buff.x, buff.y, menInfo.x, menInfo.y))


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


# 获取门是否开的信息
def IsNextDoorOpen():
    mapinfo = GetMapInfo()
    return mapinfo.kaimen


# 是否已经通过
def IsFuBenPass():
    # 不在boss房间肯定没通关呀
    if not IsCurrentInBossFangjian():
        return False

    # 出现营火算肯定通过
    if len(GetYinghuo()) > 0:
        return True

    # 没有怪物就算通过(没有营火前提前判断)
    # if NearestMonsterWrap() is None:
    #     return True

    return False


# 是否当前处在boss房间
def IsCurrentInBossFangjian():
    mapinfo = GetMapInfo()
    if mapinfo.curx == mapinfo.bossx and \
            mapinfo.cury == mapinfo.bossy:
        return True
    return False


# 多尼尔难以攻击
def FuckDuonier():
    mons = GetMonstersWrap()
    excludeDuonier = filter(lambda mon: "多尼尔" not in mon.name, mons)
    excludeDuonier = list(excludeDuonier)
    if len(excludeDuonier) > 0:
        return False

    includeDuonier = filter(lambda mon: "多尼尔" in mon.name, mons)
    includeDuonier = list(includeDuonier)
    if len(includeDuonier) < 1:
        return False

    for duonier in includeDuonier:
        if duonier.z < 80:
            return False

    return True


# 1. 是否在极昼 2. 有多尼尔并且没有其他怪物了 3. 任何一个多尼尔的太高打不到
def IsJiZhouSpecifyState():
    mapinfo = GetMapInfo()
    return "极昼" in mapinfo.name and FuckDuonier()


# 获取极昼的肉瘤
def GetouliuObj():
    mapinfo = GetMapInfo()
    if not "极昼" in mapinfo.name:
        return False
    mapobj = GetMapObj()
    for obj in mapobj:
        if obj.type == BUILD and obj.name == "天帷巨兽的肉瘤":
            return obj
    return None


# 获取当前房间的x,y
def GetCurrentMapXy():
    mapinfo = GetMapInfo()
    return mapinfo.curx, mapinfo.cury


# 是否在图内
def IsManInMap():
    meninfo = GetMenInfo()
    return meninfo.state == TUNEI


# 是否在选图
def IsManInSelectMap():
    meninfo = GetMenInfo()
    return meninfo.state == XUANTU


# 是否在城镇
def IsManInChengzhen():
    meninfo = GetMenInfo()
    return meninfo.state == CHENZHEN


# 是否在疾跑
def IsManJipao():
    meninfo = GetMenInfo()
    return meninfo.jipao


# 是否死掉了
def IsMenDead():
    meninfo = GetMenInfo()
    return meninfo.hp <= 1


# 冰霜幽暗密林第一个门有冰柱挡住
def GetNextDoorWrap():
    mapinfo = GetMapInfo()
    if "冰霜幽暗密林" in mapinfo.name and mapinfo.curx == 0 and mapinfo.cury == 1:
        return mapinfo.top
    if "冰霜幽暗密林" in mapinfo.name and mapinfo.curx == 0 and mapinfo.cury == 0:
        return mapinfo.right
    return GetNextDoor()


# 获取当前地图idx
def GetCurmapXy():
    if IsManInMap():
        mapinfo = GetMapInfo()
        return mapinfo.curx, mapinfo.cury
    return 0, 0


# 以下地图 弹出窗口也可以移动
WindowTopFilter = [
    ("格拉卡", 2, 0),
    ("烈焰格拉卡", 0, 1),
    ("烈焰格拉卡", 1, 1),
    ("暗黑雷鸣废墟", 0, 0),
    ("暗黑雷鸣废墟", 1, 0),
    ("第二脊椎", 1, 2),
    ("第二脊椎", 2, 2),
    ("黑暗玄廊", 3, 2),
    ("悬空城", 1, 3),
    ("根特北门", 0, 1),
]


# 是否有空格键确认的窗口置顶
def IsWindowTop():
    meninfo = GetMenInfo()
    if meninfo.tanchu:
        # 某些地图不管
        mapinfo = GetMapInfo()
        for ele in WindowTopFilter:
            if ele[0] in mapinfo.name and mapinfo.curx == ele[1] and mapinfo.cury == ele[2]:
                PressKey(VK_CODE["spacebar"])  # 假装按下
                return False
    return meninfo.tanchu


# 是否esc窗口置顶
def IsEscTop():
    meninfo = GetMenInfo()
    return meninfo.esc


# 当前选中的地图id
def CurSelectId():
    selectidx = GetCurSelectIdx()
    return selectidx.mapidx


# 获取剩余疲劳
def GetRemaindPilao():
    meninfo = GetMenInfo()
    return meninfo.maxpilao - meninfo.curpilao


# 疲劳是否有
def HavePilao():
    return GetRemaindPilao() > 0


# 蘑菇庄园这个奇葩地图
def IsShitmoGu():
    meninfo = GetMenInfo()
    if 50 < meninfo.level < 57:
        mapinfo = GetMapInfo()
        if "蘑菇庄园" in mapinfo.name:
            if mapinfo.curx == 0 and mapinfo.cury == 4:
                return True

    return False


# 背包是否有装备
def BagHasFenjieEquip():
    equips = GetBagEquipObj()
    equips = filter(lambda equip: equip.color in [0, 1, 2], equips)
    equips = list(equips)
    return len(equips) > 0


# 背包无色数量
def BagWuseNum():
    objs = GetBagObj()
    for obj in objs:
        if obj.name == "无色小晶块":
            return obj.num
    return 0


# 技能等级不是0或1, 学会了
def IsSkillLearned(skillname):
    skills = GetAllSkillObj()
    for skill in skills:
        if skill.name == skillname:
            if skill.level in [0, 1]:
                return False
            else:
                return True

    return False


# 是否选中了第一个目标
def IsFirstSelect():
    return GetCurSelectIdx().menidx == 0


# 是否选中了最后一个目标
def IsLastSelect():
    objs = GetSelectObj()
    return GetCurSelectIdx().menidx == (len(objs) - 1)


# 目标职业是否支持
def IsDestSupport(zhiye):
    if zhiye in ["魔枪士", "圣职者", "守护者", "格斗家", "鬼剑士", "枪剑士"]:
        return True
    if zhiye in ["暗枪士", "狂怒恶鬼", "幽影夜神",
                 "诱魔者", "断罪者", "救世者",
                 "帕拉丁", "曙光", "破晓女神",
                 "气功师", "百花缭乱", "念帝",
                 "剑影", "夜刀神", "夜见罗刹",
                 "源能专家", "源力掌控者", "未来开拓者"]:
        return True
    return False


# 当前是否支持职业
def IsCurrentSupport():
    meninfo = GetMenInfo()
    return IsDestSupport(meninfo.zhuanzhihou)


# 当前是否在训练场景内
def IsCurrentInTrain():
    meninfo = GetMenInfo()
    if meninfo.level == 1:
        mapinfo = GetMapInfo()
        if "洛兰之森" not in mapinfo.name:
            return True
    return False


# 是否制裁
def IsZhicai():
    meninfo = GetMenInfo()
    return meninfo.zhicai == 4


# 技能对应的按键
idxkeymap = {
    0: VK_CODE['a'], 1: VK_CODE['s'], 2: VK_CODE['d'], 3: VK_CODE['f'], 4: VK_CODE['g'], 5: VK_CODE['h'],
    6: VK_CODE['q'], 7: VK_CODE['w'], 8: VK_CODE['e'], 9: VK_CODE['r'], 10: VK_CODE['t'], 11: VK_CODE['y'],
}


# 技能种类
class SkillType(Enum):
    Yidong = 1,
    Gongji = 2,
    Buff = 3


# 单个技能属性包装
class SkillData:
    def __init__(self, **kw):
        # 技能种类
        self.type = None

        # 攻击垂直宽度
        self.v_w = ATTACK_V_WIDTH

        # 攻击水平宽度
        self.h_w = ATTACK_H_WIDTH

        # 攻击太靠近的垂直宽度
        self.too_close_v_w = ATTACK_TOO_CLOSE_V_WIDTH

        # 释放级别. 越高级的越先释放
        self.level = 0

        # 按键延迟时间
        self.delaytime = 0.1

        # 事后时间
        self.afterdelay = 0.15

        # 事后按键(某些buff,上下左右选择)
        self.thenpress = None

        # 时候重复按下本次按键(4姨,阿修罗) 蓄力后,再次释放
        self.doublepress = False

        # 是否锁为一血
        self.lockhp = False

        for k, w in kw.items():
            setattr(self, k, w)


# 是否锁血
gHplocked = False


# 是否锁血了 (某些技能会让怪物锁1血, 那时候不要遍历出来)
def IsLockedHp():
    return gHplocked


# 锁血
def LockHp():
    global gHplocked
    gHplocked = True


# 解除锁血
def UnLockHp():
    global gHplocked
    gHplocked = False


# 单个技能包装
class Skill:

    def __init__(self, **kw):
        # 是否存在
        self.exist = False
        # 名称
        self.name = ""
        # 快捷键
        self.key = None
        # 是否能使用
        self.canbeused = False
        # python对技能的配置
        self.skilldata = SkillData(type=SkillType.Gongji)
        # 是否是普通攻击
        self.issimpleattack = False

        for k, w in kw.items():
            setattr(self, k, w)

    # 是否垂直宽度太靠近致使攻击不能命中
    def IsV_WTOOClose(self, menx, objx):
        if self.skilldata.too_close_v_w < 1.0:
            return False

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
        return self.canbeused

    # 设置按键
    def SetKey(self, idx):
        self.key = idxkeymap[idx]

    # 初始化技能在内存中的设置
    def Init(self):
        if self.name in skillSettingMap:
            self.skilldata = skillSettingMap[self.name]
        else:
            self.skilldata = SkillData(type=SkillType.Gongji)

    # 使用
    def Use(self):
        logger.info(" %s delay %f afterdelay %f doublepress %d" % (
            self.name, self.skilldata.delaytime, self.skilldata.afterdelay, self.skilldata.doublepress))

        PressSkill(self.key, self.skilldata.delaytime, self.skilldata.afterdelay, self.skilldata.thenpress,
                   self.skilldata.doublepress, self.issimpleattack)

        if self.skilldata.lockhp:
            LockHp()


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
            self.skilllst[obj.idx].name = obj.name
            self.skilllst[obj.idx].SetKey(obj.idx)
            self.skilllst[obj.idx].canbeused = obj.canbeused
            self.skilllst[obj.idx].Init()

        # 先强制刷新一波全部不存在
        for skillobj in self.skilllst:
            skillobj.exist = False

        # 再刷新的列表,改变为存在
        for obj in objs:
            self.skilllst[obj.idx].exist = True

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


# 初始化技能配置. 因为内存中读取不到
skillSettingMap = {

    # 通用
    "远古记忆": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),

    # 移动
    "后跳": SkillData(type=SkillType.Yidong),

    # 阿修罗

    # buff
    "波动刻印": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),
    "杀意波动": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),

    # 近
    "上挑": SkillData(type=SkillType.Gongji),
    "鬼斩": SkillData(type=SkillType.Gongji),
    "裂波斩": SkillData(type=SkillType.Gongji, afterdelay=0.3),
    "鬼连斩": SkillData(type=SkillType.Gongji),
    "波动爆发": SkillData(type=SkillType.Gongji),
    "无双波": SkillData(type=SkillType.Gongji),

    # 远
    "地裂 · 波动剑": SkillData(type=SkillType.Gongji, v_w=200 / 2, h_w=40 / 2),
    "鬼印珠": SkillData(type=SkillType.Gongji, v_w=400 / 2, h_w=40 / 2, too_close_v_w=140 / 2, delaytime=0.5),
    "邪光斩": SkillData(type=SkillType.Gongji, v_w=400 / 2, h_w=40 / 2, delaytime=0.6),
    "冰刃 · 波动剑": SkillData(type=SkillType.Gongji, v_w=400 / 2, h_w=40 / 2),
    "爆炎 · 波动剑": SkillData(type=SkillType.Gongji, v_w=400 / 2, h_w=40 / 2),

    # 神龙天女
    "神谕之祈愿": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),

    # 光枪
    "能量萃取": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),

    # 暗枪
    "黑暗化身": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),
    "连锁侵蚀": SkillData(type=SkillType.Gongji, delaytime=0.2, afterdelay=0.4, lockhp=True),
    "暗蚀螺旋枪": SkillData(type=SkillType.Gongji, delaytime=0.2, afterdelay=0.4, lockhp=True),
    "坠蚀之雨": SkillData(type=SkillType.Gongji, delaytime=0.2, afterdelay=0.4, v_w=400 / 2, h_w=40 / 2,
                      too_close_v_w=140 / 2),

    # 女光剑
    "五气朝元": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),

    # 女气功
    "光之兵刃": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),
    "烈日气息": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),
    "念兽 : 龙虎啸": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),
    "千莲怒放": SkillData(type=SkillType.Gongji, afterdelay=0.5, doublepress=True),

    # 男气功
    "念气流转": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),

    # 女散打
    "强拳": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),
    "霸体护甲": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),

    # 龙骑士
    "龙语召唤 : 阿斯特拉": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=1.2),
    "肉食主义": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.8),

    # 关羽
    "不灭战戟": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),

    # 赵云
    "无双枪术": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),

    # 四姨
    "七宗罪": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4, thenpress=VK_CODE["left_arrow"]),
    "贪婪之刺": SkillData(type=SkillType.Gongji, delaytime=0.2, afterdelay=0.4, lockhp=True),

    # 吸怪,蓄力
    "怠惰之息": SkillData(type=SkillType.Gongji, afterdelay=1.2, doublepress=True),

    # 剑影
    "双魂共鸣": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.8),
    "鬼步": SkillData(type=SkillType.Gongji, afterdelay=0.5, doublepress=True),

    # 帕拉丁
    "信仰之念": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),

    # 源能
    "源能应用": SkillData(type=SkillType.Buff, delaytime=0.2, afterdelay=0.4),
    "镭射源能枪": SkillData(type=SkillType.Gongji, v_w=400 / 2, h_w=40 / 2, ),
    "脉冲斩": SkillData(type=SkillType.Gongji, v_w=400 / 2, h_w=40 / 2, ),
}

# 普通攻击
simpleAttackSkill = Skill(exit=True, key=VK_CODE['x'], name="普通攻击", issimpleattack=True)
simpleAttackSkill.skilldata.delaytime = 1.0


# 清空当前
def Clear():
    PressKey(VK_CODE["esc"]), KongjianSleep()
    if GetMenInfo().esc:
        logger.info("关闭esc")
        PressKey(VK_CODE["esc"]), KongjianSleep()

    MouseMoveTo(0, 0), KongjianSleep()


# 不要频繁的clear
def SafeClear(player, t=10):
    if player.latestClear is None or time.time() - player.latestClear > t:
        Clear()
        player.latestClear = time.time()
    else:
        logger.warning("屏蔽频繁clear")


# 打开esc
def Openesc():
    PressKey(VK_CODE["esc"]), KongjianSleep()

    if not IsEscTop():
        logger.info("打开esc")
        PressKey(VK_CODE["esc"]), KongjianSleep()
    return IsEscTop()


# 读写速度测试
def SpeedTest():
    # logger.info("HaveGoods")
    # HaveGoods()
    # logger.info("HaveGoods")

    logger.info("HaveBuffs")
    HaveBuffs()
    logger.info("HaveBuffs")

    logger.info("NearestMonster")
    NearestMonster()
    logger.info("NearestMonster")

    logger.info("GetMapInfo")
    GetMapInfo()
    logger.info("GetMapInfo")

    logger.info("GetMenInfo")
    GetMenInfo()
    logger.info("GetMenInfo")


def main():
    InitLog()
    if not GameApiInit():
        sys.exit()
    FlushPid()

    # while True:
    #     time.sleep(1.0)s
    #     PrintMenInfo()

    PrintMenInfo()
    PrintMapInfo()
    PrintMapObj()
    PrintBagObj()
    PrintBagEquipObj()
    # print("无色: " + str(BagWuseNum()))
    PrintEquipObj()
    PrintSkillObj()
    # PrintAllSkillObj()
    PrintTaskObj()
    PrintAccpetedTaskObj()
    PrintNextMen()
    PrintWH()
    # PrintSelectObj()
    PrintSelectIdx()
    # PrintXingyunxing()

    # PrintSceneInfo() # 数据太多
    # SpeedTest() # 速度还可以

    # 变态功能
    # Xiguai()
    # XiWu()
    # Zuobiaoyidong(300, 200, 0)
    # Autoshuntu()

    print(IsCurrentInTrain())


if __name__ == "__main__":
    main()
