import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from superai.gameapi import GetMenInfo, GetRemaindPilao


def GetBanzhuanDItu():
    meninfo = GetMenInfo()
    if meninfo.level <= 5:
        return "雷鸣废墟"
    elif meninfo.level <= 8:
        return "猛毒雷鸣废墟"
    elif meninfo.level <= 11:
        return "冰霜幽暗密林"
    elif meninfo.level <= 13:
        return "格拉卡"
    elif meninfo.level <= 15:
        return "烈焰格拉卡"
    elif meninfo.level <= 17:
        return "暗黑雷鸣废墟"
    elif meninfo.level <= 18:
        return "龙人之塔"
    elif meninfo.level <= 19:
        return "人偶玄关"
    elif meninfo.level <= 20:
        return "石巨人塔"
    elif meninfo.level <= 21:
        return "黑暗悬廊"
    elif meninfo.level <= 22:
        return "城主宫殿"
    elif meninfo.level <= 23:
        return "悬空城"
    elif meninfo.level <= 24:
        return "GBL教的神殿"
    elif meninfo.level <= 25:
        return "树精丛林"
    elif meninfo.level <= 26:
        return "炼狱"
    elif meninfo.level <= 27:
        return "极昼"
    elif meninfo.level <= 28:
        return "第一脊椎"
    elif meninfo.level <= 29:
        return "第二脊椎"
    elif meninfo.level <= 30:
        return "浅栖之地"
    elif meninfo.level <= 31:
        return "蜘蛛洞穴"
    elif meninfo.level <= 32:
        return "蜘蛛王国"
    elif meninfo.level <= 33:
        return "英雄冢"
    elif meninfo.level <= 34:
        return "暗精灵墓地"
    elif meninfo.level <= 35:
        return "熔岩穴"
    elif meninfo.level <= 36:
        return "暴君的祭坛"
    elif meninfo.level <= 37:
        return "黄金矿洞"
    elif meninfo.level <= 38:
        return "远古墓穴深处"
    elif meninfo.level <= 39:
        return "远古墓穴深处"
    elif meninfo.level <= 40:
        return "山脊"
    elif meninfo.level <= 41:
        return "雪山丛林"
    elif meninfo.level <= 42:
        return "冰心少年"
    elif meninfo.level <= 43:
        return "利库天井"
    elif meninfo.level <= 44:
        return "白色废墟"
    elif meninfo.level <= 45:
        return "布万加的修炼场"
    elif meninfo.level <= 46:
        return "绿都格罗兹尼"
    elif meninfo.level <= 47:
        return "堕落的盗贼"
    elif meninfo.level <= 48:
        return "迷乱之村哈穆林"
    elif meninfo.level <= 49:
        return "血蝴蝶之舞"
    elif meninfo.level <= 50:
        return "炽晶森林"
    elif meninfo.level <= 51:
        return "冰晶森林"
    elif meninfo.level <= 52:
        return "水晶矿脉"
    elif meninfo.level <= 53:
        return "幽冥监狱"
    elif meninfo.level <= 54:
        return "蘑菇庄园"
    elif meninfo.level <= 55:
        return "蚁后的巢穴"
    elif meninfo.level <= 56:
        return "腐烂之地"
    elif meninfo.level <= 57:  # TODO
        return "蚁后的巢穴"
    elif meninfo.level <= 58:  # TODO
        return "蚁后的巢穴"
    elif meninfo.level <= 59:
        return "人鱼的国度"
    elif meninfo.level <= 60:
        return "GBL女神殿"
    elif meninfo.level <= 61:
        return "树精繁殖地"
    elif meninfo.level <= 62:
        if GetRemaindPilao() >= 8:
            return "天空岛"
        else:
            return "树精繁殖地"
    elif meninfo.level <= 63:
        return "根特外围"
    elif meninfo.level <= 64:
        return "根特东门"
    elif meninfo.level <= 65:
        return "根特南门"
    elif meninfo.level <= 66:
        return "根特北门"
    elif meninfo.level <= 67:
        return "根特防御战"
    elif meninfo.level <= 68:
        return "夜间袭击站"
    elif meninfo.level <= 69:
        return "夜间袭击站"
    elif meninfo.level <= 70:
        return "夜间袭击站"
    elif meninfo.level <= 71:
        return "列车上的海贼"
    elif meninfo.level <= 72:
        return "夺回西部线"
    elif meninfo.level <= 73:
        return "雾都赫伊斯"
    elif meninfo.level <= 74:
        return "阿登高地"
    elif meninfo.level <= 75:
        return "格兰之火"
    elif meninfo.level <= 76:
        return "瘟疫之源"
    elif meninfo.level <= 77:
        return "卡勒特之刃"
    elif meninfo.level <= 78:
        return "绝密区域"
    elif meninfo.level <= 79:
        return "绝密区域"
    elif meninfo.level <= 80:
        return "凛冬"
    elif meninfo.level <= 81:
        return '普鲁兹发电站'
    elif meninfo.level <= 82:
        return "特伦斯发电站"
    elif meninfo.level <= 85:
        return "格蓝迪发电站"
    elif meninfo.level <= 86:
        return "倒悬的瞭望台"
    elif meninfo.level <= 87:
        return "卢克的聚光镜"
    elif meninfo.level <= 88:
        return "钢铁之臂"
    elif meninfo.level <= 89:
        return "能源熔炉"
    elif meninfo.level <= 90:
        return "光之舞会"

def main():
    pass


if __name__ == '__main__':
    main()
