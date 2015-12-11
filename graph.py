from math import hypot
import heapq

def distance(a, b):
    x1, y1 = a
    x2, y2 = b
    return hypot(x2 - x1, y2 - y1)

def shortest_path(graph, start, end):
    queue = [(0, start, [])]
    seen = set()
    while queue:
        (cost, v, path) = heapq.heappop(queue)
        if v not in seen:
            path = path + [v]
            seen.add(v)
            if v == end:
                return path
            for (neighbor, c) in graph[v].iteritems():
                heapq.heappush(queue, (cost + c, neighbor, path))

def make_graph(points, threshold):
    graph = {}
    for a in points:
        graph[a] = {}
        for b in points:
            d = distance(a, b)
            if d > threshold:
                continue
            graph[a][b] = d
    return graph
