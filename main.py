from alpha_shape import alpha_shape
from poisson_disc import poisson_disc
from shapely.geometry import Polygon, MultiPolygon
from shapely.affinity import translate
from xkcd import xkcdify
import cairo
import layers
import math
import noise
import random

def hex_color(dc, color):
    color = color[-6:]
    r = int(color[0:2], 16) / 255.0
    g = int(color[2:4], 16) / 255.0
    b = int(color[4:6], 16) / 255.0
    dc.set_source_rgb(r, g, b)

def make_layer():
    x = layers.Noise(8).add(layers.Constant(0.6)).clamp()
    x = x.translate(random.random() * 1000, random.random() * 1000)
    x = x.scale(0.005, 0.005)
    x = x.subtract(layers.Distance(256, 256, 256))
    return x

def render_shape(dc, shape):
    if isinstance(shape, MultiPolygon):
        for child in shape.geoms:
            render_shape(dc, child)
    if isinstance(shape, Polygon):
        dc.new_sub_path()
        for x, y in shape.exterior.coords:
            dc.line_to(x, y)
        dc.close_path()
        # TODO: interior
        # for interior in shape.interiors:
        #     render_shape(dc, interior)

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

def render(seed=None):
    random.seed(seed)
    width = height = 512
    scale = 2
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
        width * scale, height * scale)
    dc = cairo.Context(surface)
    dc.scale(scale, scale)
    dc.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    layer = make_layer()
    # layer.save('layer.png', 0, 0, width, height)
    points = poisson_disc(0, 0, width, height, 8, 16)
    mark = max(points, key=lambda (x, y): layer.get(x, y))
    shape1 = layer.alpha_shape(points, 0.1, 0.1).buffer(-4).buffer(4)
    shape2 = layer.alpha_shape(points, 0.3, 0.1).buffer(-8).buffer(4)
    # shape1 = xkcdify(shape1, 2, 4).buffer(-1).buffer(1)
    # shape2 = xkcdify(shape2, 2, 4).buffer(-1).buffer(1)
    # water background
    hex_color(dc, '2185C5')
    dc.paint()
    # water symbols
    # hex_color(dc, '7ECEFD')
    # for x, y in poisson_disc(0, 0, width, height, 48, 16):
    #     render_water_symbol(dc, x, y)
    # dc.stroke()
    # shallow water
    hex_color(dc, '4FA9E1')
    render_shape(dc, shape1.simplify(8).buffer(48).buffer(-24))
    dc.fill()
    # land outline
    hex_color(dc, 'BDD4DE')
    render_shape(dc, shape1.buffer(2))
    dc.fill()
    # sandy land
    hex_color(dc, 'FFFFA6')
    render_shape(dc, shape1)
    dc.fill()
    # grassy land
    hex_color(dc, 'BDF271')
    render_shape(dc, shape2)
    dc.fill()
    # mark
    hex_color(dc, 'DC3522')
    render_mark_symbol(dc, *mark)
    dc.set_line_cap(cairo.LINE_CAP_ROUND)
    dc.set_line_width(3)
    dc.stroke()
    return surface

if __name__ == '__main__':
    for seed in range(100):
        print seed
        surface = render(seed)
        surface.write_to_png('out%04d.png' % seed)
