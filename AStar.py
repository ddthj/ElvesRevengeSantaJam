from LinAlg import Vector


def find_h(x, finish):
    dist = abs(finish - x)
    return dist.x + dist.y


class Node:
    def __init__(self, loc, g, finish, parent=None):
        self.parent = parent
        self.loc = loc
        self.g = g  # to start
        self.h = find_h(loc, finish)  # to target
        self.f = self.g + self.h


def a_star(start, finish, occupied):

    open_list = [Node(start, 0, finish)]
    closed = []
    current = open_list[0]

    while len(open_list) > 0:
        open_list = sorted(open_list, key=lambda z: z.f)
        current = open_list.pop(0)
        if current.loc == finish:
            break
        closed.append(current)
        # commented nodes are diagonals
        next_nodes = [
            Node(current.loc + Vector(1, 0), current.g + 1, finish, current),
            # Node(current.loc + Vector(1, 1), current.g + 1, finish, current),
            # Node(current.loc + Vector(1, -1), current.g + 1, finish, current),
            Node(current.loc + Vector(-1, 0), current.g + 1, finish, current),
            # Node(current.loc + Vector(-1, 1), current.g + 1, finish, current),
            # Node(current.loc + Vector(-1, -1), current.g + 1, finish, current),
            Node(current.loc + Vector(0, 1), current.g + 1, finish, current),
            Node(current.loc + Vector(0, -1), current.g + 1, finish, current),
        ]
        for node in next_nodes:
            add = True
            for y in occupied:
                if node.loc == y:
                    # todo - may be buggy, but prevents crash when buildings are large
                    node.h += 10
                    node.f = node.g + node.h
                    break
            if add:
                for x in open_list:
                    if node.loc == x.loc:
                        add = False
                        if node.g < x.g:
                            x.parent = node.parent
                            x.g = node.g
                            x.f = x.g + x.h
                        break
            if add:
                open_list.append(node)
    result = []
    while current.parent is not None:
        result.append((current.loc.x, current.loc.y))
        current = current.parent
    result.append((current.loc.x, current.loc.y))
    return result
