from alpha_shape import alpha_shape
from poisson_disc import poisson_disc
from shapely.geometry import Polygon, MultiPolygon
from shapely.affinity import translate
import cairo
import math
import noise
import random

def hex_color(dc, color):
    color = color[-6:]
    r = int(color[0:2], 16) / 255.0
    g = int(color[2:4], 16) / 255.0
    b = int(color[4:6], 16) / 255.0
    dc.set_source_rgb(r, g, b)

def filter_points(points, levels):
    dx = random.random() * 10000
    dy = random.random() * 10000
    result = []
    for _ in levels:
        result.append([])
    for x, y in points:
        d = math.hypot(x - 256, y - 256)
        p = d / 256
        m = 0.005
        v = noise.snoise2(dx + x * m, dy + y * m, 8)
        for i, level in enumerate(levels):
            if v - p > level:
                result[i].append((x, y))
        # if v - p > -0.5:
        #     result.append((x, y))
    return result

def render_shape(dc, shape):
    if isinstance(shape, MultiPolygon):
        for child in shape.geoms:
            render_shape(dc, child)
    if isinstance(shape, Polygon):
        # TODO: interior
        dc.new_sub_path()
        for x, y in shape.exterior.coords:
            dc.line_to(x, y)
        dc.close_path()
        for interior in shape.interiors:
            print interior
            render_shape(dc, interior)

def main():
    width = height = 512
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
    dc = cairo.Context(surface)
    dc.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    hex_color(dc, '2185C5')
    dc.paint()
    points = poisson_disc(0, 0, width, height, 8, 32)
    points1, points2 = filter_points(points, [-0.5, -0.25])
    shape = alpha_shape(points1, 0.1).buffer(-4).buffer(4)
    shape2 = alpha_shape(points2, 0.1).buffer(-6).buffer(6)
    hex_color(dc, '7ECEFD')
    render_shape(dc, shape.simplify(8).buffer(64).buffer(-32))
    dc.fill()
    hex_color(dc, 'BDD4DE')
    render_shape(dc, shape.buffer(4))
    dc.fill()
    hex_color(dc, 'FFFFA6')
    render_shape(dc, shape)
    dc.fill()
    hex_color(dc, 'BDF271')
    render_shape(dc, shape2)
    dc.fill()
    surface.write_to_png('output.png')

if __name__ == '__main__':
    main()
