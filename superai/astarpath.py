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
from superai.obstacle import GetGameObstacleData, drawAll, drawBack


class Zuobiao():
    def __init__(self, x, y):
        self.x = x
        self.y = y


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

    def __init__(self, d, meninfo, start, end, img):
        self.img = img
        self.meninfo = meninfo

        self.initobstacle(d)

        # 初始化 A * 算法数据
        # start end && 行走的路径使用 10 * 10 长宽的格子
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
        self.gScore = [sys.maxsize] * self.manCellnum
        self.gScore[start] = 0

        # 估算到终点的距离
        self.fScore = [sys.maxsize] * self.manCellnum
        self.fScore[start] = manhattanDistance(idxTohw(start, self.manCellWLen), idxTohw(end, self.manCellWLen))

        self.astar()

    def DixingTouched(self, x, y):
        leftx = (x * 10 - self.meninfo.w // 2) // 0x10
        rightx = (x * 10 + self.meninfo.w // 2) // 0x10
        topy = (y * 10 - self.meninfo.h // 2) // 0xc
        downy = (y * 10 + self.meninfo.h // 2) // 0xc

        # 横轴0x10步进
        for i in range(rightx - leftx + 1):
            if self.dixing[hwToidx(leftx + i, topy, self.mapCellWLen)]:
                return True
            if self.dixing[hwToidx(leftx + i, downy, self.mapCellWLen)]:
                return True

        # 纵轴0xc步进
        for i in range(downy - topy + 1):
            if self.dixing[hwToidx(leftx, topy + i, self.mapCellWLen)]:
                return True
            if self.dixing[hwToidx(rightx, topy + i, self.mapCellWLen)]:
                return True

        return False

    def IsNotOverlap(self, l1, r1, l2, r2):
        return r1.x < l2.x or r2.x < l1.x or l2.y < r1.y or r2.y < l1.y

    def ObstacleTouched(self, x, y):
        leftx = (x * 10 - self.meninfo.w // 2)
        rightx = (x * 10 + self.meninfo.w // 2)
        topy = (y * 10 - self.meninfo.h // 2)
        downy = (y * 10 + self.meninfo.h // 2)
        for v in self.obstacles:
            halfw = int(v.w / 2)
            halfh = int(v.h / 2)
            obleftx = v.x - halfw
            obrightx = v.x + halfw
            obtopy = v.y - halfh
            obdowny = v.y + halfh

            if not self.IsNotOverlap(Zuobiao(leftx, topy), Zuobiao(rightx, downy), Zuobiao(obleftx, obtopy),
                                     Zuobiao(obrightx, obdowny)):
                cv2.rectangle(self.img, (obleftx, obtopy), (obrightx, obdowny), (255, 0, 0), 1)
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
            # if self.DixingTouched(adjx, adjy):
            #     continue
            #
            if self.ObstacleTouched(adjx, adjy):
                continue

            adjs.append(hwToidx(adjx, adjy, self.manCellWLen))
            #
            # drawx, drawy = adjx * 10, adjy * 10
            # cv2.circle(self.img, (drawx, drawy), 2, (255, 0, 0))

        return adjs

    def findMinScore(self):
        min = sys.maxsize
        minv = sys.maxsize

        for v in self.openSet:
            if self.fScore[v] < min:
                min = self.fScore[v]
                minv = v

        return minv

    def astar(self):
        while len(self.openSet) > 0:
            current = self.findMinScore()

            drawx, drawy = idxTohw(current, self.manCellWLen)
            drawx, drawy = drawx * 10, drawy * 10
            cv2.circle(self.img, (drawx, drawy), 2, (255, 0, 0))

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

                if tentativeScore < self.gScore[w]:

                    # drawx, drawy = idxTohw(current, self.manCellWLen)
                    # drawx, drawy = drawx * 10, drawy * 10
                    # cv2.circle(self.img, (drawx, drawy), 2, (255, 0, 0))

                    self.edgeTo[w] = current
                    self.marked[w] = True

                    # print("edgeTo ({}) -> ({})".format(idxTohw(current, self.manCellWLen), idxTohw(w, self.manCellWLen)))

                    self.gScore[w] = tentativeScore
                    self.fScore[w] = self.gScore[w] + manhattanDistance(idxTohw(w, self.manCellWLen),
                                                                        idxTohw(self.end, self.manCellWLen))

                    # print("fScore[%d] manhattan: %d" % (w, self.fScore[w]))

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

    d = GetGameObstacleData()

    print("w h : %d %d" % (d.mapw, d.maph))

    img = np.zeros((d.maph, d.mapw, 3), dtype=np.uint8)
    img[np.where(img == [0])] = [255]

    drawBack(img, d)

    # 人物矩形
    meninfo = GetMenInfo()
    beginx, beginy = (int(meninfo.x) // 10) * 10, (int(meninfo.y) // 10) * 10
    cv2.rectangle(img, (beginx - meninfo.w // 2, beginy - meninfo.h // 2),
                  (beginx + meninfo.w // 2, beginy + meninfo.h // 2), (0, 0, 255), 1)

    # 目的地矩形
    dstx, dsty = 734, 286
    endx, endy = (int(dstx) // 10) * 10, (int(dsty) // 10) * 10
    cv2.rectangle(img, (endx - meninfo.w // 2, endy - meninfo.h // 2),
                  (endx + meninfo.w // 2, endy + meninfo.h // 2), (0, 0, 255), 1)

    astar = AStartPaths(d, meninfo, hwToidx(beginx // 10, beginy // 10, d.mapw // 10),
                        hwToidx(endx // 10, endy // 10, d.mapw // 10), img)

    paths = astar.PathTo(hwToidx(endx // 10, endy // 10, d.mapw // 10))

    for v in reversed(paths):
        (x, y) = idxTohw(v, d.mapw // 10)
        drawx, drawy = x * 10, y * 10
        cv2.circle(img, (drawx, drawy), 2, (0, 0, 255))

    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
