from DGR.LinAlg import Vector


def circle(x):
    return [Vector(0, 0, x)]


def center_rectangle(x, y):
    x /= 2
    y /= 2
    return [Vector(x, y, 0), Vector(x, -y, 0), Vector(-x, -y, 0), Vector(-x, y, 0)]


def corner_rectangle(x, y):
    return [Vector(0, 0, 0), Vector(x, 0, 0), Vector(x, y, 0), Vector(0, y, 0)]


def ramp(x, y):
    return [Vector(0, 0, 0), Vector(x, 0, 0), Vector(0, y, 0)]


def boat(x, y, z):
    return [Vector(0, z, 0), Vector(x, y, 0), Vector(x, -y, 0), Vector(-x, -y, 0), Vector(-x, y, 0)]


def test():
    return [
        Vector(0, 0),
        Vector(0.292822, 0.0142037) * 100,
        Vector(0.332025, 0.277235) * 100,
        Vector(0.323943, 0.626203) * 100,
        Vector(0.214872, 0.900813) * 100,
        Vector(-0.0460131, 0.868041) * 100,
        Vector(-0.390819, 0.807022) * 100,
        Vector(-0.458564, 0.786636) * 100,
        Vector(-0.526733, 0.24136) * 100,
        Vector(-0.481326, 0.16156) * 100,
        Vector(-0.362815, 0.115521) * 100
    ]
