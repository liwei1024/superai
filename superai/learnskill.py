import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.yijianshu import PressKey, VK_CODE, MouseMoveTo, YijianshuInit, MouseLeftDown, RanSleep, MouseLeftClick, \
    MouseLeftUp, MouseLeftDownFor, MouseMoveR, MouseWheel
from superai.common import InitLog, GameWindowToTop
from superai.flannfind import Picture, GetImgDir
from superai.gameapi import GetMenInfo, GameApiInit, FlushPid, GetSkillObj

import logging

logger = logging.getLogger(__name__)

skillScene = Picture(GetImgDir() + "skillscene.png")
skillSceneLearn = Picture(GetImgDir() + "skillscene_learn.png")

# 技能对应的技能栏位置
idxposmap = {
    0: (600, 575), 1: (635, 575), 2: (676, 575), 3: (700, 575), 4: (735, 575), 5: (765, 575),
    6: (600, 535), 7: (635, 535), 8: (675, 535), 9: (700, 535), 10: (735, 535), 11: (765, 535)
}


# 技能名称 + 对应的图片的包装
class OccupationSkill:
    def __init__(self, zhiye, name, nameEng, beidong=False):
        self.zhieye = zhiye
        self.name = name
        self.nameEng = nameEng
        self.picutre = Picture("%s/%s/%s" % (GetImgDir(), zhiye, nameEng), dw=550)
        self.beidong = beidong

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
            self.learnstrategy.append(OccupationSkill("moqiangshi", "刺击", "moqiangshi_ciji.png"))
        if meninfo.level >= 10:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "横扫", "moqiangshi_hengsao.png"))
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "扫堂枪", "moqiangshi_saotangqiang.png"))

    # 暗枪 (转职后)
    def anqiangInit(self):
        meninfo = GetMenInfo()
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "侵蚀之矛", "anqiang_qinshizhimao.png"))
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "双重投射", "anqiang_shuangchongtoushe.png"))
            self.learnstrategy.append(OccupationSkill("moqiangshi", "暗蚀", "anqiang_anshi.png", beidong=True))
        if meninfo.level >= 20:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "暗矛投射", "anqiang_anmaotoushe.png"))
            self.learnstrategy.append(OccupationSkill("moqiangshi", "暗矛精通", "anqiang_anmaojingtong.png", beidong=True))

    # 加技能点
    def AddSkillPoints(self):
        self.OpenSkillScene()
        logger.info("技能栏已经打开")

        MouseMoveTo(309, 280), RanSleep(0.3)
        MouseWheel(30), RanSleep(0.3)

        for v in self.learnstrategy:
            logger.info("学习技能: %s" % v.name)
            pos = v.picutre.Pos()

            # w, h = 30, 25
            w, h = 50, 45
            halfw, halfh = w // 2, h // 2
            cannotLearn = Picture(GetImgDir() + "cannotlearn.png", dx=pos[0] - halfw, dy=pos[1] - halfh, dw=w, dh=h)

            if cannotLearn.Match():
                logger.info("技能: %s 不需要学习", v.name)
                continue

            logger.info("移动到相对位置: (%d,%d)" % (pos[0], pos[1]))
            MouseMoveTo(pos[0], pos[1]), RanSleep(0.3)
            MouseLeftDownFor(1.0), RanSleep(0.3)

        logger.info("技能已点完毕")

        # 确认按钮
        learnpos = skillSceneLearn.Pos()
        MouseMoveTo(learnpos[0], learnpos[1]), RanSleep(0.2)
        MouseLeftClick(), RanSleep(0.2)
        MouseLeftClick(), RanSleep(0.2)

    # 打开技能栏
    def OpenSkillScene(self):
        while not skillScene.Match():
            logger.info("打开技能栏")
            PressKey(VK_CODE["k"]), RanSleep(0.5)

    # 关闭技能栏
    def CloseSkillScene(self):
        while skillScene.Match():
            logger.info("关闭技能栏")
            PressKey(VK_CODE["k"]), RanSleep(0.5)

    # 在技能策略中
    def IsInLearnStrategy(self, name):
        for v in self.learnstrategy:
            if v.name == name:
                return True
        return False

    # 不是必备技能拖出去
    def RemoveNotInStrategy(self):
        self.OpenSkillScene(), RanSleep(0.5)

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
        self.OpenSkillScene(), RanSleep(0.5)

        for v in self.learnstrategy:
            if v.beidong:
                continue

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
    oc.CloseSkillScene()


if __name__ == '__main__':
    main()
