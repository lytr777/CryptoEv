import warnings


class Edge:
    def __init__(self, s, t):
        if not isinstance(s, Node) or not isinstance(t, Node):
            raise Exception("supported only with Node's")

        self.s = s
        self.t = t

    def reverse(self):
        self.s, self.t = self.t, self.s
        return self

    def __cmp__(self, other):
        if not isinstance(other, Edge):
            raise Exception("supported only compare between Edge's")

        sd = self.s.i - other.s.i
        return self.t.i - other.t.i if sd == 0 else sd

    def __hash__(self):
        return hash((self.s, self.t))

    def __str__(self):
        return "%s -> %s" % (self.s, self.t)


class Node:
    def __init__(self, i):
        self.i = i
        self.edges = []

    def connect(self, node):
        if not isinstance(node, Node):
            raise Exception("supported only with Node's")

        if self == node:
            raise Exception("loop on node %d" % self.i)

        if node in self.edges:
            warnings.warn("node %d already connected to %s" % (self.i, node), UserWarning)
        else:
            self.edges.append(node)

        return Edge(self, node)

    def connected(self, node):
        return node in self.edges

    def by_edge(self, edge):
        if edge.s != self:
            raise Exception("Invalid start point")

        return self.connect(edge.t)

    def __hash__(self):
        return self.i

    def __cmp__(self, other):
        if not isinstance(other, Node):
            raise Exception("supported only compare between Node's")

        return self.i - other.i

    def __str__(self):
        return str(self.i)


class Graph:
    def __init__(self, root, size=1000):
        if isinstance(root, int):
            self.root = Node(root)
        else:
            raise Exception("Invalid root")

        self.nodes = [None] * size
        self.__expand(root)
        self.nodes[root - 1] = self.root
        self.node_count = 1

    def add_edge(self, s, t, directed=False):
        s_node = self.__get_node(s)
        t_node = self.__get_node(t)

        s_node.connect(t_node)
        if not directed:
            t_node.connect(s_node)

    def __get_node(self, i):
        if len(self.nodes) < i:
            self.__expand(i)

        if self.nodes[i - 1] is None:
            self.nodes[i - 1] = Node(i)
            self.node_count += 1

        return self.nodes[i - 1]

    def __expand(self, i):
        new_size = len(self.nodes)
        while new_size < i:
            new_size *= 2

        new_nodes = [None] * new_size
        for j in range(len(self.nodes)):
            new_nodes[j] = self.nodes[j]

        self.nodes = new_nodes

    def __contains__(self, item):
        s_node = self.__get_node(item[0])
        t_node = self.__get_node(item[1])

        if s_node is None or t_node is None:
            return False

        return s_node.connected(t_node)
