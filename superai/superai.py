import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import math
from win32api import Sleep

from superai.gameapi import GetManXY, GetMonsterLst, GetMonster, GameApiInit
from superai.call import MoveCall
from superai.yijianshu import YijianshuInit, AttackPress


def distance(x1, y1, x2, y2) -> int:
    xseparation = x2 - x1
    yseparation = y2 - y1
    return int(math.sqrt(xseparation * xseparation + yseparation * yseparation))


def main():
    if GameApiInit():
        print("Init helpdll-xxiii.dll ok")
    else:
        print("Init helpdll-xxiii.dll err")
        exit(0)

    if YijianshuInit():
        print("Init 易键鼠 ok")
    else:
        print("Init 易键鼠 err")
        exit(0)

    while True:
        print("=====================")
        manx, many = GetManXY()
        monsters = GetMonsterLst()

        # 排序, 最近
        monsters.sort(
            key=lambda mon: distance(manx, many, mon.x, mon.y)
        )

        for mon in monsters:
            print("距离: {} {}".format(distance(manx, many, mon.x, mon.y), mon))

        # 没有怪物了
        if len(monsters) < 1:
            break
            # TODO 找图, 过图

        # 锁定怪物
        curMon = monsters[0]
        while True:
            Sleep(200)
            curMon = GetMonster(curMon)
            if curMon is None:
                break
            MoveCall(int(curMon.x), int(curMon.y))
            Sleep(50)
            AttackPress()

        Sleep(300)


if __name__ == "__main__":
    main()
