import os
import sys
import time

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

# a* 8方位
import copy

from superai.astartdemo import idxTohw, hwToidx, dist_between
from superai.common import Log
from superai.gameapi import FlushPid, GameApiInit, GetMenInfo
from superai.obstacle import GetGameObstacleData, drawAll, drawBack


class Zuobiao():
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Cell():
    def __init__(self, l, r, t, d):
        self.l = l
        self.r = r
        self.t = t
        self.d = d


OTHER = 2
NODE = 0


class PathEdge():
    def __init__(self, pos, next, type=NODE):
        self.pos = pos
        self.next = next
        self.type = type


class AStartPaths:

    # 初始化 地形 + 障碍物
    def initobstacle(self, d):
        # 初始化
        # 1. 地形二叉树 2. 地形数组 3. 地形额外  使用 16 * 12 长宽的格子
        # 4. 障碍物  使用特定长宽的格子
        self.mapCellWLen = d.mapw // 0x10
        self.mapCellHLen = d.maph // 0xc
        self.cellnum = self.mapCellWLen * self.mapCellHLen
        self.dixing = [False] * self.cellnum

        # Log("self.mapCellWLen: %d self.mapCellHLen: %d \n" % (self.mapCellWLen, self.mapCellHLen))

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

    # 构造函数 地形, 人物信息, 起始点, 终结点, img做测试使用
    def __init__(self, d, meninfo, start, end, img):
        self.img = img
        self.meninfo = meninfo
        self.mapwlen = d.mapw
        self.maphlen = d.maph

        self.initobstacle(d)

        # 初始化 A * 算法数据
        # start end && 行走的路径使用 10 * 10 长宽的格子
        self.manCellWLen = d.mapw // 10
        self.manCellHLen = d.maph // 10
        self.manCellnum = self.manCellHLen * self.manCellWLen

        # Log("manCellWLen: %d manCellHLen: %d manCellnum: %d" % (self.manCellWLen, self.manCellHLen, self.manCellnum))

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
        self.fScore[start] = dist_between(idxTohw(start, self.manCellWLen), idxTohw(end, self.manCellWLen))

        self.astar()

    # 矩形相交
    def IsRectangleOverlap(self, l1, r1, l2, r2):
        def IsNotOverlap(l1, r1, l2, r2):
            if r1.x < l2.x or r2.x < l1.x:
                return True
            if r1.y < l2.y or r2.y < l1.y:
                return True
            return False

        return not IsNotOverlap(l1, r1, l2, r2)

    # 构造线段
    def line(self, p1, p2):
        A = (p1[1] - p2[1])
        B = (p2[0] - p1[0])
        C = (p1[0] * p2[1] - p2[0] * p1[1])
        return A, B, -C

    # 交点
    def intersection(self, L1, L2):
        D = L1[0] * L2[1] - L1[1] * L2[0]
        Dx = L1[2] * L2[1] - L1[1] * L2[2]
        Dy = L1[0] * L2[2] - L1[2] * L2[0]
        if D != 0:
            x = Dx / D
            y = Dy / D
            return x, y
        else:
            return False

    # 线段与线段是否相交 https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
    # https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
    def IsLineOverlapLine(self, L1, L2):
        R = self.intersection(L1, L2)
        return True if R else False

    # 矩形是否和线段相交
    def IsRectagleOverlapLine(self, renleftx, renrightx, rentopy, rendowny, line):
        checks = [
            self.line([renleftx, rentopy], [renrightx, rentopy]),
            self.line([renleftx, rendowny], [renrightx, rendowny]),
            self.line([renleftx, rentopy], [renleftx, rendowny]),
            self.line([renrightx, rentopy], [renrightx, rendowny])
        ]
        for check in checks:
            if self.IsLineOverlapLine(check, line):
                return True
        return False

    # 范围内所有的地形格子
    def RangesAllDixing(self, l, r, t, d):
        dixingcells = []
        l = l // 0x10
        r = r // 0x10
        t = t // 0xc
        d = d // 0xc

        # 横轴0x10步进, 竖轴0xc步进
        for i in range(r - l + 1):
            for j in range(d - t + 1):
                if self.IsDixingVecHave(hwToidx(l + i, t + j, self.mapCellWLen)):
                    dixingcells.append((l + i, t + j))
        return dixingcells

    # 范围内相交的所有的障碍物
    def RangesAllObstacle(self, l, r, t, d):
        obstacles = []
        for v in self.obstacles:
            halfw = int(v.w / 2)
            halfh = int(v.h / 2)
            obleftx = v.x - halfw
            obrightx = v.x + halfw
            obtopy = v.y - halfh
            obdowny = v.y + halfh

            if self.IsRectangleOverlap(Zuobiao(l, t), Zuobiao(r, d), Zuobiao(obleftx, obtopy),
                                       Zuobiao(obrightx, obdowny)):
                obstacles.append(v)
        return obstacles

    # 两点之间人物是否可以直接移动过去 检查 1. 地形 2. 障碍物
    def CanTwoPointBeMove(self, point1: Zuobiao, point2: Zuobiao):
        halfw = self.meninfo.w // 2
        halfh = self.meninfo.h // 2
        # 人物矩形左右上下
        point1leftx, point1rightx, point1topy, point1downy = point1.x - halfw, point1.x + halfw, point1.y - halfh, point1.y + halfh
        point2leftx, point2rightx, point2topy, point2downy = point2.x - halfw, point2.x + halfw, point2.y - halfh, point2.y + halfh
        # 范围极值
        minl, minr, mint, mind = min(point1leftx, point2leftx), \
                                 min(point1rightx, point2rightx), min(point1topy, point2topy), \
                                 min(point1downy, point2downy)

        dixingcells = self.RangesAllDixing(minl, minr, mint, mind)
        obstacles = self.RangesAllObstacle(minl, minr, mint, mind)

        if len(dixingcells) < 1 and len(obstacles) < 1:
            return True

        checks = [
            self.line([point1leftx, point1topy], [point2leftx, point2topy]),
            self.line([point1rightx, point1topy], [point2rightx, point2topy]),
            self.line([point1leftx, point1downy], [point2leftx, point2downy]),
            self.line([point1rightx, point1downy], [point2rightx, point2downy])
        ]

        for checkline in checks:
            for dixingcell in dixingcells:
                l, r, t, d = dixingcell[0], dixingcell[0] + 0x10, dixingcell[1], dixingcell[1] + 0xc
                if self.IsRectagleOverlapLine(l, r, t, d, checkline):
                    return False

        for checkline in checks:
            for obstacle in obstacles:
                halfw = obstacle.w // 2
                halfh = obstacle.h // 2
                l, r, t, d = obstacle.x - halfw, obstacle.x + halfw, obstacle.h - halfh, obstacle.h + halfh
                if self.IsRectagleOverlapLine(l, r, t, d, checkline):
                    return False

        return True

    # 是否地形idx可移动
    def IsDixingVecHave(self, idx):
        if idx >= len(self.dixing):
            return True
        return self.dixing[idx]

    # 是否触碰到地形
    def DixingTouched(self, x, y):
        leftx = (x * 10 - self.meninfo.w // 2) // 0x10
        rightx = (x * 10 + self.meninfo.w // 2) // 0x10
        topy = (y * 10 - self.meninfo.h // 2) // 0xc
        downy = (y * 10 + self.meninfo.h // 2) // 0xc

        # 横轴0x10步进
        for i in range(rightx - leftx + 1):
            if self.IsDixingVecHave(hwToidx(leftx + i, topy, self.mapCellWLen)):
                return True
            if self.IsDixingVecHave(hwToidx(leftx + i, downy, self.mapCellWLen)):
                return True

        # 纵轴0xc步进
        for i in range(downy - topy + 1):
            if self.IsDixingVecHave(hwToidx(leftx, topy + i, self.mapCellWLen)):
                return True
            if self.IsDixingVecHave(hwToidx(rightx, topy + i, self.mapCellWLen)):
                return True

        return False

    # 是否触碰到障碍物
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

            # cv2.rectangle(self.img, (leftx, topy), (rightx, downy), (0, 0, 139), 1)
            # cv2.rectangle(self.img, (obleftx, obtopy), (obrightx, obdowny), (255, 0, 0), 1)

            if self.IsRectangleOverlap(Zuobiao(leftx, topy), Zuobiao(rightx, downy), Zuobiao(obleftx, obtopy),
                                       Zuobiao(obrightx, obdowny)):
                return True

        return False

    # 获取邻居节点
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
            if adjx * 10 > self.mapwlen or adjy * 10 > self.maphlen:
                continue

            if self.DixingTouched(adjx, adjy):
                continue

            if self.ObstacleTouched(adjx, adjy):
                continue

            adjs.append(hwToidx(adjx, adjy, self.manCellWLen))

            # 临时打印下 邻居节点
            # drawx, drawy = adjx * 10, adjy * 10
            # cv2.circle(self.img, (drawx, drawy), 2, (255, 0, 0))

        return adjs

    # a* core
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
                tentativeScore = self.gScore[current] + dist_between(idxTohw(current, self.manCellWLen),
                                                                     idxTohw(w, self.manCellWLen))
                if w not in self.openSet:
                    self.openSet.append(w)
                elif tentativeScore >= self.gScore[w]:
                    continue

                # print("add w : %d  (%s)" % (current, idxTohw(w, self.manCellWLen)))
                self.edgeTo[w] = current
                self.marked[w] = True
                self.gScore[w] = tentativeScore
                self.fScore[w] = self.gScore[w] + dist_between(idxTohw(w, self.manCellWLen),
                                                               idxTohw(self.end, self.manCellWLen))

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
    dstx, dsty = 443, 364
    endx, endy = (int(dstx) // 10) * 10, (int(dsty) // 10) * 10
    cv2.rectangle(img, (endx - meninfo.w // 2, endy - meninfo.h // 2),
                  (endx + meninfo.w // 2, endy + meninfo.h // 2), (0, 0, 255), 1)

    astar = AStartPaths(d, meninfo, hwToidx(beginx // 10, beginy // 10, d.mapw // 10),
                        hwToidx(endx // 10, endy // 10, d.mapw // 10), img)
    paths = astar.PathTo(hwToidx(endx // 10, endy // 10, d.mapw // 10))
    paths = list(reversed(paths))

    # for v in paths:
    #     (x, y) = idxTohw(v, d.mapw // 10)
    #     drawx, drawy = x * 10, y * 10
    #     cv2.circle(img, (drawx, drawy), 2, (0, 0, 255))

    firstnode = PathEdge(0, None, OTHER)
    curnode = firstnode
    for v in paths:
        curnode.next = PathEdge(v, None, NODE)
        curnode = curnode.next

    # 平滑
    e1 = firstnode.next
    e2 = e1.next
    while e2:
        (curx, cury) = idxTohw(e1.pos, d.mapw // 10)
        (nextx, nexty) = idxTohw(e2.pos, d.mapw // 10)

        firstzuobiao = Zuobiao(curx * 10, cury * 10)
        nextzuobiao = Zuobiao(nextx * 10, nexty * 10)


        cv2.circle(img, (nextzuobiao.x, nextzuobiao.y), 3, (0, 155, 0))

        if astar.CanTwoPointBeMove(firstzuobiao, nextzuobiao):
            e1.next = e2
            e2 = e2.next
        else:
            e1 = e2
            e2 = e2.next

    iternode = firstnode.next
    while iternode:
        (x, y) = idxTohw(iternode.pos, d.mapw // 10)
        drawx, drawy = x * 10, y * 10
        cv2.circle(img, (drawx, drawy), 2, (0, 0, 255))
        iternode = iternode.next



    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
