from DGR.LinAlg import Vector


def render_polygon(poly, color, window, loop=True):
    for i in range(len(poly)):
        if i + 1 < len(poly):
            a = poly[i].copy().render()
            b = poly[i + 1].copy().render()
        elif loop:
            a = poly[i].copy().render()
            b = poly[0].copy().render()
        else:
            break
        # pygame.draw.line(window, color, a, b)


# confirms that a polygon is both clockwise-defined and convex
def clockwise_convex(polygon):
    x = len(polygon)
    if x > 0:
        for i in range(x - 1):
            l1 = (polygon[(i + 1) % x] - polygon[i % x]).normalize().cross((0, 0, 1))
            l2 = (polygon[(i + 2) % x] - polygon[(i + 1) % x]).normalize()
            if l1.dot(l2) <= 0:
                return False
        return True
    return False


# Clips a subject polygon within the area of the scissors polygon. The scissors polygon must be convex
def suntherland(subject, scissors):
    def inside(p):
        return (v2[0] - v1[0]) * (p[1] - v1[1]) <= (v2[1] - v1[1]) * (p[0] - v1[0])

    def intersection():
        dc = [v1[0] - v2[0], v1[1] - v2[1]]
        dp = [s[0] - vertex[0], s[1] - vertex[1]]
        n1 = v1[0] * v2[1] - v1[1] * v2[0]
        n2 = s[0] * vertex[1] - s[1] * vertex[0]
        n3 = 1.0 / (dc[0] * dp[1] - dc[1] * dp[0])
        return Vector((n1 * dp[0] - n2 * dc[0]) * n3, (n1 * dp[1] - n2 * dc[1]) * n3, 0)

    output = subject
    v1 = scissors[-1]

    for v2 in scissors:
        input_list = output
        output = []
        if len(input_list) > 0:
            s = input_list[-1]

            for vertex in input_list:
                if inside(vertex):
                    if not inside(s):
                        output.append(intersection())
                    output.append(vertex)
                elif inside(s):
                    output.append(intersection())
                s = vertex
            v1 = v2
        else:
            break
    return output
