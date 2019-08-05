import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

# a* 8方位
import copy

from superai.astartdemo import manhattanDistance, idxTohw, hwToidx
from superai.common import Log
from superai.gameapi import FlushPid, GameApiInit, GetMenInfo
from superai.obstacle import GetGameObstacleData, drawAll


class AStartPaths:

    def initobstacle(self, d):
        # 初始化
        # 1. 地形二叉树 2. 地形数组 3. 地形额外  使用 16 * 12 长宽的格子
        # 4. 障碍物  使用特定长宽的格子
        self.mapCellWLen = d.mapw // 0x10
        self.mapCellHLen = d.maph // 0xc
        self.cellnum = self.mapCellWLen * self.mapCellHLen
        self.dixing = [False] * self.cellnum

        Log("self.mapCellWLen: %d self.mapCellHLen: %d \n" % (self.mapCellWLen, self.mapCellHLen))

        for obj in d.dixingtree:
            cellX = obj.x // 0x10
            cellY = obj.y // 0xc
            self.dixing[cellY * self.mapCellWLen + cellX] = True

        for obj in d.dixingvec:
            cellX = obj.x // 0x10
            cellY = obj.y // 0xc
            self.dixing[cellY * self.mapCellWLen + cellX] = True

        for obj in d.dixingextra:
            cellX = obj.x // 0x10
            cellY = obj.y // 0xc
            self.dixing[cellY * self.mapCellWLen + cellX] = True

        self.obstacles = copy.deepcopy(d.obstacles)

    def __init__(self, d, start, end, img):
        self.img = img

        self.initobstacle(d)

        # 初始化 A * 算法数据
        # start end && 行走的路径使用 10 * 10 长宽的格子
        # 缺点是有误差 水平4个点, 垂直8个点
        self.manCellWLen = d.mapw // 10
        self.manCellHLen = d.maph // 10
        self.manCellnum = self.manCellHLen * self.manCellWLen

        self.closedSet = []
        self.openSet = [start]

        self.start = start
        self.end = end

        self.edgeTo = [0] * self.manCellnum
        self.marked = [False] * self.manCellnum

        # 实际距离
        self.gScore = [0] * self.manCellnum
        self.gScore[start] = 0

        # 估算到终点的距离
        self.fScore = [0] * self.manCellnum
        self.fScore[start] = manhattanDistance(idxTohw(start, self.manCellWLen), idxTohw(end, self.manCellWLen))

        self.astar()

    def DixingTouched(self, x, y):
        # 获取4个角点的0xc 0x10是否和 地形相交
        # checks = [
        #     (x * 10, y * 10),
        #     (x * 10, y * 10 + 10),
        #     (x * 10 + 10, y * 10),
        #     (x * 10 + 10, y * 10 + 10)
        # ]
        # for (x, y) in checks:
        #     cellx = x // 0x10
        #     celly = y // 0xC
        #     dixingidx = hwToidx(cellx, celly, self.mapCellWLen)
        #     if dixingidx >= len(self.dixing):
        #         return True
        #     if self.dixing[celly * self.mapCellWLen + cellx]:
        #         return True
        # return False
        pass

    def ObstacleTouched(self, x, y):

        # for v in self.obstacles:
        #     # 坐标在障碍物的范围之内
        #     halfw = int(v.w / 2)
        #     halfh = int(v.h / 2)
        #     if (v.x - halfw < x < v.x + halfw) and \
        #             (v.y - halfh < y < v.y + halfh):
        #         return True
        #
        # return False
        pass

    def GetAdjs(self, pos):
        # 获取八方位邻居格子. 根据地形和障碍数据过滤掉不必要的
        adjs = []

        posx, posy = idxTohw(pos, self.manCellWLen)

        # 上下左右. 左上,左下,右上,右下.
        checks = [
            (posx, posy - 1),
            (posx, posy + 1),
            (posx - 1, posy),
            (posx + 1, posy),
            (posx - 1, posy - 1),
            (posx - 1, posy + 1),
            (posx + 1, posy - 1),
            (posx + 1, posy + 1),
        ]

        for (adjx, adjy) in checks:
            if self.DixingTouched(adjx, adjy):
                continue

            if self.ObstacleTouched(adjx, adjy):
                continue

            adjs.append(hwToidx(adjx, adjy, self.manCellWLen))

        return adjs

    def astar(self):
        while len(self.openSet) > 0:
            current = min(self.openSet, key=lambda s: self.fScore[s])
            if current == self.end:
                return
            self.openSet.remove(current)
            self.closedSet.append(current)
            adjs = self.GetAdjs(current)
            for w in adjs:
                if w in self.closedSet:
                    continue
                # 实际距离
                tentativeScore = self.gScore[current] + manhattanDistance(idxTohw(current, self.manCellWLen),
                                                                          idxTohw(w, self.manCellWLen))
                if w not in self.openSet:
                    self.openSet.append(w)
                elif tentativeScore >= self.gScore[w]:  # 如果此遍历距离大于其他点遍历过去的距离则抛弃
                    continue

                self.edgeTo[w] = current
                self.marked[w] = True

                print("edgeTo ({},{}) -> ({},{})".format(current % self.manCellWLen, current // self.manCellWLen,
                                                         w % self.manCellWLen, w // self.manCellWLen))

                self.gScore[w] = tentativeScore
                self.fScore[w] = self.gScore[w] + manhattanDistance(idxTohw(w, self.manCellWLen),
                                                                    idxTohw(self.end, self.manCellWLen))
                print("fScore[%d] manhattan: %d" % (w, self.fScore[w]))

    def HasPathTo(self, v: int):
        return self.marked[v]

    def PathTo(self, v: int):
        result = []
        if not self.HasPathTo(v):
            return result

        x = v
        while x != self.start:
            result.append(x)
            x = self.edgeTo[x]
        result.append(self.start)
        return result


def drawCell(img, cellx, celly):
    zuoshang = (cellx * 10, celly * 10)
    youxia = (cellx * 10 + 10, celly * 10 + 10)
    cv2.rectangle(img, zuoshang, youxia, (0, 255, 0), -1)


def main():
    if GameApiInit():
        print("Init helpdll-xxiii.dll ok")
    else:
        print("Init helpdll-xxiii.dll err")
        exit(0)
    FlushPid()

    # (647,312,0) 血滴石

    d = GetGameObstacleData()

    print("w h : %d %d" % (d.mapw, d.maph))

    img = np.zeros((d.maph, d.mapw, 3), dtype=np.uint8)
    img[np.where(img == [0])] = [255]

    drawAll(img, d)

    wlen = d.mapw // 10
    meninfo = GetMenInfo()

    begincellx, begincelly = int(meninfo.x) // 10, int(meninfo.y) // 10
    endcellx, endcelly = 647 // 10, 312 // 10

    drawCell(img, begincellx, begincelly)
    drawCell(img, endcellx, endcelly)

    startidx = hwToidx(begincellx, begincelly, wlen)
    endidx = hwToidx(endcellx, endcelly, wlen)

    print("a* 寻径")
    astar = AStartPaths(d, startidx, endidx, img)
    paths = astar.PathTo(hwToidx(endcellx, endcelly, wlen))

    for v in reversed(paths):
        (cellx, celly) = idxTohw(v, d.mapw // 10)

        zuoshang = (cellx * 10, celly * 10)
        youxia = (cellx * 10 + 10, celly * 10 + 10)

        cv2.rectangle(img, zuoshang, youxia,
                      (154, 250, 0), -1)

    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
