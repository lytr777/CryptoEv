from graph import Graph


def build(cnf):
    graph = Graph(1, cnf.var_count)

    for clause in cnf.clauses:
        if len(clause) < 2:
            continue

        i, j = 0, 1
        while j < len(clause):
            v1 = clause.vars[i].number
            v2 = clause.vars[j].number

            if (v1, v2) not in graph:
                graph.add_edge(v1, v2)

            j += 1
            if j == len(clause):
                i += 1
                j = i + 1

    return graph


def get_next_level(graph, s):
    level = set()
    s = set(s)
    for i in s:
        node = graph.nodes[i - 1]
        index_list = [x.i for x in node.edges]
        level = level.union(set(index_list))

    return level
