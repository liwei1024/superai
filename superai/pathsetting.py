import configparser
import os
import sys
import time
from ctypes import CDLL, RTLD_GLOBAL

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)


runPath = os.path.split(sys.executable)[0]
runPath = os.path.split(runPath)[0]
xxxiiiPath = "d:/win/reference/project/xxiii"
superaiPath = "d:/win/reference/project/superai"


# 底层依赖
def GetHelpdllLib():
    if os.path.exists(os.path.join(runPath, "x64/Release/")):
        lib = CDLL(os.path.join(runPath, "x64/Release/helpdll-xxiii.dll"), RTLD_GLOBAL)
    else:
        lib = CDLL(os.path.join(xxxiiiPath, "x64/Release/helpdll-xxiii.dll"), RTLD_GLOBAL)

    logger.info(lib)
    return lib


# 启动启动脚本
def GetDriverStartFile():
    if os.path.exists(os.path.join(runPath, "x64/Release/")):
        p = os.path.join(runPath, "x64/Release/load.cmd")
    else:
        p = os.path.join(xxxiiiPath, "x64/Release/load.cmd")

    logger.info(p)
    return p

# 易键鼠dll
def GetYiLib():
    if os.path.exists(os.path.join(runPath, "superai/dll/")):
        lib = CDLL(os.path.join(runPath, "superai/dll/msdk.dll"), RTLD_GLOBAL)
    else:
        lib = CDLL(os.path.join(superaiPath, "dll/msdk.dll"), RTLD_GLOBAL)

    logger.info(lib)
    return lib


# 幽灵dll
def GetYoulingLib():
    if os.path.exists(os.path.join(runPath, "superai/dll/")):
        lib = CDLL(os.path.join(runPath, "superai/dll/kmllib64.dll"), RTLD_GLOBAL)
    else:
        lib = CDLL(os.path.join(superaiPath, "dll/kmllib64.dll"), RTLD_GLOBAL)

    logger.info(lib)
    return lib


# 图片资源
def GetImgDir():
    if os.path.exists(os.path.join(runPath, "superimg/")):
        basedir = os.path.join(runPath, "superimg/")
    else:
        basedir = os.path.join(superaiPath, "superimg/")

    logger.info(basedir)
    return basedir


# 配置路径
def GetCfgPath():
    if os.path.exists(os.path.join(runPath, "supercfg/")):
        settingdir = os.path.join(runPath, "supercfg/")
    else:
        settingdir = os.path.join(superaiPath, "supercfg/")

    logger.info(settingdir)
    return settingdir


# 获取账户配置文件
def GetCfgFile():
    return os.path.join(GetCfgPath(), "accounts")


# 数据库路径
def GetDbDir():
    if os.path.exists(os.path.join(runPath, "superdb/")):
        dbdir = os.path.join(runPath, "superdb/")
    else:
        dbdir = os.path.join(superaiPath, "superdb/")

    logger.info(dbdir)
    return dbdir


# 数据库文件
def getDbFile():
    return os.path.join(GetDbDir(), "subnodedb.db")


# 验证码缓存路径
def GetvercodeDir():
    if os.path.exists(os.path.join(runPath, "supervercode/")):
        d = os.path.join(runPath, "supervercode/")
    else:
        d = os.path.join(superaiPath, "supervercode/")
    logger.info(d)
    return d


# 游戏路径
def GameFileDir():
    if os.path.exists("c:/win/dnf"):
        gamedir = "c:/win/dnf/地下城与勇士/start/DNFchina.exe"
    else:
        gamedir = "d:/win/game/dnf/地下城与勇士/start/DNFchina.exe"

    if os.path.exists(os.path.join(GetCfgPath(), "superai.cfg")):
        config = configparser.RawConfigParser()
        config.read(os.path.join(GetCfgPath(), "superai.cfg"))
        gamedir = config.get('superai', '游戏路径')

    logger.info(gamedir)
    return gamedir
