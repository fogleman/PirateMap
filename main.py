from alpha_shape import alpha_shape
from colour import Color
from poisson_disc import poisson_disc
from shapely.geometry import Polygon, MultiPolygon, Point
from xkcd import xkcdify
import cairo
import graph
import layers
import math
import noise
import random

def make_layer():
    x = layers.Noise(8).add(layers.Constant(0.6)).clamp()
    x = x.translate(random.random() * 1000, random.random() * 1000)
    x = x.scale(0.005, 0.005)
    x = x.subtract(layers.Distance(256, 256, 256))
    return x

def render_shape(dc, shape):
    if shape.is_empty:
        return
    if isinstance(shape, MultiPolygon):
        for child in shape.geoms:
            render_shape(dc, child)
    if isinstance(shape, Polygon):
        dc.new_sub_path()
        for x, y in shape.exterior.coords:
            dc.line_to(x, y)
        dc.close_path()

def render_water_symbol(dc, x, y):
    r = 4
    e = math.pi / 4
    for dx in [-r, r]:
        dc.new_sub_path()
        dc.arc_negative(dx + x + r, y, r, math.pi, math.pi / 2 - e)
        dc.new_sub_path()
        dc.arc(dx + x - r, y, r, 0, math.pi / 2 + e)

def render_mark_symbol(dc, x, y):
    n = 8
    dc.move_to(x - n, y - n)
    dc.line_to(x + n, y + n)
    dc.move_to(x - n, y + n)
    dc.line_to(x + n, y - n)

def render_compass_symbol(dc):
    w, h = 4, 32
    dc.line_to(-w, 0)
    dc.line_to(0, h)
    dc.line_to(w, 0)
    dc.line_to(0, -h)
    dc.close_path()
    dc.set_source_rgb(*Color('#FFFFFF').rgb)
    dc.set_line_width(4)
    dc.stroke_preserve()
    dc.fill()
    dc.line_to(-w, 0)
    dc.line_to(w, 0)
    dc.line_to(0, -h)
    dc.close_path()
    dc.set_source_rgb(*Color('#DC3522').rgb)
    dc.fill()
    dc.save()
    dc.translate(0, -h * 3 / 2 - 8)
    w, h = 5, 15
    dc.line_to(-w, h)
    dc.line_to(-w, 0)
    dc.line_to(w, h)
    dc.line_to(w, 0)
    dc.set_source_rgb(*Color('#FFFFFF').rgb)
    dc.stroke()
    dc.restore()

def render_curve(dc, points, alpha):
    items = zip(points, points[1:], points[2:], points[3:])
    # dc.line_to(*points[0])
    # dc.line_to(*points[1])
    for (x1, y1), (x2, y2), (x3, y3), (x4, y4) in items:
        a1 = math.atan2(y2 - y1, x2 - x1)
        a2 = math.atan2(y4 - y3, x4 - x3)
        cx = x2 + math.cos(a1) * alpha
        cy = y2 + math.sin(a1) * alpha
        dx = x3 - math.cos(a2) * alpha
        dy = y3 - math.sin(a2) * alpha
        dc.curve_to(cx, cy, dx, dy, x3, y3)
    # dc.line_to(*points[-1])

def find_path(layer, points, threshold):
    x = layers.Noise(4).add(layers.Constant(0.6)).clamp()
    x = x.translate(random.random() * 1000, random.random() * 1000)
    x = x.scale(0.01, 0.01)
    g = graph.make_graph(points, threshold, x)
    end = max(points, key=lambda (x, y): layer.get(x, y))
    points.sort(key=lambda (x, y): math.hypot(x - end[0], y - end[1]))
    for start in reversed(points):
        path = graph.shortest_path(g, end, start)
        if path:
            return path

def render(seed=None):
    random.seed(seed)
    width = height = 512
    scale = 2
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
        width * scale, height * scale)
    dc = cairo.Context(surface)
    dc.set_line_cap(cairo.LINE_CAP_ROUND)
    dc.set_line_join(cairo.LINE_JOIN_ROUND)
    dc.scale(scale, scale)
    layer = make_layer()
    # layer.save('layer.png', 0, 0, width, height)
    points = poisson_disc(0, 0, width, height, 8, 16)
    shape1 = layer.alpha_shape(points, 0.1, 1, 0.1).buffer(-4).buffer(4)
    shape2 = layer.alpha_shape(points, 0.3, 1, 0.1).buffer(-8).buffer(4)
    shape3 = layer.alpha_shape(points, 0.1, 0.3, 0.1).buffer(-12).buffer(4)
    points = [x for x in points if shape1.contains(Point(*x))]
    path = find_path(layer, points, 16)
    mark = path[0]
    # water background
    dc.set_source_rgb(*Color('#2185C5').rgb)
    dc.paint()
    # shallow water
    n = 5
    shape = shape1.simplify(8).buffer(32).buffer(-16)
    shapes = [shape]
    for _ in range(n):
        shape = shape.simplify(8).buffer(64).buffer(-32)
        shape = xkcdify(shape, 2, 8)
        shapes.append(shape)
    shapes.reverse()
    c1 = Color('#4FA9E1')
    c2 = Color('#2185C5')
    for c, shape in zip(c2.range_to(c1, n), shapes):
        dc.set_source_rgb(*c.rgb)
        render_shape(dc, shape)
        dc.fill()
    # land outline
    dc.set_source_rgb(*Color('#BDD4DE').rgb)
    render_shape(dc, shape1.buffer(2))
    dc.fill()
    # sandy land
    dc.set_source_rgb(*Color('#FFFFA6').rgb)
    render_shape(dc, shape1)
    dc.fill()
    # grassy land
    dc.set_source_rgb(*Color('#BDF271').rgb)
    render_shape(dc, shape2)
    dc.fill()
    # dark sand
    dc.set_source_rgb(*Color('#CFC291').rgb)
    render_shape(dc, shape3)
    dc.fill()
    # path
    dc.set_source_rgb(*Color('#DC3522').rgb)
    render_curve(dc, path, 4)
    dc.set_dash([4])
    dc.stroke()
    dc.set_dash([])
    # mark
    dc.set_source_rgb(*Color('#DC3522').rgb)
    render_mark_symbol(dc, *mark)
    dc.set_line_width(4)
    dc.stroke()
    # compass
    dc.save()
    dc.translate(48, height - 64)
    dc.rotate(random.random() * math.pi / 4 - math.pi / 8)
    render_compass_symbol(dc)
    dc.restore()
    return surface

if __name__ == '__main__':
    for seed in range(100):
        print seed
        surface = render(seed)
        surface.write_to_png('out%04d.png' % seed)
