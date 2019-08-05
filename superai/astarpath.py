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
        self.manCellHWLen = d.mapw // 10
        self.manCellWLen = d.maph // 10
        self.manCellnum = self.manCellHWLen * self.manCellWLen

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

    def ObstacleTouched(self, x, y):
        for v in self.obstacles:
            # 坐标在障碍物的范围之内
            halfw = int(v.w / 2)
            halfh = int(v.h / 2)
            if (v.x - halfw < x < v.x + halfw) and \
                    (v.y - halfh < y < v.y + halfh):
                return True

        return False

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
            # 1. 地形. 矩形的中点不在格子内
            # 把10 x 10 格子的中点 转换成 0xc 0x10 的格子. 判断是否可移动
            adjx2 = (adjx * 10 + 5) // 0x10
            adjy2 = (adjy * 10 + 5) // 0xc

            dixingidx = hwToidx(adjx2, adjy2, self.mapCellWLen)

            if dixingidx >= len(self.dixing):
                continue

            if not self.dixing[dixingidx]:
                # 2. 障碍物. 矩形的中点和不在障碍物内
                # 把10 x 10 格子的中点 转换成坐标中点.
                adjx3 = adjx * 10 + 5
                adjy3 = adjy * 10 + 5
                if not self.ObstacleTouched(adjx3, adjy3):
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

                (cellx, celly) = idxTohw(current, self.manCellWLen)
                cv2.rectangle(self.img, (cellx * 10, celly * 10), (cellx * 10 + 10, celly * 10 + 10),
                              (127, 255, 0), -1)

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


def main():
    if GameApiInit():
        print("Init helpdll-xxiii.dll ok")
    else:
        print("Init helpdll-xxiii.dll err")
        exit(0)
    FlushPid()

    # (647,312,0) 血滴石

    d = GetGameObstacleData()

    img = np.zeros((d.maph, d.mapw, 3), dtype=np.uint8)
    img[np.where(img == [0])] = [255]

    drawAll(img, d)

    wlen = d.mapw // 10
    meninfo = GetMenInfo()

    begincellx, begincelly = int(meninfo.x) // 10, int(meninfo.y) // 10
    endcellx, endcelly = 647 // 10, 312 // 10
    startidx = hwToidx(begincellx, begincelly, wlen)
    endidx = hwToidx(endcellx, endcelly, wlen)

    print("a* 寻径")
    astar = AStartPaths(d, startidx, endidx, img)
    paths = astar.PathTo(hwToidx(endcellx, endcelly, wlen))
    for v in reversed(paths):
        print(v, idxTohw(v, d.mapw // 10))

    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
