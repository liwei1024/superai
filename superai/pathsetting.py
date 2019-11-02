import os
import sys
from ctypes import CDLL, RTLD_GLOBAL

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging
from superai.config import GetConfig

logger = logging.getLogger(__name__)


def GetGlobalPath():
    if os.path.basename(sys.executable) == "python.exe":
        # 1. python 启动. 获取源码的绝对路径
        pyPath = os.path.split(os.path.realpath(__file__))[0]
        globalPath = os.path.dirname(pyPath)
    else:
        # 2. 打包的exe 启动. 获取exe的绝对路径
        runPath = os.path.split(sys.executable)[0]
        globalPath = os.path.split(runPath)[0]

    return globalPath


globalPath = GetGlobalPath()

# xxiii 目录
xxxiiiPath = os.path.join(os.path.dirname(globalPath), "xxiii")

# 本地调试用
localenvPath = "d:/win/studio/env/dists"


# 版本号文件 (客户端读的时候才会用)
def GetVersionFile():
    return os.path.join(globalPath, "version")


# 获取更新服务器的root目录
def GetServerRootDirectory():
    if os.path.exists(os.path.join(localenvPath)):
        return localenvPath
    else:
        return "~/env/dists"


# 底层依赖
def GetHelpdllLib():
    lib = CDLL(os.path.join(xxxiiiPath, "x64/Release/helpdll-xxiii.dll"), RTLD_GLOBAL)
    return lib


# 启动启动脚本
def GetDriverStartFile():
    return os.path.join(xxxiiiPath, "x64/Release/load.cmd")


# 启动关闭脚本
def GetDriverStopFile():
    return os.path.join(xxxiiiPath, "x64/Release/unload.cmd")


# 易键鼠dll
def GetYiLib():
    return CDLL(os.path.join(globalPath, "dll/msdk.dll"), RTLD_GLOBAL)


# 幽灵exe
def GetYoulingExe():
    return os.path.join(globalPath, "help/start.cmd")


# 图片资源
def GetImgDir():
    return os.path.join(globalPath, "superimg/")


# 配置路径
def GetCfgPath():
    return os.path.join(globalPath, "supercfg/")


# 获取账户配置文件
def GetCfgFile():
    return os.path.join(GetCfgPath(), "accounts")


# 数据库路径
def GetDbDir():
    return os.path.join(globalPath, "superdb/")


# 数据库文件
def getDbFile():
    return os.path.join(GetDbDir(), "subnodedb.db")


# 验证码缓存路径
def GetvercodeDir():
    return os.path.join(globalPath, "supervercode/")


# 游戏路径
def GameFileDir():
    if os.path.exists("c:/win/dnf"):
        gamedir = "c:/win/dnf/地下城与勇士/start/DNFchina.exe"
        if os.path.exists(gamedir):
            return gamedir
    else:
        gamedir = "d:/win/game/dnf/地下城与勇士/start/DNFchina.exe"
        if os.path.exists(gamedir):
            return gamedir

    if os.path.exists(os.path.join(GetCfgPath(), "superai.cfg")):
        from superai.config import GetConfig
        config = GetConfig()
        gamedir = config.get('superai', '游戏路径')
    else:
        gamedir = ""

    return gamedir


# tgp路径
def TgpDir():
    if os.path.exists("d:/Program Files (x86)/WeGame"):
        tgpdir = "d:/Program Files (x86)/WeGame/tgp_daemon.exe"
        if os.path.exists(tgpdir):
            return tgpdir
    else:
        tgpdir = "c:/Program Files (x86)/WeGame/tgp_daemon.exe"
        if os.path.exists(tgpdir):
            return tgpdir

    if os.path.exists(os.path.join(GetCfgPath(), "superai.cfg")):
        config = GetConfig()
        tgpdir = config.get("superai", 'wegame路径')
    else:
        tgpdir = ""

    return tgpdir
