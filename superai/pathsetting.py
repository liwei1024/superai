import os
import sys
import time
from ctypes import CDLL, RTLD_GLOBAL

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))


# 底层依赖
def GetHelpdllLib():
    if os.path.exists("c:/win/x64/Release/"):
        lib = CDLL("c:/win/x64/Release/helpdll-xxiii.dll", RTLD_GLOBAL)
    else:
        lib = CDLL("d:/win/reference/project/xxiii/x64/Release/helpdll-xxiii.dll", RTLD_GLOBAL)
    return lib


# 易键鼠dll
def GetYiLib():
    if os.path.exists("c:/win/superai/dll/"):
        lib = CDLL("c:/win/superai/dll/msdk.dll", RTLD_GLOBAL)
    else:
        lib = CDLL("d:/win/reference/project/superai/dll/msdk.dll", RTLD_GLOBAL)
    return lib


# 图片资源
def GetImgDir():
    if os.path.exists("c:/win/superimg/"):
        basedir = "c:/win/superimg/"
    else:
        basedir = "d:/win/studio/dxf/picture/superimg/"
    return basedir


# 配置路径
def GetCfgPath():
    if os.path.exists("c:/win/supercfg/"):
        settingdir = "c:/win/supercfg/"
    else:
        settingdir = "d:/win/studio/dxf/supercfg/"
    return settingdir


# 获取账户配置文件
def GetCfgFile():
    return os.path.join(GetCfgPath(), "accounts")


# 数据库路径
def GetDbDir():
    if os.path.exists("c:/win/superdb/"):
        dbdir = "c:/win/superdb/"
    else:
        dbdir = "d:/win/studio/dxf/superdb/"
    return dbdir


# 数据库文件
def getDbFile():
    return os.path.join(GetDbDir(), "subnodedb.db")
