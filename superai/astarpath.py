import os
import queue
import sys
import time

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

# a* 8方位
import copy

from superai.astartdemo import idxTohw, hwToidx, dist_between
from superai.gameapi import FlushPid, GameApiInit, GetMenInfo, GetNextDoor, GetNextDoorWrap
from superai.obstacle import GetGameObstacleData, drawBack, GameObstacleData, drawWithOutDoor


# 坐标
class Zuobiao():
    def __init__(self, x, y):
        self.x = x
        self.y = y


# 左右上下极值
class Cell():
    def __init__(self, l, r, t, d):
        self.l = l
        self.r = r
        self.t = t
        self.d = d


OTHER = 2
NODE = 0


# 把节点包装到链表里
class PathEdge():
    def __init__(self, pos, next, type=NODE):
        self.pos = pos
        self.next = next
        self.type = type


# 一个偏移的接口, 因为人物和目的地初始位置不一定在线条上
def NextZuobiao(x, y, way, k):
    # 左右上下
    if way == 0:
        return x - k, y
    if way == 1:
        return x + k, y
    if way == 2:
        return x, y - k
    if way == 3:
        return x, y + k
    return x, y


# 线段是否相交 https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect
def intersect(A, B, C, D):
    def ccw(A, B, C):
        return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)

    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


# 矩形是否相交
def IsRectangleOverlap(l1, r1, l2, r2):
    def IsNotOverlap(l1, r1, l2, r2):
        if r1.x < l2.x or r2.x < l1.x:
            return True
        if r1.y < l2.y or r2.y < l1.y:
            return True
        return False

    return not IsNotOverlap(l1, r1, l2, r2)


# 矩形是否和线段相交
def IsRectagleOverlapLine(renleftx, renrightx, rentopy, rendowny, line):
    rentlines = [
        [Zuobiao(renleftx, rentopy), Zuobiao(renrightx, rentopy)],
        [Zuobiao(renleftx, rendowny), Zuobiao(renrightx, rendowny)],
        [Zuobiao(renleftx, rentopy), Zuobiao(renleftx, rendowny)],
        [Zuobiao(renrightx, rentopy), Zuobiao(renrightx, rendowny)],
    ]

    for rentline in rentlines:
        if intersect(rentline[0], rentline[1], line[0], line[1]):
            return True
    return False


class Obstacle:
    def __init__(self, d: GameObstacleData, menw, menh):
        self.menw = menw
        self.menh = menh

        # 初始化 1. 地形二叉树 2. 地形数组 3. 地形额外  使用 16 * 12 长宽的格子
        self.mapCellWLen = d.mapw // 0x10
        self.mapCellHLen = d.maph // 0xc
        self.cellnum = self.mapCellWLen * self.mapCellHLen
        self.dixing = [False] * self.cellnum

        def dealcell(cell):
            cellX = cell.x // 0x10
            cellY = cell.y // 0xc
            self.dixing[cellY * self.mapCellWLen + cellX] = True

        for cell in d.dixingtree:
            dealcell(cell)
        for cell in d.dixingvec:
            dealcell(cell)
        for cell in d.dixingextra:
            dealcell(cell)

        # 4. 障碍物  使用特定长宽的格子
        self.obstacles = copy.deepcopy(d.obstacles)

    # 刷新障碍(障碍被攻击掉了)
    def UpdateObstacle(self, obstacles):
        self.obstacles = copy.deepcopy(obstacles)

    # 是否地形idx可移动. idx  10 宽高的相应cell一维位置
    def IsDixingVecHave(self, cellidx):
        if cellidx >= len(self.dixing):
            return True
        return self.dixing[cellidx]

    # 范围内相交的所有的障碍物. l,r,t,d 范围格子坐标极值. 返回 [obstacles]
    def RangesAllObstacle(self, l, r, t, d):
        obstacles = []
        for v in self.obstacles:
            halfw = v.w // 2
            halfh = v.h // 2
            obleftx = v.x - halfw
            obrightx = v.x + halfw
            obtopy = v.y - halfh
            obdowny = v.y + halfh
            if IsRectangleOverlap(Zuobiao(l, t), Zuobiao(r, d), Zuobiao(obleftx, obtopy),
                                  Zuobiao(obrightx, obdowny)):
                obstacles.append(v)
        return obstacles

    # 范围内所有的地形格子. l,r,t,d 范围格子坐标极值. 返回 [(cellx, celly)]
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

    # 范围内有障碍物或地形格子, 是否选择路径规划用. l,r,t,d 范围格子坐标极值. 返回True False
    def RangesHaveTrouble(self, l, r, t, d):
        if len(self.RangesAllObstacle(l, r, t, d)) > 0:
            return True
        return self.RangesAllDixing(l, r, t, d)

    # 是否触碰到地形. x,y 10 宽高的相应cell位置
    def DixingTouched(self, cellx, celly):
        l = (cellx * 10 - self.menw // 2) // 0x10
        r = (cellx * 10 + self.menw // 2) // 0x10
        t = (celly * 10 - self.menh // 2) // 0xc
        d = (celly * 10 + self.menh // 2) // 0xc
        for i in range(r - l + 1):
            for j in range(d - t + 1):
                if self.IsDixingVecHave(hwToidx(l + i, t + j, self.mapCellWLen)):
                    return True
        return False

    # 是否触碰到障碍物. x,y 10 宽高的相应cell位置
    def ObstacleTouched(self, cellx, celly):
        leftx = (cellx * 10 - self.menw // 2)
        rightx = (cellx * 10 + self.menw // 2)
        topy = (celly * 10 - self.menh // 2)
        downy = (celly * 10 + self.menh // 2)
        for v in self.obstacles:
            halfw = int(v.w / 2)
            halfh = int(v.h / 2)
            obleftx = v.x - halfw
            obrightx = v.x + halfw
            obtopy = v.y - halfh
            obdowny = v.y + halfh
            if IsRectangleOverlap(Zuobiao(leftx, topy), Zuobiao(rightx, downy), Zuobiao(obleftx, obtopy),
                                  Zuobiao(obrightx, obdowny)):
                return True
        return False

    # 是否越界 TODO 写死了
    def OverStep(self, cellx, celly):
        return cellx * 10 > self.mapCellWLen * 0x10 or celly * 10 > self.mapCellHLen * 0xc

    # 是否触碰到地形或者障碍物或者越界. p[cellx,celly] 10 宽高相应cell位置
    def TouchedAnything(self, p):
        if self.DixingTouched(p[0], p[1]):
            return True
        if self.ObstacleTouched(p[0], p[1]):
            return True
        if self.OverStep(p[0], p[1]):
            return True
        return False

    # 两点之间人物是否可以直接移动过去 检查 1. 地形 2. 障碍物
    def CanTwoPointBeMove(self, point1: Zuobiao, point2: Zuobiao):
        halfw = self.menw // 2
        halfh = self.menh // 2
        # 人物矩形左右上下
        point1leftx, point1rightx, point1topy, point1downy = point1.x - halfw, point1.x + halfw, point1.y - halfh, point1.y + halfh
        point2leftx, point2rightx, point2topy, point2downy = point2.x - halfw, point2.x + halfw, point2.y - halfh, point2.y + halfh
        # 范围极值
        minl, minr, mint, mind = min(point1leftx, point2leftx), \
                                 max(point1rightx, point2rightx), min(point1topy, point2topy), \
                                 max(point1downy, point2downy)

        dixingcells = self.RangesAllDixing(minl, minr, mint, mind)
        obstacles = self.RangesAllObstacle(minl, minr, mint, mind)

        if len(dixingcells) < 1 and len(obstacles) < 1:
            return True

        # 两个位置之间的4角的连线
        towpointlines = [
            [Zuobiao(point1leftx, point1topy), Zuobiao(point2leftx, point2topy)],
            [Zuobiao(point1rightx, point1topy), Zuobiao(point2rightx, point2topy)],
            [Zuobiao(point1leftx, point1downy), Zuobiao(point2leftx, point2downy)],
            [Zuobiao(point1rightx, point1downy), Zuobiao(point2rightx, point2downy)],
        ]

        # 地形判断
        for twopointline in towpointlines:
            for dixingcell in dixingcells:
                l, r, t, d = dixingcell[0] * 0x10, dixingcell[0] * 0x10 + 0x10, dixingcell[1] * 0xc, dixingcell[
                    1] * 0xc + 0xc
                if IsRectagleOverlapLine(l, r, t, d, twopointline):
                    return False
        # 障碍物判断
        for twopointline in towpointlines:
            for v in obstacles:
                halfw = v.w // 2
                halfh = v.h // 2
                l, r, t, d = v.x - halfw, v.x + halfw, v.y - halfh, v.y + halfh
                if IsRectagleOverlapLine(l, r, t, d, twopointline):
                    return False

        return True

    # 修正初始坐标, 初始坐标可能和障碍物相交, 所以需要稍微调整. return (cellx, celly)
    def CorrectZuobiao(self, cellpos):
        if self.TouchedAnything([cellpos[0], cellpos[1]]):
            curx, cury = cellpos[0], cellpos[1]
            for k in range(10):
                for i in range(4):
                    correctx, correcty = NextZuobiao(curx, cury, i, k)
                    if not self.TouchedAnything([correctx, correcty]):
                        return correctx, correcty
        return cellpos[0], cellpos[1]


class AStartPaths:
    # 构造函数 地形, 人物信息, 起始点, 终结点,
    def __init__(self, MAPW, MAPH, ob, start, end):
        self.MAPW = MAPW
        self.MAPH = MAPH
        self.ob = ob

        # start end && 行走的路径使用 10 * 10 长宽的格子
        self.manCellWLen = MAPW // 10
        self.manCellHLen = MAPH // 10
        self.manCellnum = self.manCellHLen * self.manCellWLen

        # a * 核心算法
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

    # 获取邻居节点
    def GetAdjs(self, pos):
        # 获取八方位邻居格子. 根据地形和障碍数据过滤掉不必要的
        adjs = []
        cellx, celly = idxTohw(pos, self.manCellWLen)

        # 上下左右. 左上,左下,右上,右下.
        checks = [
            (cellx, celly - 1), (cellx, celly + 1), (cellx - 1, celly), (cellx + 1, celly),
            (cellx - 1, celly - 1), (cellx - 1, celly + 1), (cellx + 1, celly - 1), (cellx + 1, celly + 1),
        ]

        for (adjx, adjy) in checks:
            if self.ob.TouchedAnything([adjx, adjy]):
                continue
            # cv2.rectangle(img, (adjx * 10, adjy * 10), (adjx * 10 + 10, adjy * 10 + 10), (0, 0, 139), 1)
            adjs.append(hwToidx(adjx, adjy, self.manCellWLen))
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

                global img
                if img is not None:
                    # 画邻居
                    ccellx, ccelly = idxTohw(w, self.manCellWLen)
                    cv2.circle(img, (ccellx * 10, ccelly * 10), 2, (255, 0, 0))

                self.edgeTo[w] = current
                self.marked[w] = True
                self.gScore[w] = tentativeScore
                self.fScore[w] = self.gScore[w] + dist_between(idxTohw(w, self.manCellWLen),
                                                               idxTohw(self.end, self.manCellWLen))

    # 是否有到该节点的路径
    def HasPathTo(self, v: int):
        return self.marked[v]

    # 到该节点的路径的所有的节点
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

    # 平滑 返回链表, [idx]
    def PathToSmooth(self, v: int):
        paths = self.PathTo(v)
        paths = list(reversed(paths))
        # 把数组变成链表
        firstnode = PathEdge(0, None, OTHER)
        curnode = firstnode
        for v in paths:
            curnode.next = PathEdge(v, None, NODE)
            curnode = curnode.next

        # 平滑路径
        e1 = firstnode.next
        e2 = e1.next
        while e2:
            (curcellx, curcelly) = idxTohw(e1.pos, self.manCellWLen)
            (nextcellx, nextcelly) = idxTohw(e2.pos, self.manCellWLen)
            firstzuobiao = Zuobiao(curcellx * 10, curcelly * 10)
            nextzuobiao = Zuobiao(nextcellx * 10, nextcelly * 10)

            if self.ob.CanTwoPointBeMove(firstzuobiao, nextzuobiao):
                e1.next = e2
                e2 = e2.next
            else:
                e1 = e2
                e2 = e2.next

        return firstnode.next

    # 平滑列表 返回列表 [idx]
    def PathToSmoothLst(self, v: int):
        result = []
        iter = self.PathToSmooth(v)
        while iter:
            result.append(iter.pos)
            iter = iter.next
        return result


# 取门范围内的可移动位置 (就写在这里吧. 防止py循环引用)
class BfsNextDoorWrapCorrect:
    def __init__(self, MAPW, MAPH, door, ob: Obstacle):
        self.MAPW = MAPW
        self.MAPH = MAPH
        self.door = door
        self.ob = ob

        self.manCellWLen = MAPW // 10
        self.manCellHLen = MAPH // 10
        self.manCellnum = self.manCellHLen * self.manCellWLen

        self.l, self.r, self.t, self.d = self.door.x, self.door.x + self.door.w, self.door.y, self.door.y + self.door.h
        self.halfw, self.halfh = self.door.w // 2, self.door.h // 2

        # bfs core
        self.marked = [False] * self.manCellnum
        self.edgeTo = [0] * self.manCellnum

        startcellx = (self.l + self.halfw) // 10
        startcelly = (self.t + self.halfh) // 10

        self.s = hwToidx(startcellx, startcelly, self.manCellWLen)

    def OutRange(self, cellx, celly):
        l = cellx * 10
        r = cellx * 10 + 10
        t = celly * 10
        d = celly * 10 + 10
        return not IsRectangleOverlap(Zuobiao(self.l, self.t), Zuobiao(self.r, self.d), Zuobiao(l, t),
                                      Zuobiao(r, d))

    # 获取邻居节点. return [cellx, celly]
    def GetAdjs(self, pos):
        # 不超过门的范围
        adjs = []
        cellx, celly = idxTohw(pos, self.manCellWLen)

        # 上下左右. 左上,左下,右上,右下.
        checks = [
            (cellx, celly - 1), (cellx, celly + 1), (cellx - 1, celly), (cellx + 1, celly),
            (cellx - 1, celly - 1), (cellx - 1, celly + 1), (cellx + 1, celly - 1), (cellx + 1, celly + 1),
        ]

        for (adjx, adjy) in checks:
            if not self.OutRange(adjx, adjy):
                adjs.append(hwToidx(adjx, adjy, self.manCellWLen))

        return adjs

    # bfs 获取没有碰撞到障碍物的点, return [cellx, celly]
    def bfs(self):
        q = queue.Queue()
        q.put(self.s)

        while q.qsize() != 0:
            v = q.get()

            adjs = self.GetAdjs(v)
            for w in adjs:

                adjcellx, adjcelly = idxTohw(w, self.manCellWLen)

                if not self.ob.TouchedAnything([adjcellx, adjcelly]):
                    return idxTohw(w, self.manCellWLen)

                if not self.marked[w]:
                    self.edgeTo[w] = v
                    self.marked[w] = True
                    q.put(w)
        return idxTohw(self.s, self.manCellWLen)


img = None


# 将x,y转换成 10 格子的坐标.并修正
def CoordToManIdx(x, y, mancellwlen, ob):
    x, y = int(x), int(y)
    (ccellx, ccelly) = ob.CorrectZuobiao([x // 10, y // 10])
    return hwToidx(ccellx, ccelly, mancellwlen)


def DrawAnyPath(beginx, beginy, endx, endy):
    global img

    meninfo = GetMenInfo()
    d = GetGameObstacleData()
    ob = Obstacle(d, meninfo.w, meninfo.h)

    mancellwlen = d.mapw // 10

    img = np.zeros((d.maph, d.mapw, 3), dtype=np.uint8)
    img[np.where(img == [0])] = [255]
    drawWithOutDoor(img, d)

    begincellidx = CoordToManIdx(beginx, beginy, mancellwlen, ob)
    endcellidx = CoordToManIdx(endy, endy, mancellwlen, ob)

    # a star search
    astar = AStartPaths(d.mapw, d.maph, ob, begincellidx, endcellidx)
    lst = astar.PathToSmoothLst(endcellidx)

    for ele in lst:
        # 画路径点
        (cellx, celly) = idxTohw(ele, mancellwlen)
        drawx, drawy = cellx * 10, celly * 10
        cv2.circle(img, (drawx, drawy), 2, (0, 0, 255))

        # 方格子
        halfw, halfh = meninfo.w // 2, meninfo.h // 2
        cv2.rectangle(img, (drawx - halfw, drawy - halfh), (drawx + halfw, drawy + halfh), (0, 0, 139), 1)

    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


# 画寻找到门的路径
def DrawNextDoorPath():
    global img

    meninfo = GetMenInfo()
    d = GetGameObstacleData()
    ob = Obstacle(d, meninfo.w, meninfo.h)

    mancellwlen = d.mapw // 10

    # 画图
    img = np.zeros((d.maph, d.mapw, 3), dtype=np.uint8)
    img[np.where(img == [0])] = [255]
    drawWithOutDoor(img, d)

    begincellidx = CoordToManIdx(meninfo.x, meninfo.y, mancellwlen, ob)

    door = GetNextDoorWrap()
    bfsdoor = BfsNextDoorWrapCorrect(d.mapw, d.maph, door, ob)
    (cellx, celly) = bfsdoor.bfs()
    endcellidx = CoordToManIdx(cellx * 10, celly * 10, mancellwlen, ob)

    # a star search
    astar = AStartPaths(d.mapw, d.maph, ob, begincellidx, endcellidx)
    lst = astar.PathToSmoothLst(endcellidx)

    for ele in lst:
        # 画路径点
        (cellx, celly) = idxTohw(ele, mancellwlen)
        drawx, drawy = cellx * 10, celly * 10
        cv2.circle(img, (drawx, drawy), 2, (0, 0, 255))

        # 方格子
        halfw, halfh = meninfo.w // 2, meninfo.h // 2
        cv2.rectangle(img, (drawx - halfw, drawy - halfh), (drawx + halfw, drawy + halfh), (0, 0, 139), 1)

    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()


def main():
    if GameApiInit():
        print("Init helpdll-xxiii.dll ok")
    else:
        print("Init helpdll-xxiii.dll err")
        exit(0)
    FlushPid()

    # DrawNextDoorPath()
    DrawAnyPath(1167, 229, 127, 24)


if __name__ == '__main__':
    main()
