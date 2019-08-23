import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

from superai.common import InitLog, GameWindowToTop
from superai.gameapi import GameApiInit, FlushPid, GetBagEquipObj, GetMenInfo, BODYPOS

from superai.flannfind import Picture, GetImgDir
from superai.location import Location
from superai.yijianshu import MouseMoveTo, RanSleep, MouseLeftClick, MouseMoveR, PressKey, VK_CODE, YijianshuInit

fenjieGelanzhisen = Picture(GetImgDir() + "fenjie_gelanzhisen.png")
fenjieTiankongzhicheng = Picture(GetImgDir() + "fenjie_tiankonghzicheng.png")
fenjieTianzhuijushou = Picture(GetImgDir() + "fenjieTianzhuijushou.png")
fenjieButton = Picture(GetImgDir() + "fenjie_button.png")
fenjiexiulijiScene = Picture(GetImgDir() + "fenjiexiuliji_scene.png")
fenjieConfirm =  Picture(GetImgDir() + "fenjie_confirm.png")
sellButton = Picture(GetImgDir() + "sellbt.png")
bagScene = Picture(GetImgDir() + "bagscene.png")
repairButton = Picture(GetImgDir() + "repair.png")


class DealEquip:
    def __init__(self):
        pass

    # 背包下标到相对位置
    def BagIdxToPos(self, idx, bagpos):
        firstpos = (bagpos[0] - 100, bagpos[1] + 220)
        cellw, cellh = 30, 30
        cellx, celly = idx % 8, idx // 8
        pos = (firstpos[0] + cellw * cellx, firstpos[1] + cellh * celly)
        return pos

    # 获取到分解机位置
    def GetFenjieJiPos(self):
        pos = None
        lo = Location()
        if lo.get() == "格兰之森":
            pos = fenjieGelanzhisen.Pos()
        elif lo.get() == "天空之城":
            pos = fenjieTiankongzhicheng.Pos()
        elif lo.get() == "天锥巨兽":
            pos = fenjieTianzhuijushou.Pos()

        return pos

    # 分解
    def FenjieAll(self):
        logger.info("分解所有")

        pos = self.GetFenjieJiPos()

        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)
        MouseMoveR(56, 54), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)

        # 分解按钮
        fenjiebt = fenjieButton.Pos()
        MouseMoveTo(fenjiebt[0], fenjiebt[1]), RanSleep(0.3)

        print(fenjiebt)

        # 检查 "稀有" "勇者" "包含我的职业装备" 是否勾选
        xiyoucheck = (Picture(GetImgDir() + "checked.png", fenjiebt[0] + 67, fenjiebt[1] + 47, 12, 12),
                      (fenjiebt[0] + 67 + 6, fenjiebt[1] + 47 + 6))

        yongzhecheck = (Picture(GetImgDir() + "checked.png", fenjiebt[0] + 67, fenjiebt[1] + 61, 12, 12),
                        (fenjiebt[0] + 67 + 6, fenjiebt[1] + 61 + 6))

        zhiyecheck = (Picture(GetImgDir() + "checked.png", fenjiebt[0] + 67, fenjiebt[1] + 80, 12, 12),
                      (fenjiebt[0] + 67 + 6, fenjiebt[1] + 80 + 6))

        checks = [xiyoucheck, yongzhecheck, zhiyecheck]
        for v in checks:
            if not v[0].Match():
                MouseMoveTo((v[1])[0], (v[1])[1]), RanSleep(0.3)
                MouseLeftClick(), RanSleep(0.3)
                MouseMoveTo(fenjiebt[0], fenjiebt[1]), RanSleep(0.3)

        # 分解按钮
        MouseMoveTo(fenjiebt[0], fenjiebt[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)

        # 确认
        pos = fenjieConfirm.Pos()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(4.0)

    # 卖所有装备
    def SellAll(self):
        logger.info("出售所有")
        pos = self.GetFenjieJiPos()
        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)
        MouseMoveR(56, 32), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)

        # 出售按钮
        sellbtn = sellButton.Pos()
        MouseMoveTo(sellbtn[0], sellbtn[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)

        bagpos = bagScene.Pos()

        equips = GetBagEquipObj()
        for v in equips:
            pos = self.BagIdxToPos(v.idx - 9, bagpos)
            MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
            MouseLeftClick(), RanSleep(0.3)
            MouseLeftClick(), RanSleep(0.3)

        self.CloseSell()

    # 修理 (身上5件 + 武器)
    def RepairAll(self):
        logger.info("修理所有")
        pos = self.GetFenjieJiPos()

        MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)
        MouseMoveR(56, 32), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)

        # 修理按钮
        repairbtn = repairButton.Pos()
        MouseMoveTo(repairbtn[0], repairbtn[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)

    # 是否需要被修理
    def NeedRepair(self):
        equips = GetBagEquipObj()
        for v in equips:
            if v.bodypos in BODYPOS or v.bodypos == 12:
                if v.curnaijiu / v.maxnaijiu < 0.25:
                    return True

        return False

    # 关闭分解机
    def CloseFenjie(self):
        while fenjiexiulijiScene.Match():
            logger.info("关闭分解机")
            PressKey(VK_CODE["esc"]), RanSleep(0.3)

    # 关闭卖物
    def CloseSell(self):
        while sellButton.Match():
            logger.info("关闭分解机")
            PressKey(VK_CODE["esc"]), RanSleep(0.3)


def main():
    InitLog()
    GameApiInit()
    FlushPid()
    YijianshuInit()
    GameWindowToTop()

    dq = DealEquip()
    dq.FenjieAll()


if __name__ == '__main__':
    main()
