import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.superai import GameWindowToTop
from superai.yijianshu import PressKey, VK_CODE, MouseMoveTo, YijianshuInit, MouseLeftDown, MouseLeftDoubleClick, \
    RanSleep, MouseLeftClick, MouseLeftUp, MouseLeftDownFor, MouseMoveR
from superai.common import InitLog
from superai.flannfind import Picture, GetImgDir
from superai.gameapi import GetMenInfo, GameApiInit, FlushPid, GetSkillObj, idxkeymap

import time
import logging

logger = logging.getLogger(__name__)

skillScene = Picture(GetImgDir() + "/skillscene.png")
skillSceneLearn = Picture(GetImgDir() + "skillscene_learn.png")

# 技能对应的技能栏位置
idxposmap = {
    0: (600, 575), 1: (635, 575), 2: (676, 575), 3: (700, 575), 4: (735, 575), 5: (765, 575),
    6: (600, 535), 7: (635, 535), 8: (675, 535), 9: (700, 535), 10: (735, 535), 11: (765, 535)
}


# 技能名称 + 对应的图片的包装
class OccupationSkill:
    def __init__(self, zhiye, name, nameEng):
        self.zhieye = zhiye
        self.name = name
        self.nameEng = nameEng
        self.picutre = Picture("%s/%s/%s.png" % (GetImgDir(), zhiye, nameEng), dw=550)


# 职业对应的加点策略
class Occupationkills:
    # 用转职后职业名称判断
    def __init__(self):
        meninfo = GetMenInfo()
        occupationbefore = meninfo.zhuanzhiqian
        occupationafter = meninfo.zhuanzhihou

        if occupationbefore in ["魔枪士"]:
            self.moqiangInit()

        if occupationbefore != occupationafter:
            if occupationafter in ["暗枪士"]:
                self.anqiangInit()

    # 删除必备技能
    def DelSkill(self, name):
        if self.learnstrategy:
            for v in self.learnstrategy:
                if v.name == name:
                    self.learnstrategy.remove(v)
                    return

    # 魔枪 (15级前)
    def moqiangInit(self):
        self.learnstrategy = []
        meninfo = GetMenInfo()
        if meninfo.level >= 1:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "刺击", "moqiangshi_ciji"))
        if meninfo.level >= 10:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "横扫", "moqiangshi_hengsao"))
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "扫堂枪", "moqiangshi_saotangqiang"))

    # 暗枪 (转职后)
    def anqiangInit(self):
        pass

    # 加技能点
    def AddSkillPoints(self):
        self.OpenSkillScene()
        logger.info("技能栏已经打开")

        for v in self.learnstrategy:
            logger.info("学习技能: %s" % v.name)
            pos = v.picutre.Pos()
            logger.info("移动到相对位置: (%d,%d)" % (pos[0], pos[1]))
            MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
            MouseLeftDownFor(1.0), RanSleep(0.3)

        logger.info("技能已点完毕")

        # 确认按钮
        learnpos = skillSceneLearn.Pos()
        MouseMoveTo(learnpos[0], learnpos[1]), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)
        MouseLeftClick(), RanSleep(0.3)

    # 打开技能栏
    def OpenSkillScene(self):
        # 技能栏窗口打开,一致后才返回
        while not skillScene.Match():
            logger.info("技能栏没有打开")
            PressKey(VK_CODE["k"]), RanSleep(0.5)
            if skillScene.Match():
                return True

    # 关闭技能栏
    def CloseSkillScene(self):
        # 技能栏窗口打开,一致后才返回
        while skillScene.Match():
            logger.info("技能栏打开")
            PressKey(VK_CODE["k"]), RanSleep(0.5)
            if skillScene.Match():
                return True

    # 不在技能策略中
    def IsInLearnStrategy(self, name):
        for v in self.learnstrategy:
            if v.name == name:
                return True
        return False

    # 不是必备技能拖出去
    def RemoveNotInStrategy(self):
        self.OpenSkillScene()

        curskills = GetSkillObj()
        for v in curskills:
            if not self.IsInLearnStrategy(v.name):
                logger.warning("技能: %s 不是当前应该用的技能,拖出去" % v.name)

                # 向上移动, 脱离
                pos = idxposmap[v.idx]
                MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
                MouseLeftDown(), RanSleep(0.3)
                MouseMoveTo(pos[0], pos[1] - 150), RanSleep(0.3)
                MouseLeftUp(), RanSleep(0.3)

    # 该位置是否有技能
    def HasPosHaveSkill(self, i):
        curskills = GetSkillObj()
        for v in curskills:
            if v.idx == i:
                return True
        return False

    # 获取空位置坐标
    def GetEmptyPosIdx(self):
        for i in range(12):
            if not self.HasPosHaveSkill(i):
                return i

    # 是否装备了技能
    def HasEquipSkill(self, name):
        curskills = GetSkillObj()
        for v in curskills:
            if v.name == name:
                return True
        return False

    # 是必备技能找个空位置拖进来
    def EquipSkillInStrategy(self):
        self.OpenSkillScene()

        for v in self.learnstrategy:
            if not self.HasEquipSkill(v.name):
                idx = self.GetEmptyPosIdx()
                destpos = idxposmap[idx]

                logger.info("技能: %s 没有装备 位置: %d 有空位 (%d, %d)", v.name, idx, destpos[0], destpos[1])

                srcpos = v.picutre.Pos()
                MouseMoveTo(srcpos[0], srcpos[1]), RanSleep(0.3)
                MouseLeftDown(), RanSleep(0.3)
                MouseMoveR(10, 10), RanSleep(0.3)
                MouseMoveTo(destpos[0], destpos[1]), RanSleep(0.3)
                MouseLeftUp(), RanSleep(0.3)


def main():
    InitLog()
    GameApiInit()
    FlushPid()
    YijianshuInit()
    GameWindowToTop()

    oc = Occupationkills()
    oc.AddSkillPoints()
    oc.RemoveNotInStrategy()
    oc.EquipSkillInStrategy()


if __name__ == '__main__':
    main()
