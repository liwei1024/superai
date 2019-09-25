import os
import sys
import time
from ctypes import CDLL, RTLD_GLOBAL

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))


# 底层依赖
def GetHelpdllLib():
    if os.path.exists("c:/win/superai/x64/Release/"):
        lib = CDLL("c:/win/superai/x64/Release/helpdll-xxiii.dll", RTLD_GLOBAL)
    else:
        lib = CDLL("d:/win/reference/project/xxiii/x64/Release/helpdll-xxiii.dll", RTLD_GLOBAL)
    return lib


# 启动启动脚本
def GetDriverStartFile():
    if os.path.exists("c:/win/superai/x64/Release/"):
        return "c:/win/superai/x64/Release/load.cmd"
    else:
        return "d:/win/reference/project/xxiii/x64/Release/load.cmd"


# 易键鼠dll
def GetYiLib():
    if os.path.exists("c:/win/superai/superai/dll/"):
        lib = CDLL("c:/win/superai/superai/dll/msdk.dll", RTLD_GLOBAL)
    else:
        lib = CDLL("d:/win/reference/project/superai/dll/msdk.dll", RTLD_GLOBAL)
    return lib


# 幽灵dll
def GetYoulingLib():
    if os.path.exists("c:/win/superai/superai/dll/"):
        lib = CDLL("c:/win/superai/superai/dll/kmllib64.dll", RTLD_GLOBAL)
    else:
        lib = CDLL("d:/win/reference/project/superai/dll/kmllib64.dll", RTLD_GLOBAL)
    return lib


# 图片资源
def GetImgDir():
    if os.path.exists("c:/win/superai/superimg/"):
        basedir = "c:/win/superai/superimg/"
    else:
        basedir = "d:/win/reference/project/superai/superimg/"
    return basedir


# 配置路径
def GetCfgPath():
    if os.path.exists("c:/win/superai/supercfg/"):
        settingdir = "c:/win/superai/supercfg/"
    else:
        settingdir = "d:/win/reference/project/superai/supercfg/"
    return settingdir


# 获取账户配置文件
def GetCfgFile():
    return os.path.join(GetCfgPath(), "accounts")


# 数据库路径
def GetDbDir():
    if os.path.exists("c:/win/superai/superdb/"):
        dbdir = "c:/win/superai/superdb/"
    else:
        dbdir = "d:/win/reference/project/superai/superdb/"
    return dbdir


# 数据库文件
def getDbFile():
    return os.path.join(GetDbDir(), "subnodedb.db")


# 验证码缓存路径
def GetvercodeDir():
    if os.path.exists("c:/win/superai/supervercode/"):
        d = "c:/win/superai/supervercode/"
    else:
        d = "d:/win/reference/project/superai/supervercode/"
    return d


# 游戏路径
def GameFileDir():
    if os.path.exists("c:/win/dnf"):
        gamedir = "c:/win/dnf/地下城与勇士/start/DNFchina.exe"
    else:
        gamedir = "d:/win/game/dnf/地下城与勇士/start/DNFchina.exe"
    return gamedir
