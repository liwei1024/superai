import queue

import sys

import logging

from superai.common import InitLog

logger = logging.getLogger(__name__)


# 2维到1维
def hwToidx(x: int, y: int, weight: int):
    return y * weight + x


# 1维到2维
def idxTohw(idx, weight: int):
    return [idx % weight, idx // weight]


# 10x10 cell idx 到 [x,y]
def idxToXY(idx, cellw: int):
    curpoint = idxTohw(idx, cellw)
    curpoint[0], curpoint[1] = curpoint[0] * 10, curpoint[1] * 10
    return curpoint


# 有向图
class Graph:
    def __init__(self, V: int, W: int):
        # 顶点数量
        self.V = V

        # 边数量
        self.E = 0

        # 邻接表
        self.adj = []

        # 宽度  (虽然是一维的但是表示是二维的)
        self.W = W

        for i in range(V):
            nears = []
            self.adj.append(nears)

    def AddEdge(self, v: int, w: int):
        self.adj[v].append(w)
        self.E += 1

    def __str__(self):
        str = ""
        for idx, nears in enumerate(self.adj):
            str += "idx: {} nears: {}\n".format(idx, nears)
        return str


# bfs
class BreadthFirstPaths:
    def __init__(self, g: Graph, s: int):
        self.marked = [False] * g.V
        self.edgeTo = [0] * g.V
        self.s = s

        self.bfs(g, self.s)

    def bfs(self, g: Graph, s: int):
        q = queue.Queue()
        q.put(s)
        while q.qsize() != 0:
            v = q.get()

            for w in g.adj[v]:
                # 这个路径没有经过
                if not self.marked[w]:
                    self.edgeTo[w] = v
                    self.marked[w] = True
                    q.put(w)

                    # print(w, idxTohw(w, 6))

    def HasPathTo(self, v: int):
        return self.marked[v]

    def PathTo(self, v: int) -> [int]:
        result = []
        if not self.HasPathTo(v):
            return result
        x = v
        while x != self.s:
            result.append(x)
            x = self.edgeTo[x]
        result.append(self.s)
        return result


# 曼哈顿距离
def manhattanDistance(x, y):
    return sum(map(lambda i, j: abs(i - j), x, y))


# 欧几里得距离
def dist_between(a, b):
    return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2


# a*  4方位
class AStarPaths:
    def __init__(self, g: Graph, start: int, end: int):
        self.closedSet = []
        self.openSet = [start]

        self.start = start
        self.end = end

        self.edgeTo = [0] * g.V
        self.marked = [False] * g.V

        # 实际距离
        self.gScore = [sys.maxsize] * g.V
        self.gScore[start] = 0

        # 估算到终点的距离
        self.fScore = [sys.maxsize] * g.V
        self.fScore[start] = manhattanDistance(idxTohw(start, g.W), idxTohw(end, g.W))

        self.astar(g)

    def astar(self, g: Graph):
        while len(self.openSet) > 0:
            current = min(self.openSet, key=lambda s: self.fScore[s])

            if current == self.end:
                return
            self.openSet.remove(current)
            self.closedSet.append(current)
            for w in g.adj[current]:
                if w in self.closedSet:
                    continue
                # 实际距离
                tentativegScore = self.gScore[current] + manhattanDistance(idxTohw(current, g.W),
                                                                           idxTohw(w, g.W))
                if tentativegScore < self.gScore[w]:
                    self.edgeTo[w] = current
                    self.marked[w] = True

                    print("edgeTo ({}) -> ({})".format(idxTohw(current, g.W), idxTohw(w, g.W)))
                    self.gScore[w] = tentativegScore
                    self.fScore[w] = self.gScore[w] + manhattanDistance(idxTohw(w, g.W), idxTohw(self.end, g.W))

                    print("fScore[%d] manhattan: %d" % (w, self.fScore[w]))

                    if w not in self.openSet:
                        self.openSet.append(w)

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
    InitLog()

    # 0,1,2,3,4 ... 一共12个顶点. width=6,height=4
    graph = Graph(24, 6)

    graph.AddEdge(hwToidx(2, 0, 6), hwToidx(2, 1, 6))

    graph.AddEdge(hwToidx(1, 1, 6), hwToidx(1, 2, 6))

    graph.AddEdge(hwToidx(2, 1, 6), hwToidx(2, 0, 6))
    graph.AddEdge(hwToidx(2, 1, 6), hwToidx(3, 1, 6))

    graph.AddEdge(hwToidx(3, 1, 6), hwToidx(2, 1, 6))
    graph.AddEdge(hwToidx(3, 1, 6), hwToidx(4, 1, 6))

    graph.AddEdge(hwToidx(4, 1, 6), hwToidx(4, 2, 6))
    graph.AddEdge(hwToidx(4, 1, 6), hwToidx(3, 1, 6))

    graph.AddEdge(hwToidx(0, 2, 6), hwToidx(1, 2, 6))

    graph.AddEdge(hwToidx(1, 2, 6), hwToidx(1, 3, 6))
    graph.AddEdge(hwToidx(1, 2, 6), hwToidx(0, 2, 6))
    graph.AddEdge(hwToidx(1, 2, 6), hwToidx(1, 1, 6))
    graph.AddEdge(hwToidx(1, 2, 6), hwToidx(2, 2, 6))

    graph.AddEdge(hwToidx(2, 2, 6), hwToidx(2, 3, 6))
    graph.AddEdge(hwToidx(2, 2, 6), hwToidx(1, 2, 6))
    graph.AddEdge(hwToidx(2, 2, 6), hwToidx(3, 2, 6))
    graph.AddEdge(hwToidx(3, 2, 6), hwToidx(3, 3, 6))
    graph.AddEdge(hwToidx(3, 2, 6), hwToidx(2, 2, 6))
    graph.AddEdge(hwToidx(3, 2, 6), hwToidx(4, 2, 6))
    graph.AddEdge(hwToidx(4, 2, 6), hwToidx(4, 3, 6))
    graph.AddEdge(hwToidx(4, 2, 6), hwToidx(3, 2, 6))
    graph.AddEdge(hwToidx(4, 2, 6), hwToidx(4, 1, 6))
    graph.AddEdge(hwToidx(4, 2, 6), hwToidx(5, 2, 6))
    graph.AddEdge(hwToidx(5, 2, 6), hwToidx(5, 3, 6))
    graph.AddEdge(hwToidx(5, 2, 6), hwToidx(4, 2, 6))
    graph.AddEdge(hwToidx(1, 3, 6), hwToidx(1, 2, 6))
    graph.AddEdge(hwToidx(2, 3, 6), hwToidx(2, 2, 6))
    graph.AddEdge(hwToidx(2, 3, 6), hwToidx(3, 3, 6))
    graph.AddEdge(hwToidx(3, 3, 6), hwToidx(2, 3, 6))
    graph.AddEdge(hwToidx(3, 3, 6), hwToidx(3, 2, 6))
    graph.AddEdge(hwToidx(4, 3, 6), hwToidx(5, 3, 6))
    graph.AddEdge(hwToidx(4, 3, 6), hwToidx(4, 2, 6))
    graph.AddEdge(hwToidx(5, 3, 6), hwToidx(4, 3, 6))
    graph.AddEdge(hwToidx(5, 3, 6), hwToidx(5, 2, 6))

    print("图:")
    print(graph)

    print("广度优先:")
    bfs = BreadthFirstPaths(graph, 2)
    paths = bfs.PathTo(hwToidx(1, 1, 6))
    for v in reversed(paths):
        print(v, idxTohw(v, 6))

    # print(manhattanDistance([0, 2], [1, 2]))

    print("\na*寻径")
    astar = AStarPaths(graph, 2, 7)
    paths = astar.PathTo(hwToidx(1, 1, 6))
    for v in reversed(paths):
        print(v, idxTohw(v, 6))


if __name__ == "__main__":
    main()
