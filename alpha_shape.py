from math import hypot, sqrt
from pyhull.delaunay import DelaunayTri
from shapely.geometry import MultiLineString
from shapely.ops import cascaded_union, polygonize

def alpha_shape(points, alpha):
    def add_edge(points, i, j):
        if (i, j) in edges or (j, i) in edges:
            return
        edges.add((i, j))
        edge_points.append((points[i], points[j]))
    tri = DelaunayTri(points)
    edges = set()
    edge_points = []
    for i1, i2, i3 in tri.vertices:
        x1, y1 = tri.points[i1]
        x2, y2 = tri.points[i2]
        x3, y3 = tri.points[i3]
        a = hypot(x1 - x2, y1 - y2)
        b = hypot(x2 - x3, y2 - y3)
        c = hypot(x3 - x1, y3 - y1)
        s = (a + b + c) / 2.0
        area = sqrt(s * (s - a) * (s - b) * (s - c))
        radius = a * b * c / (4 * area)
        if radius < 1.0 / alpha:
            add_edge(tri.points, i1, i2)
            add_edge(tri.points, i2, i3)
            add_edge(tri.points, i3, i1)
    shape = cascaded_union(list(polygonize(MultiLineString(edge_points))))
    return shape
