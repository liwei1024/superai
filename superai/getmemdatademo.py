import sys
import os

from win32api import Sleep

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

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


lib.Init.argtypes = []
lib.Init.restype = c_bool

lib.GetManXY.argtypes = [POINTER(XY)]
lib.GetObjArray.argtypes = [POINTER(POINTER(OBJ)), POINTER(c_int)]

lib.Free.argtypes = [c_void_p]


def main():
    if lib.Init():
        print("Init ok")
    else:
        print("Init err")

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
