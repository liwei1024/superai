import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)
from superai.common import InitLog, GameWindowToTop

from superai.flannfind import Picture, GetImgDir
from superai.vkcode import VK_CODE
from superai.yijianshu import PressKey, RanSleep, MouseMoveTo, MouseLeftDown, MouseLeftUp, YijianshuInit

from superai.gameapi import GetMenInfo, GetEquipObj, GetBagEquipObj, GameApiInit, FlushPid, TYPEMAP, BODYPOS

# 任意策略
ANYStrategy = -1

#  布甲0,皮甲1,轻甲2,重甲3,板甲4
BUJIA = 0
PIJIA = 1
QINGJIA = 2
ZHONGJIA = 3
BANJIA = 4

# 下标, 武器0,称号1,上衣2,头肩3,下装4,鞋5,腰带6,项链7,护腕8,戒指9
WUQIIDX, WUQITYPE = 0, 12
CHENGHAOIDX, CHENGHAOTYPE = 1, 13
SHANGYIIDX, SHANGYITYPE = 2, 14
TOUJIANIDX, TOUJIANTYTPE = 3, 15
XIAZHUANGIDX, XIAZHUANGTYPE = 4, 16
XIEIDX, XIETYPE = 5, 17
YAODAIIDX, YAODAITYPE = 6, 18
XIANGLIANIDX, XIANGLIANGTYPE = 7, 19
SHOUZHUOIDX, SHOUZHUOTYPE = 8, 20
JIEZHIIDX, JIEZHITYPE = 9, 21

# 检查替换
CheckReplices = {
    (WUQIIDX, WUQITYPE),
    (SHANGYIIDX, SHANGYITYPE), (TOUJIANIDX, TOUJIANTYTPE), (XIAZHUANGIDX, XIAZHUANGTYPE), (XIEIDX, XIETYPE),
    (YAODAIIDX, YAODAITYPE),
    (XIANGLIANIDX, XIANGLIANGTYPE), (SHOUZHUOIDX, SHOUZHUOTYPE), (JIEZHIIDX, JIEZHITYPE)
}

IDXNAMEMAP = {
    WUQIIDX: "武器",
    CHENGHAOIDX: "称号",
    SHANGYIIDX: "上衣",
    TOUJIANIDX: "头肩",
    XIAZHUANGIDX: "下装",
    XIEIDX: "鞋",
    YAODAIIDX: "腰带",
    XIANGLIANIDX: "项链",
    SHOUZHUOIDX: "护腕",
    JIEZHIIDX: "戒指",
}

bagScene = Picture(GetImgDir() + "/bagscene.png")


class Equips:
    def __init__(self):
        meninfo = GetMenInfo()
        occupationafter = meninfo.zhuanzhihou

        self.bodystragy = None

        if occupationafter in ["魔枪士"]:
            self.bodystragy = ANYStrategy

        if occupationafter in ["暗枪士"]:
            self.bodystragy = PIJIA

        if self.bodystragy is None:
            raise NotImplementedError()

    # 打开装备栏
    def OpenBagScene(self):
        while not bagScene.Match():
            logger.info("装备栏没有打开")
            PressKey(VK_CODE["i"]), RanSleep(0.5)
            if bagScene.Match():
                return True

    # 关闭装备栏
    def CloseBagScene(self):
        while bagScene.Match():
            logger.info("装备栏已经打开")
            PressKey(VK_CODE["i"]), RanSleep(0.5)
            if not bagScene.Match():
                return True

    # 身上没有装备
    def BodyEquiped(self, IDX):
        menequips = GetEquipObj()
        for v in menequips:
            if v.idx == IDX:
                return True
        return False

    # 获取身上指定位置装备
    def GetBodyEquip(self, IDX):
        menequips = GetEquipObj()
        for v in menequips:
            if v.idx == IDX:
                return v
        return None

    # 比较装备 等级优先, 等级相等品级优先
    def CompareEquip(self, v1, v2):
        if v1.canbeusedlevel > v2.canbeusedlevel:
            return True
        elif v1.canbeusedlevel == v2.canbeusedlevel:
            return v1.color > v2.color
        else:
            return False

    # 如果是身上穿的,判断下是甲类是否吻合
    def IsJiaTypeLegal(self, equip):
        # 不是身上穿的不判断了
        if equip.bodypos not in BODYPOS:
            return True
        if equip.jiatype != self.bodystragy:
            return False
        return True

    # 背包中相应类型的装备比身上的好  IDX: 身上装备下标 TYPE: 装备类型 curWrap: 当前装备
    # ->  返回 None 没有更好的选择,  返回 背包IDX 有更好的选择
    def BagEquipBetter(self, IDX, TYPE):
        equips = GetBagEquipObj()
        tobeWrapedEquip = None
        for v in equips:
            if v.bodypos == TYPE:
                # 不是自己穿的忽略了
                if not self.IsJiaTypeLegal(v):
                    continue

                if tobeWrapedEquip is None:
                    if not self.BodyEquiped(IDX):
                        tobeWrapedEquip = v
                    else:
                        if self.CompareEquip(v, self.GetBodyEquip(IDX)):
                            tobeWrapedEquip = v
                else:
                    if self.CompareEquip(v, tobeWrapedEquip):
                        tobeWrapedEquip = v
        return tobeWrapedEquip

    # 背包下标到相对位置
    def BagIdxToPos(self, idx, bagpos):
        firstpos = (bagpos[0] - 100, bagpos[1] + 220)
        cellw, cellh = 30, 30
        cellx, celly = idx % 8, idx // 8
        pos = (firstpos[0] + cellw * cellx, firstpos[1] + cellh * celly)
        return pos

    # 更换装备.
    def ChangeEquip(self):
        self.OpenBagScene(), RanSleep(0.5)
        bagpos = bagScene.Pos()
        for v in CheckReplices:
            betterEquip = self.BagEquipBetter(v[0], v[1])
            if betterEquip is not None:
                logger.info("更换装备: %s", betterEquip)
                pos = self.BagIdxToPos(betterEquip.idx - 9, bagpos)
                MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
                MouseLeftDown(), RanSleep(0.3)
                MouseMoveTo(bagpos[0], bagpos[1] + 100), RanSleep(0.3)
                MouseLeftUp(), RanSleep(0.3)


def main():
    InitLog()
    GameApiInit()
    FlushPid()
    YijianshuInit()
    GameWindowToTop()

    eq = Equips()
    eq.ChangeEquip()


if __name__ == '__main__':
    main()
