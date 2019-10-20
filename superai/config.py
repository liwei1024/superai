import configparser
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.pathsetting import GetCfgPath


def GetConfig():
    cfgfile = os.path.join(GetCfgPath(), "superai.cfg")
    config = configparser.RawConfigParser()
    config.read(cfgfile)
    return config


def SaveConfig(cfg):
    cfgfile = os.path.join(GetCfgPath(), "superai.cfg")
    f = open(cfgfile, "w")
    cfg.write(f)
    f.close()


def main():
    config = GetConfig()


if __name__ == '__main__':
    main()
