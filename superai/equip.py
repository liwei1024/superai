import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import logging

logger = logging.getLogger(__name__)
from superai.common import InitLog, GameWindowToTop

from superai.flannfind import Picture, GetImgDir
from superai.vkcode import VK_CODE
from superai.yijianshu import PressKey, RanSleep, MouseMoveTo, MouseLeftDown, MouseLeftUp, YijianshuInit, \
    MouseLeftClick, MouseMoveR, MouseRightClick, KongjianSleep, LanSleep

from superai.gameapi import GetMenInfo, GetEquipObj, GetBagEquipObj, GameApiInit, FlushPid, TYPEMAP, BODYPOS, WUQIPOS, \
    SHIPINPOS, IsEscTop, GetXingyunxing, Clear, ChengHaoRequire, Openesc

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
CheckReplices = [
    (WUQIIDX, WUQITYPE),
    (SHANGYIIDX, SHANGYITYPE), (TOUJIANIDX, TOUJIANTYTPE), (XIAZHUANGIDX, XIAZHUANGTYPE), (XIEIDX, XIETYPE),
    (YAODAIIDX, YAODAITYPE),
    (XIANGLIANIDX, XIANGLIANGTYPE), (SHOUZHUOIDX, SHOUZHUOTYPE), (JIEZHIIDX, JIEZHITYPE)
]

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

bagScene = Picture(GetImgDir() + "bagscene.png")
zupinScene = Picture(GetImgDir() + "zupin_scene.png")
xingyunxing = Picture(GetImgDir() + "xingyunxing.png")
zupinconfirm = Picture(GetImgDir() + "zupin_confirm.png")
zupinconfirm2 = Picture(GetImgDir() + "zupin_confirm2.png")
chenghaobu = Picture(GetImgDir() + "chenghaobu.png")
chenghaobubtn = Picture(GetImgDir() + "chenghaobubtn.png")
zhuangbeizhanshi = Picture(GetImgDir() + "zhuangbeizhanshi.png")
jichudabiao = Picture(GetImgDir() + "jichudabiao.png")

levelNumMap = {
    10: 3,
    20: 5,
    30: 10,
    40: 15,
    50: 20,
    60: 25,
}

ZhunangbeiPos = (-89, 193)
XiaohaoPos = (-43, 194)


# 打开装备栏
def OpenBagScene():
    Clear()
    if not bagScene.Match():
        logger.info("打开装备栏")
        PressKey(VK_CODE["i"]), LanSleep()
    return bagScene.Match()


# 关闭装备栏
def CloseBagScene():

    while bagScene.Match():
        logger.info("关闭装备栏")
        PressKey(VK_CODE["esc"]), KongjianSleep()



class Equips:
    def __init__(self):
        meninfo = GetMenInfo()
        occupationafter = meninfo.zhuanzhihou
        occupationbefore = meninfo.zhuanzhiqian

        self.bodystragy = None

        if occupationbefore in ["魔枪士"]:
            self.bodystragy = ANYStrategy
            self.wuqistragy = ["长枪", "战戟", "光枪", "暗矛"]
            self.xingyunwuqipos = (-31, 114)
            if occupationafter in ["暗枪士", "狂怒恶鬼", "幽影夜神"]:
                self.bodystragy = PIJIA
                if meninfo.level >= 20:
                    self.wuqistragy = ["暗矛"]
                    self.xingyunwuqipos = (30, 111)

        elif occupationbefore in ["圣职者"]:
            self.bodystragy = ANYStrategy
            self.wuqistragy = ["十字架", "念珠", "图腾", "镰刀", "战斧"]
            self.xingyunwuqipos = (4, 107)
            if occupationafter in ["诱魔者", "断罪者", "救世者"]:
                self.bodystragy = ZHONGJIA
                if meninfo.level >= 20:
                    self.wuqistragy = ["镰刀"]
                    self.xingyunwuqipos = (63, 107)
        elif occupationbefore in ["守护者"]:
            self.bodystragy = ANYStrategy
            self.wuqistragy = ["短剑", "太刀", "钝器", "巨剑", "光剑"]
            self.xingyunwuqipos = (0, 109)
            if occupationafter in ["帕拉丁", "曙光", "破晓女神"]:
                self.bodystragy = BANJIA
                if meninfo.level >= 20:
                    self.wuqistragy = ["钝器"]
                    self.xingyunwuqipos = (0, 109)
        elif occupationbefore in ["鬼剑士"]:
            self.bodystragy = ANYStrategy
            self.wuqistragy = ["短剑", "太刀", "钝器", "巨剑", "光剑"]
            self.xingyunwuqipos = (0, 109)
            if occupationafter in ["剑影", "夜刀神", "夜见罗刹"]:
                self.bodystragy = PIJIA
                if meninfo.level >= 20:
                    self.wuqistragy = ["太刀"]
                    self.xingyunwuqipos = (30, 110)

        elif occupationbefore in ["格斗家"]:
            self.bodystragy = ANYStrategy
            self.wuqistragy = ["手套", "臂铠", "爪", "拳套", "东方棍"]
            self.xingyunwuqipos = (-56, 111)
            if occupationafter in ["气功师", "百花缭乱", "念帝"]:
                self.bodystragy = BUJIA
                if meninfo.level >= 20:
                    self.wuqistragy = ["手套"]
                    self.xingyunwuqipos = (-56, 111)
        elif occupationbefore in ["枪剑士"]:
            self.bodystragy = ANYStrategy
            self.wuqistragy = ["长刀", "小太刀", "重剑", "源力剑"]
            self.xingyunwuqipos = (-56, 111)
            if occupationafter in ["源能专家", "源力掌控者", "未来开拓者"]:
                self.bodystragy = BUJIA
                if meninfo.level >= 20:
                    self.wuqistragy = ["源力剑"]
                    self.xingyunwuqipos = (30, 110)
        else:
            raise NotImplementedError("还未支持的职业 %s" % occupationafter)

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

        # 幸运星优先
        meninfo = GetMenInfo()
        suitlevel = (meninfo.level // 10) * 10

        if v1.bodypos == WUQIPOS and "灵跃" in v1.name and v1.wuqitype in self.wuqistragy:
            return True
        elif v2.bodypos == WUQIPOS and "灵跃" in v2.name and v2.wuqitype in self.wuqistragy:
            return False

        if v1.bodypos == WUQIPOS and v1.canbeusedlevel >= suitlevel and "幸运星" in v1.name and v1.wuqitype in self.wuqistragy:
            return True
        elif v2.bodypos == WUQIPOS and v2.canbeusedlevel >= suitlevel and "幸运星" in v2.name and v2.wuqitype in self.wuqistragy:
            return False

        if v1.canbeusedlevel == 35 and "耀之荣光" in v1.name:
            return True
        elif v2.canbeusedlevel == 35 and "耀之荣光" in v2.name:
            return False

        if v1.canbeusedlevel > v2.canbeusedlevel:
            return True
        elif v1.canbeusedlevel == v2.canbeusedlevel:
            return v1.color > v2.color
        else:
            return False

    # 如果是身上穿的,判断下是甲类是否吻合
    def IsJiaTypeLegal(self, equip):
        meninfo = GetMenInfo()

        # 等级判断
        if equip.canbeusedlevel <= meninfo.level:

            # 身体
            if equip.bodypos in BODYPOS:
                # 任意策略
                if self.bodystragy == ANYStrategy:
                    return True
                # 指定策略
                if equip.jiatype == self.bodystragy:
                    return True
            # 武器
            elif equip.bodypos == WUQIPOS:
                # 指定策略
                if equip.wuqitype in self.wuqistragy:
                    return True

            # 手镯,项链,戒指
            elif equip.bodypos in SHIPINPOS:
                return True

        return False

    # 背包中相应类型的装备比身上的好  IDX: 身上装备下标 TYPE: 装备类型 curWrap: 当前装备
    # ->  返回 None 没有更好的选择,  返回 背包IDX 有更好的选择
    def BagEquipBetter(self, IDX, TYPE):
        equips = GetBagEquipObj()
        tobeWrapedEquip = None
        for v in equips:
            if v.bodypos == TYPE and v.color != 0:
                # 不是自己穿的忽略了
                if not self.IsJiaTypeLegal(v):
                    continue

                if tobeWrapedEquip is None:
                    if not self.BodyEquiped(IDX):
                        tobeWrapedEquip = v
                    else:
                        if v.bodypos == WUQIPOS and self.DoesWuqiXingyunxing():
                            pass
                        elif self.CompareEquip(v, self.GetBodyEquip(IDX)):
                            tobeWrapedEquip = v
                else:

                    if v.bodypos == WUQIPOS and self.DoesWuqiXingyunxing():
                        pass
                    elif self.CompareEquip(v, tobeWrapedEquip):
                        tobeWrapedEquip = v
        return tobeWrapedEquip

    # 背包下标到相对位置
    def BagIdxToPos(self, idx, bagpos):
        firstpos = (bagpos[0] - 100, bagpos[1] + 220)
        cellw, cellh = 30, 30
        cellx, celly = idx % 8, idx // 8
        pos = (firstpos[0] + cellw * cellx, firstpos[1] + cellh * celly)
        return pos

    # 更换装备
    def ChangeEquip(self):
        if not OpenBagScene():
            logger.warning("打开装备栏失败")
            return

        bagpos = bagScene.Pos()

        MouseMoveTo(bagpos[0] - 91, bagpos[1] + 192), KongjianSleep()
        MouseLeftClick(), KongjianSleep()

        def EquipBetter():
            for v in CheckReplices:
                betterEquip = self.BagEquipBetter(v[0], v[1])
                if betterEquip is not None:
                    logger.info("更换装备: %s", betterEquip)
                    pos = self.BagIdxToPos(betterEquip.idx - 9, bagpos)
                    MouseMoveTo(pos[0], pos[1]), KongjianSleep()
                    MouseLeftDown(), KongjianSleep()
                    MouseMoveTo(bagpos[0], bagpos[1] + 100), KongjianSleep()
                    MouseLeftUp(), KongjianSleep()
                    MouseLeftClick(), KongjianSleep()

        # 两次调用. 防止魔法封印
        EquipBetter()

        if self.DoesBagHaveBetterEquip():
            RanSleep(0.5)
            EquipBetter()

    # 背包内是否有有更好的装备
    def DoesBagHaveBetterEquip(self):
        for v in CheckReplices:
            betterEquip = self.BagEquipBetter(v[0], v[1])
            if betterEquip is not None:
                return True
        return False

    # 身上或者背包里是否有租的武器
    def DoesHaveHireEquip(self):
        meninfo = GetMenInfo()
        suitlevel = (meninfo.level // 10) * 10
        equips = GetBagEquipObj()
        for v in equips:
            if v.bodypos == WUQIPOS and v.canbeusedlevel == suitlevel and "幸运星" in v.name and v.wuqitype in self.wuqistragy:
                return True
        equips = GetEquipObj()
        for v in equips:
            if v.bodypos == WUQIPOS and v.canbeusedlevel == suitlevel and "幸运星" in v.name and v.wuqitype in self.wuqistragy:
                return True
        return False

    # 武器是幸运星武器且符合等级
    def DoesWuqiXingyunxing(self):
        meninfo = GetMenInfo()
        suitlevel = (meninfo.level // 10) * 10
        equips = GetEquipObj()
        for v in equips:
            if v.bodypos == WUQIPOS and v.canbeusedlevel == suitlevel and "幸运星" in v.name and v.wuqitype in self.wuqistragy:
                return True
        return False

    # 获取幸运星数量
    def GetXingyunxing(self):
        if not self.OpenZupin():
            logger.warning("打开租聘失败")
            return 0

        return GetXingyunxing().num

    # 租聘武器
    def ZupinWuqi(self):
        if not self.OpenZupin():
            logger.warning("打开租聘失败")
            return

        pos = zupinScene.Pos()
        MouseMoveTo(pos[0] + self.xingyunwuqipos[0], pos[1] + self.xingyunwuqipos[1]), KongjianSleep()
        MouseLeftClick(), KongjianSleep()
        MouseMoveTo(pos[0] + 9, pos[1] + 143), KongjianSleep()
        MouseLeftClick(), KongjianSleep()
        pos = zupinconfirm2.Pos()
        MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        MouseLeftClick(), KongjianSleep()

    # 是否足够的幸运星
    def HaveEnoughXingyunxing(self):
        num = self.GetXingyunxing()
        meninfo = GetMenInfo()
        requirenum = levelNumMap[(meninfo.level // 10) * 10]
        if num >= requirenum:
            return True

    # 打开租聘界面
    def OpenZupin(self):
        if not zupinScene.Match():
            Clear()  # 判断数量 + 租聘. 所以在这里clear
            logger.info("要打开幸运星租聘界面")
            if not Openesc():
                logger.warning("打开esc失败")
                return False

            pos = xingyunxing.Pos()
            MouseMoveTo(pos[0], pos[1]), KongjianSleep()
            MouseLeftClick(), LanSleep()

        return zupinScene.Match()

    # 关闭租聘界面
    def CloseZupin(self):

        while zupinScene.Match():
            logger.info("关闭幸运星租聘界面")
            PressKey(VK_CODE["esc"]), KongjianSleep()

    # 是否可以领称号(基础达标者)
    def NeedGetChenghao(self):
        equips = GetEquipObj()

        # 有就别领了
        for v in equips:
            if v.bodypos == 13:
                return False

        if len(equips) < 9:
            return False

        # 所有装备是紫色才领
        for v in equips:
            if v.bodypos in ChengHaoRequire:
                if v.color < 2:
                    return False

        return True

    # 获得称号界面
    def OpenChenghao(self):
        Clear()
        if not chenghaobu.Match():
            if not OpenBagScene():
                logger.warning("打开装备栏失败")
                return False

            logger.info("要打开称号栏")
            pos = chenghaobubtn.Pos()
            MouseMoveTo(pos[0], pos[1]), KongjianSleep()
            MouseLeftClick(), LanSleep()

            MouseMoveTo(0, 0)

        return chenghaobu.Match()

    # 获取称号
    def GetChenghao(self):
        if not self.OpenChenghao():
            logger.warning("打开称号栏失败")
            return

        pos = zhuangbeizhanshi.Pos()
        MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        MouseLeftClick(), KongjianSleep()

        pos = jichudabiao.Pos()
        MouseMoveTo(pos[0], pos[1]), KongjianSleep()
        MouseRightClick(), KongjianSleep()


def main():
    InitLog()
    GameApiInit()
    FlushPid()
    YijianshuInit()
    GameWindowToTop()

    eq = Equips()
    # eq.ZupinWuqi()
    eq.ChangeEquip()


if __name__ == '__main__':
    main()
