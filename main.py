from alpha_shape import alpha_shape
from poisson_disc import poisson_disc
from shapely.geometry import Polygon, MultiPolygon
from shapely.affinity import translate
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

def main():
    width = height = 512
    scale = 2
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width * scale, height * scale)
    dc = cairo.Context(surface)
    dc.scale(scale, scale)
    dc.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    hex_color(dc, '2185C5')
    dc.paint()
    layer = make_layer()
    layer.save('layer.png', 0, 0, width, height)
    points = poisson_disc(0, 0, width, height, 8, 32)
    shape1 = layer.alpha_shape(points, 0.1, 0.1).buffer(-4).buffer(4)
    shape2 = layer.alpha_shape(points, 0.2, 0.1).buffer(-8).buffer(4)
    hex_color(dc, '7ECEFD')
    render_shape(dc, shape1.simplify(8).buffer(64).buffer(-32))
    dc.fill()
    hex_color(dc, 'BDD4DE')
    render_shape(dc, shape1.buffer(4))
    dc.fill()
    hex_color(dc, 'FFFFA6')
    render_shape(dc, shape1)
    dc.fill()
    hex_color(dc, 'BDF271')
    render_shape(dc, shape2)
    dc.fill()
    surface.write_to_png('output.png')

if __name__ == '__main__':
    main()
