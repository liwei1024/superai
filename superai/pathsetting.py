import os
import sys
from ctypes import CDLL, RTLD_GLOBAL

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging
from superai.config import GetConfig

logger = logging.getLogger(__name__)

runPath = os.path.split(sys.executable)[0]
runPath = os.path.split(runPath)[0]

if os.path.exists("c:/win/reference"):
    xxxiiiPath = "c:/win/reference/project/xxiii"
    superaiPath = "c:/win/reference/project/superai"
else:
    xxxiiiPath = "d:/win/reference/project/xxiii"
    superaiPath = "d:/win/reference/project/superai"


# 底层依赖
def GetHelpdllLib():
    if os.path.exists(os.path.join(runPath, "x64/Release/")):
        lib = CDLL(os.path.join(runPath, "x64/Release/helpdll-xxiii.dll"), RTLD_GLOBAL)
    else:
        lib = CDLL(os.path.join(xxxiiiPath, "x64/Release/helpdll-xxiii.dll"), RTLD_GLOBAL)
    return lib


# 启动启动脚本
def GetDriverStartFile():
    if os.path.exists(os.path.join(runPath, "x64/Release/")):
        p = os.path.join(runPath, "x64/Release/load.cmd")
    else:
        p = os.path.join(xxxiiiPath, "x64/Release/load.cmd")
    return p


# 易键鼠dll
def GetYiLib():
    if os.path.exists(os.path.join(runPath, "superai/dll/")):
        lib = CDLL(os.path.join(runPath, "superai/dll/msdk.dll"), RTLD_GLOBAL)
    else:
        lib = CDLL(os.path.join(superaiPath, "dll/msdk.dll"), RTLD_GLOBAL)
    return lib


# 幽灵exe
def GetYoulingExe():
    if os.path.exists(os.path.join(runPath, "superai/help/")):
        path = os.path.join(runPath, "superai/help/start.cmd")
    else:
        path = os.path.join(superaiPath, "help/start.cmd")
    return path


# 图片资源
def GetImgDir():
    if os.path.exists(os.path.join(runPath, "superimg/")):
        basedir = os.path.join(runPath, "superimg/")
    else:
        basedir = os.path.join(superaiPath, "superimg/")
    return basedir


# 配置路径
def GetCfgPath():
    if os.path.exists(os.path.join(runPath, "supercfg/")):
        settingdir = os.path.join(runPath, "supercfg/")
    else:
        settingdir = os.path.join(superaiPath, "supercfg/")
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
    return d


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

    if os.path.exists(os.path.join(GetCfgPath(), "superai.cfg")):
        config = GetConfig()
        tgpdir = config.get("superai", 'wegame路径')
    else:
        tgpdir = ""

    return tgpdir
