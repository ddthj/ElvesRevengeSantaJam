import math
from typing import List


class Vector:
    def __init__(self, x, y, z=0.0):
        self.data: List[float] = [x, y, z]

    # Property functions allow you to use `Vector3.x` vs `Vector3[0]`
    @property
    def x(self):
        return self.data[0]

    @x.setter
    def x(self, value):
        self.data[0] = value

    @property
    def y(self):
        return self.data[1]

    @y.setter
    def y(self, value):
        self.data[1] = value

    @property
    def z(self):
        return self.data[2]

    @z.setter
    def z(self, value):
        self.data[2] = value

    def __getitem__(self, key):
        # To access a single value in a Vector3, treat it like a list
        # ie: to get the first (x) value use: Vector3[0]
        # The same works for setting values
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __str__(self):
        # Vector3's can be printed to console
        return str(self.data)

    __repr__ = __str__

    def __eq__(self, value):
        # Vector3's can be compared with:
        # - Another Vector3, in which case True will be returned if they have the same values
        # - A list, in which case True will be returned if they have the same values
        # - A single value, in which case True will be returned if the Vector's length matches the value
        if isinstance(value, Vector):
            return self.data == value.data
        elif isinstance(value, list):
            return self.data == value
        else:
            return self.magnitude() == value

    # Vector3's support most operators (+-*/)
    # If using an operator with another Vector3, each dimension will be independent
    # ie x+x, y+y, z+z
    # If using an operator with only a value, each dimension will be affected by that value
    # ie x+v, y+v, z+v
    def __add__(self, value):
        if hasattr(value, "__getitem__"):
            return Vector(self[0] + value[0], self[1] + value[1], self[2] + value[2])
        return Vector(self[0] + value, self[1] + value, self[2] + value)

    __radd__ = __add__

    def __sub__(self, value):
        if hasattr(value, "__getitem__"):
            return Vector(self[0] - value[0], self[1] - value[1], self[2] - value[2])
        return Vector(self[0] - value, self[1] - value, self[2] - value)

    __rsub__ = __sub__

    def __neg__(self):
        return Vector(-self[0], -self[1], -self[2])

    def __mul__(self, value):
        if hasattr(value, "__getitem__"):
            return Vector(self[0] * value[0], self[1] * value[1], self[2] * value[2])
        return Vector(self[0] * value, self[1] * value, self[2] * value)

    __rmul__ = __mul__

    def __truediv__(self, value):
        if hasattr(value, "__getitem__"):
            return Vector(self[0] / value[0], self[1] / value[1], self[2] / value[2])
        return Vector(self[0] / value, self[1] / value, self[2] / value)

    def __rtruediv__(self, value):
        if hasattr(value, "__getitem__"):
            return Vector(value[0] / self[0], value[1] / self[1], value[2] / self[2])
        raise TypeError("unsupported rtruediv operands")

    def __mod__(self, value):
        if hasattr(value, "__getitem__"):
            return Vector(self[0] % value[0], self[1] % value[1], self[2] % value[2])
        return Vector(self[0] % value, self[1] % value, self[2] % value)

    def __floordiv__(self, value):
        if hasattr(value, "__getitem__"):
            return Vector(int(self[0] // value[0]), int(self[1] // value[1]), int(self[2] // value[2]))
        return Vector(int(self[0] // value), int(self[1] // value), int(self[2] // value))

    def __abs__(self):
        return Vector(abs(self[0]), abs(self[1]), abs(self[2]))

    def magnitude(self):
        # Magnitude() returns the length of the vector
        return math.sqrt((self[0] * self[0]) + (self[1] * self[1]) + (self[2] * self[2]))

    def normalize(self, return_magnitude=False):
        # Normalize() returns a Vector3 that shares the same direction but has a length of 1.0
        # Normalize(True) can also be used if you'd also like the length of this Vector3 returned
        magnitude = self.magnitude()
        if magnitude != 0:
            if return_magnitude:
                return Vector(self[0] / magnitude, self[1] / magnitude, self[2] / magnitude), magnitude
            return Vector(self[0] / magnitude, self[1] / magnitude, self[2] / magnitude)
        if return_magnitude:
            return Vector(0, 0, 0), 0
        return Vector(0, 0, 0)

    # Linear algebra functions
    def dot(self, value):
        return self[0] * value[0] + self[1] * value[1] + self[2] * value[2]

    def cross(self, value):
        return Vector((self[1] * value[2]) - (self[2] * value[1]),
                      (self[2] * value[0]) - (self[0] * value[2]),
                      (self[0] * value[1]) - (self[1] * value[0]))

    def flatten(self, axis=None):
        # Sets Z (Vector3[2]) to 0, or flattens point to some plane orthogonal to the provided axis
        if axis is None:
            return Vector(self[0], self[1], 0)
        else:
            return self - (axis * self.dot(axis))

    def render(self):
        # Returns a list with the x and y values, to be used with pygame
        return [int(self[0]), -int(self[1])]

    def copy(self):
        # Returns a copy of this Vector3
        return Vector(*self.data[:])

    def angle(self, value):
        # Returns the angle between this Vector3 and another Vector3
        return math.acos(round(self.flatten().normalize().dot(value.flatten().normalize()), 4))

    def rotate(self, angle):
        # Rotates this Vector3 by the given angle in radians
        # Note that this is only 2D, in the x and y axis
        return Vector((math.cos(angle) * self[0]) - (math.sin(angle) * self[1]),
                      (math.sin(angle) * self[0]) + (math.cos(angle) * self[1]), self[2])

    def clamp(self, start, end):
        # Similar to integer clamping, Vector3's clamp() forces the Vector3's direction between a start and end Vector3
        # Such that Start < Vector3 < End in terms of clockwise rotation
        # Note that this is only 2D, in the x and y axis
        s = self.normalize()
        right = s.dot(end.cross((0, 0, -1))) < 0
        left = s.dot(start.cross((0, 0, -1))) > 0
        if (right and left) if end.dot(start.cross((0, 0, -1))) > 0 else (right or left):
            return self
        if start.dot(s) < end.dot(s):
            return end
        return start


class Matrix3:
    def __init__(self, *args):
        if len(args) == 1:
            self.data = ()
            self.convert_euler(0, args[0], 0)
        elif len(args) > 0:
            self.data = (args[0], args[1], args[2])
        else:
            self.data = (Vector(0, 0, 0), Vector(0, 0, 0), Vector(0, 0, 0))
        self.forward, self.left, self.up = self.data

    def convert_euler(self, pitch, yaw, roll):
        cp = math.cos(pitch)
        sp = math.sin(pitch)
        cy = math.cos(yaw)
        sy = math.sin(yaw)
        cr = math.cos(roll)
        sr = math.sin(roll)
        self.data = (
            Vector(cp * cy, cp * sy, sp),
            Vector(cy * sp * sr - cr * sy, sy * sp * sr + cr * cy, -cp * sr),
            Vector(-cr * cy * sp - sr * sy, -cr * sy * sp + sr * cy, cp * cr))
        self.forward, self.left, self.up = self.data

    def dot(self, vector):
        return Vector(self.forward.dot(vector),
                      self.left.dot(vector),
                      self.up.dot(vector))

    def transpose(self):
        return Matrix3(
            Vector(self[0][0], self[1][0], self[2][0]),
            Vector(self[0][1], self[1][1], self[2][1]),
            Vector(self[0][2], self[1][2], self[2][2]))

    def axis_angle(self):
        theta = math.acos((self[0][0] + self[1][1] + self[2][2] - 1.0) / 2)
        x = (self[2][1] - self[1][2]) / (2 * math.sin(theta))
        y = (self[0][2] - self[2][0]) / (2 * math.sin(theta))
        z = (self[1][0] - self[0][1]) / (2 * math.sin(theta))
        return Vector(x, y, z)

    def __getitem__(self, value):
        return self.data[value]

    def __mul__(self, mat):
        return Matrix3(
            Vector(self[0][0] * mat[0][0] + self[1][0] * mat[0][1] + self[2][0] * mat[0][2],
                   self[0][1] * mat[0][0] + self[1][1] * mat[0][1] + self[2][1] * mat[0][2],
                   self[0][2] * mat[0][0] + self[1][2] * mat[0][1] + self[2][2] * mat[0][2]),
            Vector(self[0][0] * mat[1][0] + self[1][0] * mat[1][1] + self[2][0] * mat[1][2],
                   self[0][1] * mat[1][0] + self[1][1] * mat[1][1] + self[2][1] * mat[1][2],
                   self[0][2] * mat[1][0] + self[1][2] * mat[1][1] + self[2][2] * mat[1][2]),
            Vector(self[0][0] * mat[2][0] + self[1][0] * mat[2][1] + self[2][0] * mat[2][2],
                   self[0][1] * mat[2][0] + self[1][1] * mat[2][1] + self[2][1] * mat[2][2],
                   self[0][2] * mat[2][0] + self[1][2] * mat[2][1] + self[2][2] * mat[2][2]),
        )


def cross(x: Vector):
    return Vector(-x.y, x.x)


def det(a, b):
    return a.x * b.y - a.y * b.x

