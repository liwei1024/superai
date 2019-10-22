import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)

from superai.vkcode import VK_CODE
from superai.common import InitLog, GameWindowToTop, KongjianSleep, RanSleep
from superai.gameapi import GameApiInit, FlushPid, GetBagEquipObj, BODYPOS, Clear, GetEquipObj
from superai.flannfind import Picture, GetImgDir
from superai.location import Location
from superai.anjian import aj

fenjieGelanzhisen = Picture(GetImgDir() + "fenjie_gelanzhisen.png")
fenjieTiankongzhicheng = Picture(GetImgDir() + "fenjie_tiankonghzicheng.png")
fenjieTianzhuijushou = Picture(GetImgDir() + "fenjieTianzhuijushou.png")
fenjieButton = Picture(GetImgDir() + "fenjie_button.png")
fenjiexiulijiScene = Picture(GetImgDir() + "fenjiexiuliji_scene.png")
fenjieConfirm = Picture(GetImgDir() + "fenjie_confirm.png")
fenjieAfaliya = Picture(GetImgDir() + "fenjieAfaliya.png")
fenjieNuoyipeila = Picture(GetImgDir() + "fenjie_nuoyipeila.png")
fenjieXueshan = Picture(GetImgDir() + "fenjie_xuieshan.png")
fenjieNuosimaer = Picture(GetImgDir() + "fenjie_nuosimaer.png")
fenjieyanuofasenlin = Picture(GetImgDir() + "fenjie_yanuofasenlin.png")
fenjieeyunzhicheng = Picture(GetImgDir() + "fenjie_eyunzhicheng.png")
fenjieniliupubu = Picture(GetImgDir() + "fenjie_niliupubu.png")
fenjiegente = Picture(GetImgDir() + "fenjie_gente.png")

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
        location = Location()
        lo = location.GetFenjieLocation()

        if lo == "格兰之森":
            pos = fenjieGelanzhisen.Pos()
        if lo == "雪山":
            pos = fenjieXueshan.Pos()
        elif lo == "天空之城":
            pos = fenjieTiankongzhicheng.Pos()
        elif lo == "天锥巨兽":
            pos = fenjieTianzhuijushou.Pos()
        elif lo == "诺斯玛尔":
            pos = fenjieNuosimaer.Pos()
        elif lo == "阿法利亚":
            pos = fenjieAfaliya.Pos()
        elif lo == "诺伊佩拉":
            pos = fenjieNuoyipeila.Pos()
        elif lo == "亚诺法森林":
            pos = fenjieyanuofasenlin.Pos()
        elif lo == "厄运之城":
            pos = fenjieeyunzhicheng.Pos()
        elif lo == "逆流瀑布":
            pos = fenjieniliupubu.Pos()
        elif lo == "根特":
            pos = fenjiegente.Pos()
        return pos

    # 分解
    def FenjieAll(self):
        Clear()

        logger.info("分解所有")

        pos = self.GetFenjieJiPos()

        if pos is None or pos == (0, 0):
            return

        aj().MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        aj().MouseLeftClick(), KongjianSleep()
        aj().MouseMoveR(56, 54), KongjianSleep()
        aj().MouseLeftClick(), KongjianSleep()

        # 分解按钮
        fenjiebt = fenjieButton.Pos()
        aj().MouseMoveTo(fenjiebt[0], fenjiebt[1]), KongjianSleep()

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
                aj().MouseMoveTo((v[1])[0], (v[1])[1]), KongjianSleep()
                aj().MouseLeftClick(), KongjianSleep()
                aj().MouseMoveTo(fenjiebt[0], fenjiebt[1]), KongjianSleep()

        # 分解按钮
        aj().MouseMoveTo(fenjiebt[0], fenjiebt[1]), KongjianSleep()
        aj().MouseLeftClick(), KongjianSleep()

        # 确认
        pos = fenjieConfirm.Pos()
        aj().MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        aj().MouseLeftClick(), RanSleep(3.0)

    # 卖所有装备
    def SellAll(self):
        Clear()

        logger.info("出售所有")
        pos = self.GetFenjieJiPos()

        if pos is None or pos == (0, 0):
            return

        aj().MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        aj().MouseLeftClick(), KongjianSleep()
        aj().MouseMoveR(56, 32), KongjianSleep()
        aj().MouseLeftClick(), KongjianSleep()

        # 出售按钮
        sellbtn = sellButton.Pos()
        aj().MouseMoveTo(sellbtn[0], sellbtn[1]), KongjianSleep()
        aj().MouseLeftClick(), KongjianSleep()

        bagpos = bagScene.Pos()

        equips = GetBagEquipObj()
        for v in equips:
            pos = self.BagIdxToPos(v.idx - 9, bagpos)
            aj().MouseMoveTo(pos[0], pos[1]), KongjianSleep()
            aj().MouseLeftClick(), KongjianSleep()
            aj().MouseLeftClick(), KongjianSleep()

        self.CloseSell()

    # 修理 (身上5件 + 武器)
    def RepairAll(self):
        Clear()

        logger.info("修理所有")
        pos = self.GetFenjieJiPos()

        if pos is None or pos == (0, 0):
            return

        aj().MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        aj().MouseLeftClick(), KongjianSleep()
        aj().MouseMoveR(56, 32), KongjianSleep()
        aj().MouseLeftClick(), KongjianSleep()

        # 修理按钮
        repairbtn = repairButton.Pos()
        aj().MouseMoveTo(repairbtn[0], repairbtn[1]), KongjianSleep()
        aj().MouseLeftClick(), KongjianSleep()
        aj().MouseLeftClick(), KongjianSleep()

    # 是否需要被修理
    def NeedRepair(self):
        equips = GetEquipObj()
        for v in equips:
            if v.bodypos in BODYPOS or v.bodypos == 12:
                if v.maxnaijiu > 0.0 and v.curnaijiu / v.maxnaijiu < 0.25:
                    return True

        return False

    # 关闭分解机
    def CloseFenjie(self):
        while fenjiexiulijiScene.Match():
            logger.info("关闭分解机")
            aj().PressKey(VK_CODE["esc"]), KongjianSleep()

    # 关闭卖物
    def CloseSell(self):
        while sellButton.Match():
            logger.info("关闭分解机")
            aj().PressKey(VK_CODE["esc"]), KongjianSleep()


def main():
    InitLog()
    if not GameApiInit():
        sys.exit()
    FlushPid()
    if not aj().Init():
        sys.exit()
    GameWindowToTop()

    dq = DealEquip()
    print(dq.NeedRepair())


if __name__ == '__main__':
    main()
