import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.yijianshu import PressKey, VK_CODE, MouseMoveTo, YijianshuInit, MouseLeftDown, RanSleep, MouseLeftClick, \
    MouseLeftUp, MouseLeftDownFor, MouseMoveR, MouseWheel, KongjianSleep, LanSleep, MouseRightDownFor, ShiftLeft, \
    ShiftRight
from superai.common import InitLog, GameWindowToTop
from superai.flannfind import Picture, GetImgDir
from superai.gameapi import GetMenInfo, GameApiInit, FlushPid, GetSkillObj, Clear, IsSkillLearned

import logging

logger = logging.getLogger(__name__)

skillScene = Picture(GetImgDir() + "skillscene.png")
skillSceneLearn = Picture(GetImgDir() + "skillscene_learn.png")
skillstore = Picture(GetImgDir() + "skill_store.png")

# 技能对应的技能栏位置
idxposmap = {
    0: (600, 575), 1: (635, 575), 2: (676, 575), 3: (700, 575), 4: (735, 575), 5: (765, 575),
    6: (600, 535), 7: (635, 535), 8: (675, 535), 9: (700, 535), 10: (735, 535), 11: (765, 535)
}

wulibaoji, wilibeiji, mofabaoji, mofabeiji = (-173, 103), (-93, 103), (-130, 103), (-49, 103)

WULI = 0
MOFA = 1


# 技能名称 + 对应的图片的包装
class OccupationSkill:
    def __init__(self, zhiye, name, nameEng, beidong=False):
        self.zhieye = zhiye
        self.name = name
        self.nameEng = nameEng

        self.picutre = Picture("%s/%s/%s" % (GetImgDir(), zhiye, nameEng), dw=550)

        if name == "烈日气息":
            self.picutre = Picture("%s/%s/%s" % (GetImgDir(), zhiye, nameEng), dx=343, dy=0, dw=85, dh=600)  # TODO

        self.beidong = beidong

    def GetPos(self):
        pos = self.picutre.Pos()
        pos = [pos[0], pos[1]]
        if self.name == "烈日气息":
            pos[0] = pos[0] + 343
        return pos


# 职业对应的加点策略
class Occupationkills:
    # 用转职后职业名称判断
    def __init__(self):
        meninfo = GetMenInfo()
        occupationbefore = meninfo.zhuanzhiqian
        occupationafter = meninfo.zhuanzhihou

        self.deletedskills = []
        self.AttackType = None

        if occupationbefore in ["魔枪士"]:
            self.moqiangInit()
            if occupationafter in ["暗枪士", "狂怒恶鬼", "幽影夜神"]:
                self.anqiangInit()
        elif occupationbefore in ["圣职者"]:
            self.shengzhiInit()
            if occupationafter in ["诱魔者", "断罪者", "救世者"]:
                self.youmozheInit()
        elif occupationbefore in ["守护者"]:
            self.shouhuInit()
            if occupationafter in ["帕拉丁", "曙光", "破晓女神"]:
                self.paladingInit()
        elif occupationbefore in ["格斗家"]:
            self.gedouInit()
            if occupationafter in ["气功师", "百花缭乱", "念帝"]:
                self.nvqigongInit()
        elif occupationbefore in ["鬼剑士"]:
            self.guijianshiInit()
            if occupationafter in ["剑影", "夜刀神", "夜见罗刹"]:
                self.jianyingInit()
        elif occupationbefore in ["枪剑士"]:
            self.qiangjianshiInit()
            if occupationafter in ["源能专家", "源力掌控者", "未来开拓者"]:
                self.yuannengInit()
        else:
            logger.warning("还未支持的职业 %s" % occupationafter)
            return

    # 删除必备技能
    def DelSkill(self, name):
        if self.learnstrategy:
            for v in self.learnstrategy:
                if v.name == name:
                    self.deletedskills.append(v)
                    self.learnstrategy.remove(v)
                    return

    # 枪剑士
    def qiangjianshiInit(self):
        self.learnstrategy = []
        meninfo = GetMenInfo()
        if meninfo.level >= 1:
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "穿透射击", "qiangjianshi_chuantousheji.png"))
        if meninfo.level >= 5:
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "重劈", "qiangjianshi_zhongpi.png"))
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "源光斩", "qiangjianshi_yuanguangzhan.png"))
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "瞬击", "qiangjianshi_shunji.png"))

    # 源能专家
    def yuannengInit(self):
        self.AttackType = MOFA
        meninfo = GetMenInfo()
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "旋转源能波", "qiangjianshi_xuanzhuanyuannnengbo.png"))
        if meninfo.level >= 20:
            self.DelSkill("重劈")

            self.learnstrategy.append(
                OccupationSkill("qiangjianshi", "源力剑精通", "yuanneng_jianjingtong.png", beidong=True))
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "镭射源能枪", "yuanneng_leishe.png"))
        if meninfo.level >= 25:
            self.DelSkill("穿透射击")
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "细胞弱化", "yuanneng_xibaoruohua.png", beidong=True))
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "源能波刃", "yuanneng_yuannengboren.png"))
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "能量飞鱼弹", "yuanneng_nengliangfeiyudan.png"))
        if meninfo.level >= 30:
            self.DelSkill("瞬击")
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "源能应用", "yuanneng_yuannengyingyong.png"))
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "脉冲斩", "yuanneng_maichongzhan.png"))
        if meninfo.level >= 35:
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "电磁领域", "yuanneng_diancilingyu.png"))
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "引力源光弹", "yuanneng_yinliyuannengdan.png"))
        if meninfo.level >= 40:
            self.DelSkill("源光斩")
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "光裂斩", "yuanneng_guangliezhan.png"))
        if meninfo.level >= 45:
            self.learnstrategy.append(OccupationSkill("qiangjianshi", "光导裂地斩", "yuanneng_guangdaoliedizhan.png"))

    # 鬼剑士
    def guijianshiInit(self):
        self.learnstrategy = []
        meninfo = GetMenInfo()
        if meninfo.level >= 1:
            self.learnstrategy.append(OccupationSkill("guijianshi", "鬼斩", "guijianshi_guizhan.png"))
            self.learnstrategy.append(OccupationSkill("guijianshi", "上挑", "guijianshi_shangtiao.png", beidong=True))
        if meninfo.level >= 10:
            self.learnstrategy.append(OccupationSkill("guijianshi", "裂波斩", "guijianshi_liebozhan.png"))
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("guijianshi", "鬼连斩", "guijianshi_guilianzhan.png"))
            self.learnstrategy.append(OccupationSkill("guijianshi", "地裂 · 波动剑", "guijianshi_bodongjian.png"))

    # 剑影
    def jianyingInit(self):
        self.AttackType = WULI
        meninfo = GetMenInfo()
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("guijianshi", "鬼步", "jianying_guibu.png"))

        if meninfo.level >= 20:
            self.DelSkill("上挑")
            self.learnstrategy.append(
                OccupationSkill("guijianshi", "剑影太刀精通", "jianying_taidaojingtong.png", beidong=True))
            self.learnstrategy.append(OccupationSkill("guijianshi", "幻鬼 : 一闪", "jianying_huanguiyishan.png"))
        if meninfo.level >= 25:
            self.DelSkill("鬼斩")
            self.DelSkill("裂波斩")
            self.learnstrategy.append(
                OccupationSkill("guijianshi", "幻鬼之力", "jianying_huanguizhili.png", beidong=True))

            self.learnstrategy.append(OccupationSkill("guijianshi", "鬼连牙", "jianying_guilianya.png"))
            self.learnstrategy.append(OccupationSkill("guijianshi", "幻鬼 : 连斩", "jianying_huanguilianzhan.png"))
        if meninfo.level >= 30:
            self.learnstrategy.append(OccupationSkill("guijianshi", "双魂共鸣", "jianying_shuanghungongming.png"))
            self.learnstrategy.append(
                OccupationSkill("guijianshi", "鬼连斩 : 极", "jianying_guilianzhanji.png", beidong=True))
            self.learnstrategy.append(OccupationSkill("guijianshi", "共鸣 : 离魂一闪", "jianying_lihunyishan.png"))
        if meninfo.level >= 35:
            self.learnstrategy.append(OccupationSkill("guijianshi", "魂破斩", "jianying_hunpozhan.png"))
            self.learnstrategy.append(OccupationSkill("guijianshi", "共鸣 : 鬼灵斩", "jianying_guilingzhan.png"))
            self.DelSkill("地裂 · 波动剑")
        if meninfo.level >= 40:
            self.learnstrategy.append(OccupationSkill("guijianshi", "幻鬼 : 回天", "jianying_huitian.png"))
        if meninfo.level >= 45:
            self.learnstrategy.append(OccupationSkill("guijianshi", "冥灵断魂斩", "jianying_minlingdunhunzhan.png"))

    # 格斗家
    def gedouInit(self):
        self.learnstrategy = []
        meninfo = GetMenInfo()
        if meninfo.level >= 1:
            self.learnstrategy.append(OccupationSkill("gedoujia", "前踢", "gedou_qianti.png"))
        if meninfo.level >= 5:
            self.learnstrategy.append(OccupationSkill("gedoujia", "下段踢", "gedou_xiaduanti.png"))
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("gedoujia", "背摔", "gedou_beishuai.png"))

    # 女气功
    def nvqigongInit(self):
        self.AttackType = MOFA
        meninfo = GetMenInfo()
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("gedoujia", "光之兵刃", "qigong_guangzhibingren.png"))
            self.learnstrategy.append(OccupationSkill("gedoujia", "雷霆背摔", "qidong_leitingbeishuai.png", beidong=True))
        if meninfo.level >= 20:
            self.learnstrategy.append(OccupationSkill("gedoujia", "分身", "gedou_fenshen.png"))
            self.learnstrategy.append(OccupationSkill("gedoujia", "幻影爆碎", "qigong_huanyingbaosui.png", beidong=True))
            self.learnstrategy.append(OccupationSkill("gedoujia", "烈日气息", "qigong_lieriqixi.png"))
        if meninfo.level >= 30:
            self.learnstrategy.append(OccupationSkill("gedoujia", "念气环绕", "qigong_nianqihuanrao.png", beidong=True))
        if meninfo.level >= 35:
            self.learnstrategy.append(OccupationSkill("gedoujia", "狮子吼", "qigong_shizihou.png"))
        if meninfo.level >= 40:
            self.learnstrategy.append(OccupationSkill("gedoujia", "念兽 : 龙虎啸", "qigong__longhuxiao.png"))
        if meninfo.level >= 45:
            self.learnstrategy.append(OccupationSkill("gedoujia", "螺旋念气场", "qigong_luoxuannianqi.png"))

    # 守护者
    def shouhuInit(self):
        self.learnstrategy = []
        meninfo = GetMenInfo()
        if meninfo.level >= 1:
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "强踢", "shouhu_qiangti.png"))
        if meninfo.level >= 5:
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "命运之轮", "shouhu_mingyunlun.png", beidong=True))
        if meninfo.level >= 10:
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "致命突刺", "shouhu_zhimingci.png", beidong=True))

    # 帕拉丁
    def paladingInit(self):
        self.AttackType = WULI

        meninfo = GetMenInfo()
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "神光冲击", "palading_shenguangchongji.png"))
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "神光连斩", "palading_shenguanglianzhan.png"))
            self.learnstrategy.append(
                OccupationSkill("shouhuzhe", "天使降临", "palading_tianshijianglin.png", beidong=True))
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "天使光翼", "palading_tianshizhiyi.png", beidong=True))
        if meninfo.level >= 20:
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "圣盾突击", "palading_shengduntiji.png"))
            self.DelSkill("命运之轮")
        if meninfo.level >= 25:
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "神光喷涌", "palading_shenguangpenyong.png"))
        if meninfo.level >= 30:
            self.DelSkill("强踢")
            self.DelSkill("致命突刺")
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "神光盾击", "palading_shenguangdunji.png"))
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "烈光", "palading_lieguang.png"))
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "信仰之念", "palding_xinyangzhinian.png"))
        if meninfo.level >= 35:
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "神光闪耀", "palading_shenguangshanyao.png"))
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "神光闪影击", "palading_shenguangshanyingji.png"))
        if meninfo.level >= 40:
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "神罚之锤", "palading_shenfazhichui.png"))
        if meninfo.level >= 45:
            self.learnstrategy.append(OccupationSkill("shouhuzhe", "神光之跃", "palading_shenzhiguangyue.png"))

    # 圣职
    def shengzhiInit(self):
        self.learnstrategy = []
        meninfo = GetMenInfo()

        if meninfo.level >= 1:
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "审判捶击", "shengzhi_shengpanchuiji.png"))
        if meninfo.level >= 5:
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "钩颈斩", "shengzhi_goujingzhan.png"))
        if meninfo.level >= 10:
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "罪业加身", "shengzhi_zuiyejiashen.png"))
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "冲刺斩", "shengzhi_chongcizhan.png"))

    # 四姨
    def youmozheInit(self):
        self.AttackType = MOFA
        meninfo = GetMenInfo()
        if meninfo.level >= 15:
            self.learnstrategy.append(
                OccupationSkill("shengzhizhe", "负罪者镰刀精通", "youmozhe_liandaojingtong.png", beidong=True))
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "罪业诱惑", "youmozhe_zuiyeyouhuo.png", beidong=True))
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "双重切割", "youmozhe_shuangchongqiege.png"))
        if meninfo.level >= 20:
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "断头台", "youmozhe_duantoutai.png"))
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "七宗罪", "youmozhe_qizongzui.png"))
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "欲望之手", "youmozhe_yuwangzhishou.png"))
        if meninfo.level >= 25:
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "傲慢之堕", "youmozhe_aomanzhiduo.png"))
        if meninfo.level >= 30:
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "屠戮回旋斩", "youmozhe_tuchuolunhuizhan.png"))
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "怠惰之息", "youmozhe_daiduozhixi.png"))

            self.DelSkill("审判捶击")
            self.DelSkill("钩颈斩")
            self.DelSkill("罪业加身")
            self.DelSkill("冲刺斩")
        if meninfo.level >= 35:
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "贪婪之刺", "youmozhe_tanlanzhici.png"))
        if meninfo.level >= 40:
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "杀戮战镰", "youmozhe_shaluzhanlian.png"))
        if meninfo.level >= 45:
            self.learnstrategy.append(OccupationSkill("shengzhizhe", "愤怒之袭", "youmozhe_fennuzhixi.png"))

    # 魔枪
    def moqiangInit(self):
        self.learnstrategy = []
        meninfo = GetMenInfo()
        if meninfo.level >= 1:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "刺击", "moqiangshi_ciji.png"))
        if meninfo.level >= 10:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "横扫", "moqiangshi_hengsao.png"))
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "扫堂枪", "moqiangshi_saotangqiang.png"))

    # 暗枪
    def anqiangInit(self):
        self.AttackType = MOFA

        meninfo = GetMenInfo()
        if meninfo.level >= 15:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "侵蚀之矛", "anqiang_qinshizhimao.png"))
            self.learnstrategy.append(OccupationSkill("moqiangshi", "双重投射", "anqiang_shuangchongtoushe.png"))
            self.learnstrategy.append(OccupationSkill("moqiangshi", "暗蚀", "anqiang_anshi.png", beidong=True))
        if meninfo.level >= 20:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "暗矛投射", "anqiang_anmaotoushe.png"))
            self.learnstrategy.append(OccupationSkill("moqiangshi", "暗矛精通", "anqiang_anmaojingtong.png", beidong=True))
        if meninfo.level >= 25:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "黑暗枪雨", "anqiang_heianqiangyu.png"))
            self.learnstrategy.append(OccupationSkill("moqiangshi", "暗矛贯穿", "anqiangshi_anmaoguanchuan.png"))
            self.learnstrategy.append(OccupationSkill("moqiangshi", "黑暗化身", "anqiang_heianhuashen.png"))
        if meninfo.level >= 30:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "黑蚀葬礼", "anqiang_heishizangli.png"))
            self.learnstrategy.append(OccupationSkill("moqiangshi", "绝望枪", "anqiang_juewangqiang.png"))
            self.DelSkill("刺击")
            self.DelSkill("横扫")
            self.DelSkill("扫堂枪")
        if meninfo.level >= 35:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "暗蚀螺旋枪", "anqiang_anheiluoxuanqiang.png"))
            self.learnstrategy.append(OccupationSkill("moqiangshi", "连锁侵蚀", "anqiang_liansuoqinshi.png"))
        if meninfo.level >= 40:
            self.learnstrategy.append(OccupationSkill("moqiangshi", "坠蚀之雨", "anqiang_zuishizhiyu.png"))
        if meninfo.level >= 45:
            self.DelSkill("侵蚀之矛")
            self.DelSkill("双重投射")
            self.learnstrategy.append(OccupationSkill("moqiangshi", "暗蚀爆雷杀", "anqiang_anshibaoleisha.png"))
        if meninfo.level >= 50:
            self.learnstrategy.append(
                OccupationSkill("moqiangshi", "黑暗支配者", "anqiang_heianzhipeizhe.png", beidong=True))
            self.learnstrategy.append(OccupationSkill("moqiangshi", "无尽侵蚀 : 缚魂", "anqiang_wujinqinshi.png"))

    # 找不到图片,滚轮用
    def FindedPic(self, pic):
        pos = pic.Pos()
        if pos[0] == 0 and pos[1] == 0:
            return False
        return True

    # 有技能需要忘记
    def NeedWangji(self):
        for v in self.deletedskills:
            if IsSkillLearned(v.name):
                return True
        return False

    # 加技能点
    def AddSkillPoints(self):
        if not self.OpenSkillScene():
            logger.warning("打开技能栏失败")
            return

        logger.info("技能栏已经打开")

        needLearn = False
        if self.NeedWangji():
            logger.info("去掉不需要技能的加点")
            MouseMoveTo(536, 360), KongjianSleep()
            MouseWheel(30), KongjianSleep()

            for v in self.deletedskills:
                logger.info("开始忘记技能: %s", v.name)

                if not IsSkillLearned(v.name):
                    logger.info("技能: %s 不需要忘记" % v.name)
                else:

                    for i in range(3):
                        if self.FindedPic(v.picutre):
                            break
                        MouseMoveTo(536, 360), KongjianSleep()
                        MouseWheel(-3), KongjianSleep()

                    if not self.FindedPic(v.picutre):
                        logger.warning("找不到技能: %s" % v.name)
                        continue

                    pos = v.GetPos()
                    needLearn = True
                    logger.info("忘记,移动到相对位置: (%d,%d)" % (pos[0], pos[1]))
                    MouseMoveTo(pos[0], pos[1]), KongjianSleep()
                    ShiftRight(), KongjianSleep()

        logger.info("开始学习技能")
        MouseMoveTo(536, 360), KongjianSleep()
        MouseWheel(30), KongjianSleep()

        if self.AttackType is not None:
            pos = skillScene.Pos()
            if pos is not None or pos != (0, 0):
                tolearnpos = []
                if self.AttackType == MOFA:
                    tolearnpos.append((pos[0] + mofabaoji[0], pos[1] + mofabaoji[1]))
                    tolearnpos.append((pos[0] + mofabeiji[0], pos[1] + mofabeiji[1]))
                elif self.AttackType == WULI:
                    tolearnpos.append((pos[0] + wulibaoji[0], pos[1] + wulibaoji[1]))
                    tolearnpos.append((pos[0] + wilibeiji[0], pos[1] + wilibeiji[1]))

                for pos in tolearnpos:
                    w, h = 50, 60
                    halfw, halfh = w // 2, h // 2
                    cannotLearn = Picture(GetImgDir() + "cannotlearn.png", dx=pos[0] - halfw, dy=pos[1] - halfh, dw=w,
                                          dh=h)
                    jingtong = Picture(GetImgDir() + "jingtong.png", dx=pos[0] - halfw, dy=pos[1] - halfh, dw=w, dh=h)

                    if cannotLearn.Match() or jingtong.Match():
                        logger.warning("暴击不需要学习")
                    else:
                        needLearn = True
                        MouseMoveTo(pos[0], pos[1]), KongjianSleep()
                        ShiftLeft(), KongjianSleep()
            else:
                logger.warning("没有找到技能栏")

        for v in self.learnstrategy:

            logger.info("学习技能: %s" % v.name)

            for i in range(3):
                if self.FindedPic(v.picutre):
                    break
                MouseMoveTo(536, 360), KongjianSleep()
                MouseWheel(-3), KongjianSleep()

            if not self.FindedPic(v.picutre):
                logger.warning("找不到技能: %s" % v.name)
                continue

            pos = v.GetPos()

            # w, h = 30, 25
            w, h = 50, 60
            halfw, halfh = w // 2, h // 2
            cannotLearn = Picture(GetImgDir() + "cannotlearn.png", dx=pos[0] - halfw, dy=pos[1] - halfh, dw=w, dh=h)
            jingtong = Picture(GetImgDir() + "jingtong.png", dx=pos[0] - halfw, dy=pos[1] - halfh, dw=w, dh=h)
            if cannotLearn.Match() or jingtong.Match():
                logger.info("技能: %s 不需要学习", v.name)
            else:
                needLearn = True
                logger.info("学习,移动到相对位置: (%d,%d)" % (pos[0], pos[1]))
                MouseMoveTo(pos[0], pos[1]), KongjianSleep()
                ShiftLeft(), KongjianSleep()

            # MouseMoveR(- (30 // 2 - 2), 0), KongjianSleep()

        logger.info("技能已学习完毕")

        if needLearn:
            # 确认按钮
            learnpos = skillSceneLearn.Pos()
            MouseMoveTo(learnpos[0], learnpos[1]), KongjianSleep()
            MouseLeftClick(), RanSleep(0.3)
            MouseLeftClick(), KongjianSleep()

    # 打开技能栏
    def OpenSkillScene(self):
        # Clear() 不要再这里. 因为连续3次 (加点,脱进来,脱出去,太浪费时间了)
        if not skillScene.Match():
            logger.info("打开技能栏")
            PressKey(VK_CODE["k"]), LanSleep()
        return skillScene.Match()

    # 关闭技能栏
    def CloseSkillScene(self):
        while skillScene.Match():
            logger.info("关闭技能栏")
            PressKey(VK_CODE["esc"]), KongjianSleep()

            if skillstore.Match():
                PressKey(VK_CODE["enter"]), KongjianSleep()

    # 在技能策略中
    def IsInLearnStrategy(self, name):
        for v in self.learnstrategy:
            if v.name == name:
                return True
        return False

    # 是否是被动
    def IsBeidong(self, name):
        for v in self.learnstrategy:
            if v.name == name:
                if v.beidong:
                    return True
        return False

    # 不是必备技能拖出去
    def RemoveNotInStrategy(self):
        if not self.OpenSkillScene():
            logger.warning("打开技能栏失败")
            return

        curskills = GetSkillObj()
        for v in curskills:
            if not self.IsInLearnStrategy(v.name) or self.IsBeidong(v.name):
                logger.warning("技能: %s 不是当前应该用的技能,拖出去" % v.name)

                # 向上移动, 脱离
                pos = idxposmap[v.idx]
                MouseMoveTo(pos[0], pos[1]), KongjianSleep()
                MouseLeftDown(), KongjianSleep()
                MouseMoveTo(pos[0], pos[1] - 150), KongjianSleep()
                MouseLeftUp(), KongjianSleep()

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
        if not self.OpenSkillScene():
            logger.warning("打开技能栏失败")
            return

        MouseMoveTo(536, 360), KongjianSleep()
        MouseWheel(30), KongjianSleep()

        for v in self.learnstrategy:
            if v.beidong:
                continue

            if not self.HasEquipSkill(v.name):
                idx = self.GetEmptyPosIdx()
                destpos = idxposmap[idx]
                logger.info("技能: %s 没有装备 位置: %d 有空位 (%d, %d)", v.name, idx, destpos[0], destpos[1])

                for i in range(3):
                    if self.FindedPic(v.picutre):
                        break
                    MouseMoveTo(536, 360), KongjianSleep()
                    MouseWheel(-3), KongjianSleep()

                if not self.FindedPic(v.picutre):
                    logger.warning("找不到技能: %s" % v.name)
                    continue

                srcpos = v.GetPos()

                MouseMoveTo(srcpos[0], srcpos[1]), KongjianSleep()
                MouseLeftDown(), KongjianSleep()
                MouseMoveR(10, 10), KongjianSleep()
                MouseMoveTo(destpos[0], destpos[1]), KongjianSleep()
                MouseLeftUp(), KongjianSleep()


def main():
    InitLog()
    if not GameApiInit():
        sys.exit()
    FlushPid()
    if not YijianshuInit():
        sys.exit()
    GameWindowToTop()

    print(skillstore.Match())

    # oc = Occupationkills()
    # oc.AddSkillPoints()
    # oc.RemoveNotInStrategy()
    # oc.EquipSkillInStrategy()
    # oc.CloseSkillScene()


if __name__ == '__main__':
    main()
