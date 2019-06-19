import copy
import sys
import os
from typing import List

from win32api import Sleep

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.defer import defer

from ctypes import *

lib = CDLL("E:/win/reference/project/xxiii/x64/Release/helpdll-xxiii.dll", RTLD_GLOBAL)


class XY(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float)]


class OBJ(Structure):
    _fields_ = [
        ("object", c_int32),
        ("type", c_int32),
        ("zhenying", c_int32),
        ("x", c_float),
        ("y", c_float),
        ("name", c_char * 60)
    ]

    def __str__(self):
        return "对象: 0x%08X 类型: 0x%X 阵营: 0x%X 名称: %s 坐标:(%.0f,%.0f) " % \
               (self.object & 0xffffffff, self.type, self.zhenying, self.name.decode("gbk"), self.x, self.y)


MANTYPE = 0x111
MONSTERTYPE = 0x211
GOODTYPE = 0x121

ENEMYHAWK = 0x64
OWNHAWK = 0x0

lib.Init.argtypes = []
lib.Init.restype = c_bool

lib.GetManXY.argtypes = [POINTER(XY)]
lib.GetObjArray.argtypes = [POINTER(POINTER(OBJ)), POINTER(c_int)]

lib.Free.argtypes = [c_void_p]


# 获取人物坐标
def GetManXY() -> (int, int):
    xy = XY()
    lib.GetManXY(pointer(xy))
    return int(xy.x), int(xy.y)


# 获取怪物列表
@defer
def GetMonsterLst(defer) -> List:
    objarray = POINTER(OBJ)()
    count = c_int(0)
    lib.GetObjArray(pointer(objarray), pointer(count))
    defer(lambda: (lib.Free(objarray)))

    outlst = []
    for i in range(count.value):
        if objarray[i].type == MONSTERTYPE:
            outlst.append(copy.deepcopy(objarray[i]))

    return outlst


# 获取所有对象列表
@defer
def GetAllLst(defer) -> List:
    objarray = POINTER(OBJ)()
    count = c_int(0)
    lib.GetObjArray(pointer(objarray), pointer(count))
    defer(lambda: (lib.Free(objarray)))

    outlst = []
    for i in range(count.value):
        outlst.append(copy.deepcopy(objarray[i]))

    return outlst


# 更新怪物对象
def GetMonster(obj):
    for mon in GetMonsterLst():
        if mon.object == obj.object:
            return mon
    return None


def GameApiInit() -> bool:
    return lib.Init()


def main():
    if lib.Init():
        print("Init helpdll-xxiii.dll ok")
    else:
        print("Init helpdll-xxiii.dll err")

    while True:
        Sleep(1000)

        xy = XY()
        lib.GetManXY(pointer(xy))
        print("人物坐标: [{0},{1}]".format(xy.x, xy.y))

        objarray = POINTER(OBJ)()
        count = c_int(0)
        lib.GetObjArray(pointer(objarray), pointer(count))
        for i in range(count.value):
            print(objarray[i])

        lib.Free(objarray)


if __name__ == "__main__":
    main()
