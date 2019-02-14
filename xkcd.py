from shapely.geometry import LineString, Polygon, MultiPolygon
import math
import random

def low_pass(values, alpha):
    result = []
    y = 0.0
    for x in values:
        y = y - (alpha * (y - x))
        result.append(y)
    return result

def normalize(values, new_lo, new_hi):
    result = []
    lo = min(values)
    hi = max(values)
    for x in values:
        p = (x - lo) / (hi - lo)
        x = new_lo + p * (new_hi - new_lo)
        result.append(x)
    return result

def evenly_spaced(points, spacing):
    result = []
    line = LineString(points)
    length = line.length
    d = 0
    while d < length:
        point = line.interpolate(d)
        result.append((point.x, point.y))
        d += spacing
    return result

def perturbed(points, spacing, intensity):
    result = []
    points = evenly_spaced(points, spacing)
    noises = [random.random() * 2 - 1 for _ in range(len(points) // 2)]
    for _ in range(3):
        noises = low_pass(noises, 0.3)
    noises = normalize(noises, -1, 1)
    noises = noises + list(reversed(noises))
    for (x1, y1), (x2, y2), noise in zip(points, points[1:], noises):
        a = math.atan2(y2 - y1, x2 - x1) + math.pi / 2
        x = x1 + math.cos(a) * intensity * noise
        y = y1 + math.sin(a) * intensity * noise
        result.append((x, y))
    return result

def xkcdify(shape, spacing, intensity):
    if isinstance(shape, MultiPolygon):
        return MultiPolygon([xkcdify(child, spacing, intensity)
            for child in shape.geoms])
    elif isinstance(shape, Polygon):
        return Polygon(perturbed(shape.exterior.coords, spacing, intensity))
    elif isinstance(shape, LineString):
        return LineString(perturbed(shape.coords, spacing, intensity))
    else:
        raise Exception('unsupported shape')
