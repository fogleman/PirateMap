from alpha_shape import alpha_shape
from math import hypot
from PIL import Image
import noise

class Layer(object):
    def translate(self, x, y):
        return Translate(self, x, y)
    def scale(self, x, y):
        return Scale(self, x, y)
    def power(self, power):
        return Power(self, power)
    def add(self, other):
        return Add(self, other)
    def subtract(self, other):
        return Subtract(self, other)
    def multiply(self, other):
        return Multiply(self, other)
    def threshold(self, threshold):
        return Threshold(self, threshold)
    def clamp(self, lo=0, hi=1):
        return Clamp(self, lo, hi)
    def normalize(self, lo, hi, new_lo, new_hi):
        return Normalize(self, lo, hi, new_lo, new_hi)
    def filter_points(self, points, lo, hi):
        return [(x, y) for x, y in points if lo <= self.get(x, y) < hi]
    def alpha_shape(self, points, lo, hi, alpha):
        points = self.filter_points(points, lo, hi)
        return alpha_shape(points, alpha)
    def save(self, path, x1, y1, x2, y2, lo=0, hi=1):
        data = []
        for y in range(y1, y2):
            for x in range(x1, x2):
                v = (self.get(x, y) - lo) / (hi - lo)
                v = int(v * 255)
                v = min(v, 255)
                v = max(v, 0)
                data.append(chr(v))
        im = Image.frombytes('L', (x2 - x1, y2 - y1), ''.join(data))
        im.save(path, 'png')

class Constant(Layer):
    def __init__(self, value):
        self.value = value
    def get(self, x, y):
        return self.value

class Noise(Layer):
    def __init__(self, octaves=1):
        self.octaves = octaves
    def get(self, x, y):
        return noise.snoise2(x, y, self.octaves)

class Translate(Layer):
    def __init__(self, layer, x, y):
        self.layer = layer
        self.x = x
        self.y = y
    def get(self, x, y):
        return self.layer.get(self.x + x, self.y + y)

class Scale(Layer):
    def __init__(self, layer, x, y):
        self.layer = layer
        self.x = x
        self.y = y
    def get(self, x, y):
        return self.layer.get(self.x * x, self.y * y)

class Power(Layer):
    def __init__(self, layer, power):
        self.layer = layer
        self.power = power
    def get(self, x, y):
        return self.layer.get(x, y) ** self.power

class Add(Layer):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def get(self, x, y):
        return self.a.get(x, y) + self.b.get(x, y)

class Subtract(Layer):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def get(self, x, y):
        return self.a.get(x, y) - self.b.get(x, y)

class Multiply(Layer):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def get(self, x, y):
        return self.a.get(x, y) * self.b.get(x, y)

class Threshold(Layer):
    def __init__(self, layer, threshold):
        self.layer = layer
        self.threshold = threshold
    def get(self, x, y):
        return 0 if self.layer.get(x, y) < self.threshold else 1

class Clamp(Layer):
    def __init__(self, layer, lo=0, hi=1):
        self.layer = layer
        self.lo = lo
        self.hi = hi
    def get(self, x, y):
        v = self.layer.get(x, y)
        v = min(v, self.hi)
        v = max(v, self.lo)
        return v

class Normalize(Layer):
    def __init__(self, layer, lo, hi, new_lo, new_hi):
        self.layer = layer
        self.lo = lo
        self.hi = hi
        self.new_lo = new_lo
        self.new_hi = new_hi
    def get(self, x, y):
        v = self.layer.get(x, y)
        p = (v - self.lo) / (self.hi - self.lo)
        v = self.new_lo + p * (self.new_hi - self.new_lo)
        return v

class Distance(Layer):
    def __init__(self, x, y, maximum):
        self.x = x
        self.y = y
        self.maximum = maximum
    def get(self, x, y):
        return hypot(x - self.x, y - self.y) / self.maximum
