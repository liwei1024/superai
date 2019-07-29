import os
import sys
import time

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.gameapi import GameApiInit, GetSeceneInfo, FlushPid, GetMenInfo, GetMonsters, GetGoods, IsManInMap, \
    GetNextDoor


def main():
    if GameApiInit():
        print("Init helpdll-xxiii.dll ok")
    else:
        print("Init helpdll-xxiii.dll err")
        exit(0)
    FlushPid()

    while True:

        dixinglst, dixingvec, obstacles, wh = GetSeceneInfo()
        # print("宽高: %s" % wh)
        img = np.zeros((wh.h, wh.w, 3), dtype=np.uint8)
        img[np.where(img == [0])] = [255]

        if IsManInMap():

            # 地形链表. x,y左上角
            for v in dixinglst:
                cv2.rectangle(img, (v.x, v.y), (v.x + 0x10, v.y + 0xc), (144, 128, 112), 2)

            # 地形数组. x,y左上角
            for v in dixingvec:
                cv2.rectangle(img, (v.x, v.y), (v.x + 0x10, v.y + 0xc), (64, 64, 64), 2)

            # 障碍物. x,y中点
            for v in obstacles:
                halfw = int(v.w / 2)
                halfh = int(v.h / 2)
                cv2.rectangle(img, (v.x - halfw, v.y - halfh), (v.x + halfw, v.y + halfh), (64, 64, 64), 2)

            # 人,怪物,物品. x,y中点
            meninfo = GetMenInfo()
            halfw = int(meninfo.w / 2)
            halfh = int(meninfo.h / 2)
            cv2.rectangle(img, (int(meninfo.x) - halfw, int(meninfo.y) - halfh),
                          (int(meninfo.x) + halfw, int(meninfo.y) + halfh),
                          (0, 0, 255), 2)

            monsters = GetMonsters()
            for mon in monsters:
                halfw = int(mon.w / 2)
                halfh = int(mon.h / 2)
                cv2.rectangle(img, (int(mon.x) - halfw, int(mon.y) - halfh),
                              (int(mon.x) + halfw, int(mon.y) + halfh),
                              (0, 140, 255), 2)

            goods = GetGoods()
            for good in goods:
                halfw = int(20 / 2)
                halfh = int(20 / 2)
                cv2.rectangle(img, (int(good.x) - halfw, int(good.y) - halfh),
                              (int(good.x) + halfw, int(good.y) + halfh),
                              (0, 140, 255), 2)

            # 门. x,y 左上角
            nextdoor = GetNextDoor()
            cv2.rectangle(img, (nextdoor.x, nextdoor.y), (nextdoor.x + nextdoor.w, nextdoor.y + nextdoor.h), (255, 144, 30), 2)

            cv2.imshow('img', img)
            if (cv2.waitKey(30) & 0xFF) in [ord('q'), 27]:
                break
            time.sleep(0.3)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
