import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
logger = logging.getLogger(__name__)

from superai.config import GetConfig, SaveConfig
from superai.superai import InitSetting


def main():
    InitSetting()
    config = GetConfig()
    config.set("superai", "wegame路径", "c:/program files (x86)/wegame/tgp_daemon.exe")
    config.set("superai", "登录方式", "wegame")
    config.set("superai", "单账号刷角色数量", "6")
    SaveConfig(config)


if __name__ == '__main__':
    main()
