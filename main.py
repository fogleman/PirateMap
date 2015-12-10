from alpha_shape import alpha_shape
from poisson_disc import poisson_disc
from shapely.geometry import Polygon, MultiPolygon
import cairo
import math
import noise
import random

def filter_points(points):
    dx = random.random() * 10000
    dy = random.random() * 10000
    result = []
    for x, y in points:
        d = math.hypot(x - 256, y - 256)
        p = d / 256
        m = 0.005
        v = noise.snoise2(dx + x * m, dy + y * m, 8)
        if v - p * 0.5 > 0:
            result.append((x, y))
    return result

def render_shape(dc, shape):
    if isinstance(shape, MultiPolygon):
        for child in shape.geoms:
            render_shape(dc, child)
    if isinstance(shape, Polygon):
        # TODO: interior
        for x, y in shape.exterior.coords:
            dc.line_to(x, y)
        dc.close_path()

def main():
    width = height = 512
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
    dc = cairo.Context(surface)
    dc.set_source_rgb(0, 0, 0)
    dc.paint()
    dc.set_source_rgb(1, 1, 1)
    points = poisson_disc(0, 0, width, height, 8, 32)
    points = filter_points(points)
    shape = alpha_shape(points, 0.1)
    shape = shape.buffer(-4).buffer(4)
    render_shape(dc, shape)
    dc.fill()
    surface.write_to_png('output.png')

if __name__ == '__main__':
    main()
