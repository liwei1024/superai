import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from ctypes import *

lib = CDLL("E:/win/reference/project/xxiii/x64/Release/helpdll-xxiii.dll", RTLD_GLOBAL)


class XY(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float)]


class OBJ(Structure):
    _fields_ = [
        ("object", c_int),
        ("type", c_int),
        ("zhenying", c_int),
        ("x", c_float),
        ("y", c_float),
        ("name", c_char * 64),
    ]

    def __str__(self):
        return "对象: %08X 类型: %04X 阵营: %04X  坐标:(%.0f,%.0f) 名称: %s" % \
               (self.object, self.type, self.zhenying, self.x, self.y, str(self.name))


class OBJArray(Structure):
    _fields_ = [
        ("count", c_int),
        ("obj", OBJ * 10),
    ]


lib.Init.argtypes = []
lib.Init.restype = c_bool

lib.GetManXY.argtypes = [POINTER(XY)]
lib.GetManXY.restype = c_bool

lib.GetObjArray.argtypes = []
lib.GetObjArray.restype = POINTER(OBJArray)

lib.FreeObjArray.argtypes = [POINTER(OBJArray)]


def main():
    if lib.Init():
        print("Init ok")
    else:
        print("Init err")

    xy = XY()

    lib.GetManXY(byref(xy))

    print("人物坐标: [{0},{1}]".format(xy.x, xy.y))

    objArray = lib.GetObjArray()

    array = cast(byref(objArray.obj), POINTER(OBJ * objArray.count)).contents

    print(array[1])
    # for val in array:
    #     print(val)

    lib.FreeObjArray(objArray)


if __name__ == "__main__":
    main()
