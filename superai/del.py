import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

logger = logging.getLogger(__name__)

from superai.common import InitLog
from superai.gameapi import GameApiInit, FlushPid, GetMenInfo, DescryptF, EncryptF


def main():
    InitLog()
    if not GameApiInit():
        sys.exit()
    FlushPid()

    meninfo = GetMenInfo()

    value = DescryptF(meninfo.object + 0x1728)  # 倍功
    print(value)
    value = DescryptF(meninfo.object + 0x1578)  # 移动速度
    print(value)
    value = DescryptF(meninfo.object + 0x15a8)  # 攻击速度
    print(value)

    EncryptF(meninfo.object + 0x1728, 1.0)
    # EncryptF(meninfo.object + 0x1578, 2.0)
    # EncryptF(meninfo.object + 0x15a8, 0.0)

    value = DescryptF(meninfo.object + 0x1728)  # 倍功
    print(value)
    value = DescryptF(meninfo.object + 0x1578)  # 移动速度
    print(value)
    value = DescryptF(meninfo.object + 0x15a8)  # 攻击速度
    print(value)


if __name__ == '__main__':
    main()
